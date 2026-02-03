"""
Tests for data models.

Tests for Paper, Query, and Results classes.
"""

import pytest
from datetime import datetime

from nasa_ads.models.paper import Paper, Query, Results


class TestPaper:
    """Tests for Paper model."""

    def test_create_paper_valid(self):
        """Test creating a valid paper."""
        paper = Paper(
            bibcode="2021ApJ...919..136K",
            title="Discovery of New Exoplanet",
            year=2021,
            pub="The Astrophysical Journal",
            abstract="A fascinating study...",
            keyword=["exoplanet", "transit"],
            citation_count=42,
        )

        assert paper.bibcode == "2021ApJ...919..136K"
        assert paper.title == "Discovery of New Exoplanet"
        assert paper.year == 2021
        assert paper.citation_count == 42

    def test_paper_ads_url(self):
        """Test ADS URL generation."""
        paper = Paper(
            bibcode="2021ApJ...919..136K",
            title="Test",
            year=2021,
            pub="Test Journal",
            abstract="Test",
        )

        url = paper.ads_url
        assert "2021ApJ...919..136K" in url
        assert url.startswith("https://ui.adsabs.harvard.edu/abs/")

    def test_paper_to_dict(self):
        """Test converting paper to dictionary."""
        paper = Paper(
            bibcode="2021ApJ...919..136K",
            title="Test Paper",
            year=2021,
            pub="Journal",
            abstract="Abstract",
            keyword=["keyword1"],
            citation_count=5,
        )

        paper_dict = paper.to_dict()

        assert paper_dict["bibcode"] == "2021ApJ...919..136K"
        assert paper_dict["title"] == "Test Paper"
        assert paper_dict["url"] == paper.ads_url

    def test_paper_invalid_year(self):
        """Test paper with invalid year."""
        with pytest.raises(ValueError, match="year must be integer"):
            Paper(
                bibcode="2021ApJ...919..136K",
                title="Test",
                year=1700,
                pub="Journal",
                abstract="",
            )

    def test_paper_negative_citations(self):
        """Test paper with negative citation count."""
        with pytest.raises(ValueError, match="citation_count must be non-negative"):
            Paper(
                bibcode="2021ApJ...919..136K",
                title="Test",
                year=2021,
                pub="Journal",
                abstract="",
                citation_count=-5,
            )

    def test_paper_missing_bibcode(self):
        """Test paper without bibcode."""
        with pytest.raises(ValueError, match="bibcode must be a non-empty"):
            Paper(
                bibcode="",
                title="Test",
                year=2021,
                pub="Journal",
                abstract="",
            )


class TestQuery:
    """Tests for Query model."""

    def test_create_query_simple(self):
        """Test creating a simple query."""
        query = Query(q="supernova")

        assert query.q == "supernova"
        assert query.rows == 100
        assert query.start == 0

    def test_query_to_params(self):
        """Test converting query to params dict."""
        query = Query(
            q="black hole",
            rows=50,
            start=0,
        )

        params = query.to_params()

        assert params["q"] == "black hole"
        assert params["rows"] == 50
        assert "sort" in params

    def test_query_build_simple(self):
        """Test building query from components."""
        query = Query.build_query(terms=["supernova", "type Ia"])

        assert "supernova" in query.q
        assert "type Ia" in query.q

    def test_query_build_with_author(self):
        """Test building query with author filter."""
        query = Query.build_query(
            terms=["dark matter"],
            author="Smith",
        )

        assert "dark matter" in query.q
        assert "Smith" in query.q

    def test_query_build_with_year_range(self):
        """Test building query with year range."""
        query = Query.build_query(
            terms=["pulsar"],
            year_range=(2015, 2023),
        )

        assert "[2015 TO 2023]" in query.q

    def test_query_build_with_citations(self):
        """Test building query with citation threshold."""
        query = Query.build_query(
            terms=["galaxy"],
            min_citations=100,
        )

        assert "[100 TO *]" in query.q

    def test_query_invalid_rows(self):
        """Test query with invalid rows count."""
        with pytest.raises(ValueError, match="rows must be between"):
            Query(q="test", rows=5000)

    def test_query_empty_string(self):
        """Test query with empty string."""
        with pytest.raises(ValueError, match="Query string"):
            Query(q="")


class TestResults:
    """Tests for Results model."""

    def test_create_results_empty(self):
        """Test creating empty results."""
        results = Results()

        assert len(results) == 0
        assert results.total_count == 0

    def test_results_add_paper(self):
        """Test adding paper to results."""
        results = Results()

        paper = Paper(
            bibcode="2021ApJ...919..136K",
            title="Test",
            year=2021,
            pub="Journal",
            abstract="",
        )

        results.add_paper(paper)

        assert len(results) == 1
        assert results[0].bibcode == "2021ApJ...919..136K"

    def test_results_iterator(self):
        """Test iterating over results."""
        results = Results()

        for i in range(3):
            paper = Paper(
                bibcode=f"2021ApJ...919..{100+i}K",
                title=f"Paper {i}",
                year=2021,
                pub="Journal",
                abstract="",
            )
            results.add_paper(paper)

        count = 0
        for paper in results:
            count += 1
            assert isinstance(paper, Paper)

        assert count == 3

    def test_results_has_more(self):
        """Test checking if more results available."""
        results = Results(total_count=1000, returned_count=100, start=0)

        assert results.has_more() is True

        results2 = Results(total_count=50, returned_count=50, start=0)

        assert results2.has_more() is False

    def test_results_get_statistics(self):
        """Test getting result statistics."""
        results = Results()

        for i in range(5):
            paper = Paper(
                bibcode=f"202{i}ApJ...919..136K",
                title=f"Paper {i}",
                year=2020 + i,
                pub="Journal",
                abstract="",
                citation_count=10 * i,
            )
            results.add_paper(paper)

        stats = results.get_statistics()

        assert stats["total_papers"] == 5
        assert "avg_citations" in stats
        assert "year_range" in stats
        assert stats["year_range"] == (2020, 2024)

    def test_results_to_list(self):
        """Test converting results to list."""
        results = Results()

        paper = Paper(
            bibcode="2021ApJ...919..136K",
            title="Test",
            year=2021,
            pub="Journal",
            abstract="Abstract",
            keyword=["test"],
        )

        results.add_paper(paper)
        result_list = results.to_list()

        assert len(result_list) == 1
        assert result_list[0]["bibcode"] == "2021ApJ...919..136K"
