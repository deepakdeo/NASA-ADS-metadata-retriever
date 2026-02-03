"""
Example script: Basic search and export

This example demonstrates basic search functionality:
- Searching for papers by topic
- Exporting results to different formats
"""

from pathlib import Path
from nasa_ads import NASAADSClient, Query


def main():
    """Run example search."""
    # Initialize client (requires NASA_ADS_API_KEY environment variable)
    # Set via: export NASA_ADS_API_KEY="your-api-key"
    client = NASAADSClient(api_key="your-api-key-here")

    # Example 1: Simple search
    print("=== Simple Search ===")
    simple_query = Query(q="supernova")
    results = client.search(simple_query)

    print(f"Total papers found: {results.total_count}")
    print(f"Papers in this batch: {len(results.papers)}")

    for paper in results.papers[:3]:  # Show first 3
        print(f"\n{paper.bibcode}: {paper.title}")
        print(f"  Year: {paper.year}, Citations: {paper.citation_count}")

    # Example 2: Advanced search with filters
    print("\n\n=== Advanced Search ===")
    query = Query.build_query(
        terms=["gravitational waves"],
        author="Abbott",
        year_range=(2015, 2022),
        min_citations=10,
        rows=50,
    )

    results = client.search(query)
    print(f"Found {len(results.papers)} highly cited papers with author Abbott")

    # Example 3: Export results
    print("\n\n=== Export Results ===")
    from nasa_ads.formatters.output_formatter import (
        CSVFormatter,
        JSONFormatter,
        BibTeXFormatter,
    )

    # Export as CSV
    csv_formatter = CSVFormatter()
    csv_formatter.save(results, Path("results.csv"))
    print("✓ Saved results.csv")

    # Export as JSON
    json_formatter = JSONFormatter()
    json_formatter.save(results, Path("results.json"))
    print("✓ Saved results.json")

    # Export as BibTeX
    bibtex_formatter = BibTeXFormatter()
    bibtex_formatter.save(results, Path("results.bib"))
    print("✓ Saved results.bib")

    # Statistics
    print("\n\n=== Statistics ===")
    stats = results.get_statistics()
    print(f"Total papers: {stats['total_papers']}")
    print(f"Average citations: {stats['avg_citations']:.1f}")
    print(f"Year range: {stats['year_range']}")

    client.close()


if __name__ == "__main__":
    main()
