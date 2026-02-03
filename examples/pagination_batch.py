"""
Example script: Pagination and batch processing

This example demonstrates:
- Handling pagination for large result sets
- Processing results in batches
- Tracking metadata across requests
"""

from nasa_ads import NASAADSClient, Query


def main():
    """Run example with pagination."""
    client = NASAADSClient(api_key="your-api-key-here")

    # Create query
    query = Query.build_query(
        terms=["exoplanet"],
        year_range=(2015, 2024),
        rows=100,  # 100 papers per request
    )

    print("=== Batch Processing Example ===\n")

    total_processed = 0
    batch_count = 0

    while total_processed < 500:  # Process first 500 papers
        print(f"Fetching batch {batch_count + 1} (start={query.start})...")

        results = client.search(query)

        print(f"  Retrieved {len(results.papers)} papers")
        print(f"  Total available: {results.total_count}")

        batch_count += 1
        total_processed += len(results.papers)

        # Process results
        for paper in results.papers:
            print(f"  - {paper.bibcode}: {paper.title[:50]}...")

        # Check if more results available
        if not results.has_more():
            print("\nNo more results available")
            break

        # Move to next batch
        query.start += query.rows

    print(f"\n✓ Processed {total_processed} papers in {batch_count} batches")

    client.close()


if __name__ == "__main__":
    main()
