"""
Tests for output formatters.

Tests for CSV, JSON, and BibTeX formatters.
"""

import pytest
import json
import tempfile
from pathlib import Path

from nasa_ads.models.paper import Paper, Results
from nasa_ads.formatters.output_formatter import (
    CSVFormatter,
    JSONFormatter,
    BibTeXFormatter,
    get_formatter,
)


@pytest.fixture
def sample_results():
    """Create sample results for testing."""
    results = Results(total_count=2, returned_count=2, start=0)

    paper1 = Paper(
        bibcode="2021ApJ...919..136K",
        title="Discovery of New Exoplanet",
        year=2021,
        pub="The Astrophysical Journal",
        abstract="A fascinating study of exoplanets",
        keyword=["exoplanet", "transit"],
        citation_count=42,
    )

    paper2 = Paper(
        bibcode="2020ApJ...901..123S",
        title="Study of Dark Matter",
        year=2020,
        pub="The Astrophysical Journal",
        abstract="Understanding dark matter properties",
        keyword=["dark matter", "cosmology"],
        citation_count=15,
    )

    results.add_paper(paper1)
    results.add_paper(paper2)

    return results


class TestCSVFormatter:
    """Tests for CSV formatter."""

    def test_format_csv(self, sample_results):
        """Test formatting results as CSV."""
        formatter = CSVFormatter()
        csv_output = formatter.format(sample_results)

        assert "bibcode" in csv_output
        assert "2021ApJ...919..136K" in csv_output
        assert "2020ApJ...901..123S" in csv_output

    def test_csv_has_header(self, sample_results):
        """Test that CSV output has header."""
        formatter = CSVFormatter()
        csv_output = formatter.format(sample_results)

        lines = csv_output.split("\n")
        assert len(lines) > 1
        assert "bibcode" in lines[0]

    def test_save_csv(self, sample_results):
        """Test saving CSV to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.csv"

            formatter = CSVFormatter()
            formatter.save(sample_results, output_path)

            assert output_path.exists()
            content = output_path.read_text()
            assert "2021ApJ...919..136K" in content


class TestJSONFormatter:
    """Tests for JSON formatter."""

    def test_format_json(self, sample_results):
        """Test formatting results as JSON."""
        formatter = JSONFormatter()
        json_output = formatter.format(sample_results)

        data = json.loads(json_output)
        assert "metadata" in data
        assert "papers" in data

    def test_json_metadata(self, sample_results):
        """Test JSON metadata."""
        formatter = JSONFormatter()
        json_output = formatter.format(sample_results)

        data = json.loads(json_output)
        metadata = data["metadata"]

        assert metadata["total_papers"] == sample_results.total_count
        assert metadata["papers_returned"] == sample_results.returned_count

    def test_json_papers(self, sample_results):
        """Test JSON papers array."""
        formatter = JSONFormatter()
        json_output = formatter.format(sample_results)

        data = json.loads(json_output)
        papers = data["papers"]

        assert len(papers) == 2
        assert papers[0]["bibcode"] == "2021ApJ...919..136K"

    def test_save_json(self, sample_results):
        """Test saving JSON to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.json"

            formatter = JSONFormatter()
            formatter.save(sample_results, output_path)

            assert output_path.exists()
            content = json.loads(output_path.read_text())
            assert content["metadata"]["total_papers"] == 2


class TestBibTeXFormatter:
    """Tests for BibTeX formatter."""

    def test_format_bibtex(self, sample_results):
        """Test formatting results as BibTeX."""
        formatter = BibTeXFormatter()
        bibtex_output = formatter.format(sample_results)

        assert "@article" in bibtex_output or "@" in bibtex_output
        assert "2021ApJ" in bibtex_output

    def test_bibtex_has_fields(self, sample_results):
        """Test that BibTeX has required fields."""
        formatter = BibTeXFormatter()
        bibtex_output = formatter.format(sample_results)

        assert "title" in bibtex_output.lower()
        assert "year" in bibtex_output.lower() or "2021" in bibtex_output

    def test_save_bibtex(self, sample_results):
        """Test saving BibTeX to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.bib"

            formatter = BibTeXFormatter()
            formatter.save(sample_results, output_path)

            assert output_path.exists()
            content = output_path.read_text()
            assert "@" in content


class TestGetFormatter:
    """Tests for get_formatter function."""

    def test_get_csv_formatter(self):
        """Test getting CSV formatter."""
        formatter = get_formatter("csv")
        assert isinstance(formatter, CSVFormatter)

    def test_get_json_formatter(self):
        """Test getting JSON formatter."""
        formatter = get_formatter("json")
        assert isinstance(formatter, JSONFormatter)

    def test_get_bibtex_formatter(self):
        """Test getting BibTeX formatter."""
        formatter = get_formatter("bibtex")
        assert isinstance(formatter, BibTeXFormatter)

    def test_get_invalid_formatter(self):
        """Test getting invalid formatter."""
        with pytest.raises(ValueError, match="Unknown format"):
            get_formatter("xml")


class TestEmptyResults:
    """Tests for formatting empty results."""

    def test_format_empty_csv(self):
        """Test formatting empty results as CSV."""
        results = Results()
        formatter = CSVFormatter()
        output = formatter.format(results)

        assert "bibcode" in output
        # Header should be present even with no papers

    def test_format_empty_json(self):
        """Test formatting empty results as JSON."""
        results = Results()
        formatter = JSONFormatter()
        output = formatter.format(results)

        data = json.loads(output)
        assert data["papers"] == []

    def test_format_empty_bibtex(self):
        """Test formatting empty results as BibTeX."""
        results = Results()
        formatter = BibTeXFormatter()
        output = formatter.format(results)

        assert output.strip() == ""
