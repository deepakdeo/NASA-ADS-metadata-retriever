"""
Output formatters for NASA ADS results.

This module provides formatters to export search results in various
formats: CSV, JSON, and BibTeX.
"""

import csv
import json
from pathlib import Path
from typing import List
from abc import ABC, abstractmethod

from ..models.paper import Results, Paper
from ..utils.logger import get_logger

logger = get_logger(__name__)


class Formatter(ABC):
    """Base class for output formatters."""

    @abstractmethod
    def format(self, results: Results) -> str:
        """Format results as string."""
        pass

    @abstractmethod
    def save(self, results: Results, output_path: Path) -> None:
        """Save formatted results to file."""
        pass


class CSVFormatter(Formatter):
    """Export results to CSV format."""

    FIELDS = [
        "bibcode",
        "title",
        "year",
        "pub",
        "abstract",
        "citation_count",
        "keywords",
        "ADS_URL",
    ]

    def format(self, results: Results) -> str:
        """
        Format results as CSV string.

        Args:
            results: Results object to format

        Returns:
            CSV-formatted string
        """
        # Create temp list to collect CSV rows
        rows = []
        rows.append(",".join(self.FIELDS))

        for paper in results.papers:
            row = {
                "bibcode": paper.bibcode,
                "title": paper.title,
                "year": paper.year,
                "pub": paper.pub,
                "abstract": paper.abstract[:100] + "..."
                if len(paper.abstract) > 100
                else paper.abstract,
                "citation_count": paper.citation_count,
                "keywords": "; ".join(paper.keyword),
                "ADS_URL": paper.ads_url,
            }
            rows.append(self._dict_to_csv_row(row))

        return "\n".join(rows)

    @staticmethod
    def _dict_to_csv_row(row: dict) -> str:
        """Convert dict to CSV row string."""
        output = []
        for field in CSVFormatter.FIELDS:
            value = row.get(field, "")
            # Escape quotes and wrap in quotes if contains comma
            if isinstance(value, str):
                if "," in value or '"' in value or "\n" in value:
                    value = '"' + value.replace('"', '""') + '"'
            output.append(str(value))
        return ",".join(output)

    def save(self, results: Results, output_path: Path) -> None:
        """
        Save results to CSV file.

        Args:
            results: Results to save
            output_path: Path to output file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDS)
            writer.writeheader()

            for paper in results.papers:
                writer.writerow(
                    {
                        "bibcode": paper.bibcode,
                        "title": paper.title,
                        "year": paper.year,
                        "pub": paper.pub,
                        "abstract": paper.abstract[:100] + "..."
                        if len(paper.abstract) > 100
                        else paper.abstract,
                        "citation_count": paper.citation_count,
                        "keywords": "; ".join(paper.keyword),
                        "ADS_URL": paper.ads_url,
                    }
                )

        logger.info(f"Saved {len(results.papers)} papers to {output_path}")


class JSONFormatter(Formatter):
    """Export results to JSON format."""

    def format(self, results: Results) -> str:
        """
        Format results as JSON string.

        Args:
            results: Results object to format

        Returns:
            JSON-formatted string
        """
        data = {
            "metadata": {
                "total_papers": results.total_count,
                "papers_returned": results.returned_count,
                "start": results.start,
                "timestamp": results.timestamp.isoformat(),
            },
            "papers": results.to_list(),
        }
        return json.dumps(data, indent=2)

    def save(self, results: Results, output_path: Path) -> None:
        """
        Save results to JSON file.

        Args:
            results: Results to save
            output_path: Path to output file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(self.format(results))

        logger.info(f"Saved {len(results.papers)} papers to {output_path}")


class BibTeXFormatter(Formatter):
    """Export results to BibTeX format."""

    def format(self, results: Results) -> str:
        """
        Format results as BibTeX string.

        Args:
            results: Results object to format

        Returns:
            BibTeX-formatted string
        """
        entries = []

        for paper in results.papers:
            if paper.bibtex:
                entries.append(paper.bibtex)
            else:
                # Generate minimal BibTeX entry
                entry = self._generate_bibtex(paper)
                entries.append(entry)

        return "\n\n".join(entries)

    @staticmethod
    def _generate_bibtex(paper: Paper) -> str:
        """
        Generate BibTeX entry for paper.

        Args:
            paper: Paper to convert

        Returns:
            BibTeX entry string
        """
        # Determine entry type
        entry_type = "article"

        # Clean title
        title = paper.title.replace("{", "").replace("}", "")

        # Extract author from bibcode or use generic
        author = extract_author_from_bibcode(paper.bibcode)

        entry = f"""@{entry_type}{{{paper.bibcode},
    title = {{{title}}},
    author = {{{author}}},
    year = {{{paper.year}}},
    journal = {{{paper.pub}}}
}}"""

        return entry

    def save(self, results: Results, output_path: Path) -> None:
        """
        Save results to BibTeX file.

        Args:
            results: Results to save
            output_path: Path to output file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(self.format(results))

        logger.info(f"Saved {len(results.papers)} papers to {output_path}")


def extract_author_from_bibcode(bibcode: str) -> str:
    """
    Extract author information from bibcode.

    Format: YYYY[source]....author[extra]
    Example: 2021ApJ...919..136K -> K

    Args:
        bibcode: ADS bibcode

    Returns:
        Author abbreviation or "Unknown"
    """
    if len(bibcode) > 20:
        # Last meaningful character might be author initial
        # This is simplified - full parsing would need ADS API
        return bibcode[-1].upper() if bibcode[-1].isalpha() else "Unknown"
    return "Unknown"


def get_formatter(format_name: str) -> Formatter:
    """
    Get formatter instance by name.

    Args:
        format_name: Format name (csv, json, bibtex)

    Returns:
        Formatter instance

    Raises:
        ValueError: If format not supported
    """
    formatters = {
        "csv": CSVFormatter(),
        "json": JSONFormatter(),
        "bibtex": BibTeXFormatter(),
    }

    if format_name not in formatters:
        raise ValueError(f"Unknown format: {format_name}")

    return formatters[format_name]
