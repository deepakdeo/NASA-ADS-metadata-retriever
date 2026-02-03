"""
NASA ADS API client with retry logic and rate limiting.

This module provides a high-level client for interacting with the
NASA ADS Search API with automatic retries and rate limiting.
"""

import time
import requests
from typing import Dict, List, Optional, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime, timedelta

from ..models.paper import Paper, Query, Results
from ..utils.logger import get_logger
from ..utils.validators import (
    validate_api_key,
    validate_query,
    ValidationError,
)
from ..constants import (
    API_SEARCH_ENDPOINT,
    API_EXPORT_ENDPOINT,
    REQUEST_TIMEOUT_SECONDS,
    MAX_RETRIES,
    RETRY_BACKOFF_FACTOR,
    RATE_LIMIT_DELAY_SECONDS,
    DEFAULT_FIELDS,
)

logger = get_logger(__name__)


class APIError(Exception):
    """Custom exception for API errors."""

    pass


class RateLimiter:
    """Simple rate limiter to throttle API requests."""

    def __init__(self, min_delay: float = RATE_LIMIT_DELAY_SECONDS):
        """
        Initialize rate limiter.

        Args:
            min_delay: Minimum delay between requests (seconds)
        """
        self.min_delay = min_delay
        self.last_request_time: Optional[datetime] = None

    def wait(self) -> None:
        """Wait if necessary to maintain minimum delay between requests."""
        if self.last_request_time is None:
            self.last_request_time = datetime.now()
            return

        elapsed = (datetime.now() - self.last_request_time).total_seconds()
        if elapsed < self.min_delay:
            sleep_time = self.min_delay - elapsed
            logger.debug(f"Rate limiting: sleeping {sleep_time:.3f}s")
            time.sleep(sleep_time)

        self.last_request_time = datetime.now()


class NASAADSClient:
    """
    Client for NASA ADS Search API.

    Handles authentication, rate limiting, retries, and error handling
    for interaction with NASA ADS REST API.
    """

    def __init__(
        self,
        api_key: str,
        timeout: int = REQUEST_TIMEOUT_SECONDS,
        max_retries: int = MAX_RETRIES,
        backoff_factor: float = RETRY_BACKOFF_FACTOR,
    ):
        """
        Initialize NASA ADS API client.

        Args:
            api_key: NASA ADS API key
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries on failure
            backoff_factor: Backoff factor for exponential retry delays

        Raises:
            ValidationError: If API key is invalid
        """
        validate_api_key(api_key)
        self.api_key = api_key
        self.timeout = timeout
        self.rate_limiter = RateLimiter()

        # Set up session with retry strategy
        self.session = self._create_session(max_retries, backoff_factor)

        logger.info("NASA ADS API client initialized")

    def _create_session(self, max_retries: int, backoff_factor: float) -> requests.Session:
        """
        Create requests session with retry strategy.

        Args:
            max_retries: Number of retries
            backoff_factor: Backoff factor for retries

        Returns:
            Configured requests.Session
        """
        session = requests.Session()

        # Retry strategy
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
            backoff_factor=backoff_factor,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with API key."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def search(
        self,
        query: Query,
    ) -> Results:
        """
        Search NASA ADS database.

        Args:
            query: Query object with search parameters

        Returns:
            Results object containing papers and metadata

        Raises:
            APIError: If API request fails
            ValidationError: If query is invalid
        """
        validate_query(query.q)

        # Rate limit
        self.rate_limiter.wait()

        try:
            logger.info(f"Searching ADS: {query.q[:50]}...")
            params = query.to_params()

            response = self.session.get(
                API_SEARCH_ENDPOINT,
                headers=self._get_headers(),
                params=params,
                timeout=self.timeout,
            )

            response.raise_for_status()
            data = response.json()

            # Parse results
            results = self._parse_search_response(data, query)
            logger.info(
                f"Retrieved {len(results.papers)} papers "
                f"({results.start}/{results.total_count} total)"
            )

            return results

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.error("Rate limit exceeded")
                raise APIError("Rate limit exceeded. Please try again later.") from e
            elif e.response.status_code == 401:
                logger.error("Authentication failed")
                raise APIError("Invalid API key") from e
            else:
                logger.error(f"HTTP error: {e}")
                raise APIError(f"API request failed: {e}") from e

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise APIError(f"Failed to connect to API: {e}") from e

        except ValueError as e:
            logger.error(f"JSON parsing error: {e}")
            raise APIError(f"Failed to parse API response: {e}") from e

    def _parse_search_response(self, data: Dict[str, Any], query: Query) -> Results:
        """
        Parse API response into Results object.

        Args:
            data: JSON response from API
            query: Original query

        Returns:
            Results object with parsed papers
        """
        results = Results()

        response_section = data.get("response", {})
        results.total_count = response_section.get("numFound", 0)
        results.start = response_section.get("start", 0)
        results.returned_count = len(response_section.get("docs", []))

        for doc in response_section.get("docs", []):
            try:
                paper = Paper(
                    bibcode=doc.get("bibcode", ""),
                    title=doc.get("title", [""])[0] if doc.get("title") else "",
                    year=doc.get("year", 0),
                    pub=doc.get("pub", ""),
                    abstract=doc.get("abstract", ""),
                    keyword=doc.get("keyword", []) or [],
                    citation_count=doc.get("citation_count", 0),
                )
                results.add_paper(paper)
            except (ValueError, KeyError) as e:
                logger.warning(f"Failed to parse paper: {e}")
                continue

        return results

    def get_bibtex(self, bibcodes: List[str]) -> Dict[str, str]:
        """
        Get BibTeX entries for papers.

        Args:
            bibcodes: List of ADS bibcodes

        Returns:
            Dictionary mapping bibcode to BibTeX entry

        Raises:
            APIError: If request fails
        """
        if not bibcodes:
            return {}

        # Rate limit
        self.rate_limiter.wait()

        try:
            logger.debug(f"Fetching BibTeX for {len(bibcodes)} papers")

            response = self.session.post(
                API_EXPORT_ENDPOINT,
                headers=self._get_headers(),
                json={"bibcodes": bibcodes, "format": "bibtex"},
                timeout=self.timeout,
            )

            response.raise_for_status()
            data = response.json()

            return self._parse_bibtex_response(data, bibcodes)

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch BibTeX: {e}")
            raise APIError(f"Failed to fetch BibTeX: {e}") from e

    def _parse_bibtex_response(
        self, data: Dict[str, Any], bibcodes: List[str]
    ) -> Dict[str, str]:
        """
        Parse BibTeX response.

        Args:
            data: API response
            bibcodes: Original bibcodes list

        Returns:
            Dictionary of bibcode -> BibTeX entry
        """
        bibtex_dict = {}
        export_text = data.get("export", "")

        if not export_text:
            return bibtex_dict

        # Simple parsing: split by @article, @inproceedings, etc.
        entries = export_text.split("@")
        for entry in entries:
            if not entry.strip():
                continue

            # Try to extract bibcode from entry
            for bibcode in bibcodes:
                if bibcode in entry:
                    bibtex_dict[bibcode] = "@" + entry
                    break

        return bibtex_dict

    def close(self) -> None:
        """Close API session."""
        if self.session:
            self.session.close()
            logger.debug("API session closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
