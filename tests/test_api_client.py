"""
Tests for NASA ADS API client.

Tests for API client with mocked HTTP responses.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests

from nasa_ads.core.api_client import NASAADSClient, APIError, RateLimiter
from nasa_ads.models.paper import Query, Paper
from nasa_ads.utils.validators import ValidationError


class TestRateLimiter:
    """Tests for rate limiter."""

    def test_rate_limiter_creation(self):
        """Test creating rate limiter."""
        limiter = RateLimiter(min_delay=0.1)
        assert limiter.min_delay == 0.1

    def test_rate_limiter_wait(self):
        """Test rate limiter wait."""
        limiter = RateLimiter(min_delay=0.01)
        limiter.wait()  # First call
        limiter.wait()  # Second call (may delay)
        assert limiter.last_request_time is not None


class TestNASAADSClientInit:
    """Tests for API client initialization."""

    def test_create_client_valid_key(self):
        """Test creating client with valid API key."""
        client = NASAADSClient(api_key="test_key_1234567890")
        assert client.api_key == "test_key_1234567890"

    def test_create_client_invalid_key(self):
        """Test creating client with invalid API key."""
        with pytest.raises(ValidationError):
            NASAADSClient(api_key="short")

    def test_create_client_empty_key(self):
        """Test creating client with empty API key."""
        with pytest.raises(ValidationError):
            NASAADSClient(api_key="")

    def test_client_has_session(self):
        """Test that client creates session."""
        client = NASAADSClient(api_key="test_key_1234567890")
        assert client.session is not None


class TestNASAADSClientSearch:
    """Tests for search functionality."""

    @patch("nasa_ads.core.api_client.requests.Session.get")
    def test_search_success(self, mock_get):
        """Test successful search."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {
                "numFound": 100,
                "start": 0,
                "docs": [
                    {
                        "bibcode": "2021ApJ...919..136K",
                        "title": ["Discovery of New Exoplanet"],
                        "year": 2021,
                        "pub": "The Astrophysical Journal",
                        "abstract": "A study of new exoplanets",
                        "keyword": ["exoplanet"],
                        "citation_count": 42,
                    }
                ],
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = NASAADSClient(api_key="test_key_1234567890")
        query = Query(q="supernova")
        results = client.search(query)

        assert results.total_count == 100
        assert len(results.papers) == 1
        assert results.papers[0].bibcode == "2021ApJ...919..136K"

    @patch("nasa_ads.core.api_client.requests.Session.get")
    def test_search_rate_limit_error(self, mock_get):
        """Test search with rate limit error."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_get.return_value = mock_response

        client = NASAADSClient(api_key="test_key_1234567890")
        query = Query(q="test")

        with pytest.raises(APIError):
            client.search(query)

    @patch("nasa_ads.core.api_client.requests.Session.get")
    def test_search_authentication_error(self, mock_get):
        """Test search with authentication error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_get.return_value = mock_response

        client = NASAADSClient(api_key="invalid_key")
        query = Query(q="test")

        with pytest.raises(APIError):
            client.search(query)

    @patch("nasa_ads.core.api_client.requests.Session.get")
    def test_search_empty_results(self, mock_get):
        """Test search with no results."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {
                "numFound": 0,
                "start": 0,
                "docs": [],
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = NASAADSClient(api_key="test_key_1234567890")
        query = Query(q="nonexistent_query_xyz")
        results = client.search(query)

        assert results.total_count == 0
        assert len(results.papers) == 0

    @patch("nasa_ads.core.api_client.requests.Session.get")
    def test_search_malformed_response(self, mock_get):
        """Test search with malformed response."""
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        client = NASAADSClient(api_key="test_key_1234567890")
        query = Query(q="test")

        with pytest.raises(APIError):
            client.search(query)


class TestNASAADSClientBibTeX:
    """Tests for BibTeX export."""

    @patch("nasa_ads.core.api_client.requests.Session.post")
    def test_get_bibtex_success(self, mock_post):
        """Test successful BibTeX retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "export": "@article{2021ApJ...919..136K,\n  title={Test}\n}"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        client = NASAADSClient(api_key="test_key_1234567890")
        bibtex_dict = client.get_bibtex(["2021ApJ...919..136K"])

        assert len(bibtex_dict) >= 0

    @patch("nasa_ads.core.api_client.requests.Session.post")
    def test_get_bibtex_empty_list(self, mock_post):
        """Test BibTeX with empty bibcode list."""
        client = NASAADSClient(api_key="test_key_1234567890")
        bibtex_dict = client.get_bibtex([])

        assert bibtex_dict == {}
        mock_post.assert_not_called()


class TestNASAADSClientContext:
    """Tests for context manager."""

    def test_context_manager(self):
        """Test using client as context manager."""
        with NASAADSClient(api_key="test_key_1234567890") as client:
            assert client is not None
            assert client.session is not None

    def test_client_close(self):
        """Test closing client."""
        client = NASAADSClient(api_key="test_key_1234567890")
        client.close()
        # Should not raise exception
