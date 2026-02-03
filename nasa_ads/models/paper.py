"""
Data models for NASA ADS metadata retriever.

This module defines the core data structures using Python dataclasses:
- Paper: Represents a single paper from NASA ADS API
- Query: Encapsulates search query parameters
- Results: Container for API results with pagination info
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class Paper:
    """
    Represents a single astronomical paper from NASA ADS.

    Attributes:
        bibcode: Unique identifier in ADS (e.g., '2021ApJ...919..136K')
        title: Paper title
        year: Publication year
        pub: Publication venue (journal/conference name)
        abstract: Paper abstract text
        keyword: List of associated keywords
        citation_count: Number of citations received
        bibtex: BibTeX citation string (optional, fetched separately)
        url: Direct link to paper on ADS website
    """

    bibcode: str
    title: str
    year: int
    pub: str
    abstract: str
    keyword: List[str] = field(default_factory=list)
    citation_count: int = 0
    bibtex: Optional[str] = None
    url: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate paper data after initialization."""
        if not self.bibcode or not isinstance(self.bibcode, str):
            raise ValueError("bibcode must be a non-empty string")
        if not self.title or not isinstance(self.title, str):
            raise ValueError("title must be a non-empty string")
        if not isinstance(self.year, int) or self.year < 1800 or self.year > 2100:
            raise ValueError(f"year must be integer between 1800 and 2100, got {self.year}")
        if self.citation_count < 0:
            raise ValueError(f"citation_count must be non-negative, got {self.citation_count}")

    @property
    def ads_url(self) -> str:
        """Generate direct URL to paper on ADS website."""
        return f"https://ui.adsabs.harvard.edu/abs/{self.bibcode}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert paper to dictionary."""
        return {
            "bibcode": self.bibcode,
            "title": self.title,
            "year": self.year,
            "pub": self.pub,
            "abstract": self.abstract,
            "keyword": self.keyword,
            "citation_count": self.citation_count,
            "bibtex": self.bibtex,
            "url": self.ads_url,
        }


@dataclass
class Query:
    """
    Encapsulates NASA ADS search query parameters.

    Attributes:
        q: Query string (ADS QL format)
        rows: Number of results per request (default: 100, max: 2000)
        start: Starting position for pagination
        fl: Fields to return (comma-separated)
        sort: Sort field and direction (e.g., 'citation_count desc')
    """

    q: str
    rows: int = 100
    start: int = 0
    fl: str = "bibcode,title,year,pub,abstract,keyword,citation_count"
    sort: str = "citation_count desc"

    def __post_init__(self) -> None:
        """Validate query parameters."""
        if not self.q or not isinstance(self.q, str):
            raise ValueError("Query string (q) must be non-empty")
        if not 1 <= self.rows <= 2000:
            raise ValueError(f"rows must be between 1 and 2000, got {self.rows}")
        if self.start < 0:
            raise ValueError(f"start must be non-negative, got {self.start}")

    def to_params(self) -> Dict[str, Any]:
        """Convert to parameters dict for API request."""
        return {
            "q": self.q,
            "rows": self.rows,
            "start": self.start,
            "fl": self.fl,
            "sort": self.sort,
        }

    @classmethod
    def build_query(
        cls,
        terms: List[str],
        author: Optional[str] = None,
        year_range: Optional[tuple] = None,
        min_citations: int = 0,
        sort_by: str = "citation_count desc",
        rows: int = 100,
    ) -> "Query":
        """
        Build a query from components.

        Args:
            terms: List of search terms to AND together
            author: Author name filter
            year_range: Tuple of (min_year, max_year)
            min_citations: Minimum citation threshold
            sort_by: Sort specification
            rows: Rows per request

        Returns:
            Query instance
        """
        query_parts = terms.copy() if terms else ["*"]

        if author:
            query_parts.append(f'author:"{author}"')

        if year_range:
            min_year, max_year = year_range
            query_parts.append(f"year:[{min_year} TO {max_year}]")

        if min_citations > 0:
            query_parts.append(f"citation_count:[{min_citations} TO *]")

        q = " AND ".join(query_parts)
        return cls(q=q, sort=sort_by, rows=rows)


@dataclass
class Results:
    """
    Container for API search results with pagination metadata.

    Attributes:
        papers: List of Paper objects
        total_count: Total matching papers (from server)
        returned_count: Number of papers in this result set
        start: Starting index of this result set
        timestamp: When results were retrieved
    """

    papers: List[Paper] = field(default_factory=list)
    total_count: int = 0
    returned_count: int = 0
    start: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

    def __len__(self) -> int:
        """Return number of papers in results."""
        return len(self.papers)

    def __iter__(self):
        """Iterate over papers."""
        return iter(self.papers)

    def __getitem__(self, index: int) -> Paper:
        """Index into papers list."""
        return self.papers[index]

    def add_paper(self, paper: Paper) -> None:
        """Add a paper to results."""
        if not isinstance(paper, Paper):
            raise TypeError("Can only add Paper instances")
        self.papers.append(paper)

    def has_more(self) -> bool:
        """Check if more results available on server."""
        return self.start + self.returned_count < self.total_count

    def to_list(self) -> List[Dict[str, Any]]:
        """Convert results to list of dictionaries."""
        return [paper.to_dict() for paper in self.papers]

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the result set."""
        if not self.papers:
            return {"total_papers": 0, "avg_citations": 0, "year_range": None}

        citations = [p.citation_count for p in self.papers]
        years = [p.year for p in self.papers]

        return {
            "total_papers": len(self.papers),
            "avg_citations": sum(citations) / len(citations),
            "min_citations": min(citations),
            "max_citations": max(citations),
            "year_range": (min(years), max(years)),
            "retrieved_at": self.timestamp.isoformat(),
        }
