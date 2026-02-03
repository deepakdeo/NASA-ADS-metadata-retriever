"""
Command-line interface for NASA ADS metadata retriever.

Provides argparse-based CLI with multiple subcommands for querying,
exporting, and managing NASA ADS searches.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .core.api_client import NASAADSClient, APIError
from .models.paper import Query
from .config.config_loader import ConfigLoader
from .utils.logger import setup_logger
from .utils.validators import ValidationError, validate_output_path
from .formatters.output_formatter import get_formatter
from . import __version__


def create_parser() -> argparse.ArgumentParser:
    """Create and return argument parser."""
    parser = argparse.ArgumentParser(
        prog="nasa-ads-finder",
        description="Query and export astronomy paper metadata from NASA ADS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for supernova papers
  nasa-ads-finder search "supernova" --output results.csv
  
  # Search with year range
  nasa-ads-finder search "gravitational waves" --year-min 2020 --year-max 2024
  
  # Export as JSON with author filter
  nasa-ads-finder search "dark matter" --author "Smith" --format json
        """,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "--config",
        type=Path,
        help="Path to YAML configuration file",
    )

    parser.add_argument(
        "--api-key",
        help="NASA ADS API key (overrides config file and .env)",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Search subcommand
    search_parser = subparsers.add_parser(
        "search",
        help="Search NASA ADS database",
    )

    search_parser.add_argument(
        "query",
        help="Search query string",
    )

    search_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file path",
    )

    search_parser.add_argument(
        "-f",
        "--format",
        choices=["csv", "json", "bibtex"],
        default="csv",
        help="Output format (default: csv)",
    )

    search_parser.add_argument(
        "--rows",
        type=int,
        default=100,
        help="Number of results per request (default: 100, max: 2000)",
    )

    search_parser.add_argument(
        "--author",
        help="Filter by author name",
    )

    search_parser.add_argument(
        "--year-min",
        type=int,
        help="Minimum publication year",
    )

    search_parser.add_argument(
        "--year-max",
        type=int,
        help="Maximum publication year",
    )

    search_parser.add_argument(
        "--min-citations",
        type=int,
        default=0,
        help="Minimum citation count (default: 0)",
    )

    search_parser.add_argument(
        "--sort",
        default="citation_count desc",
        help="Sort by field (default: citation_count desc)",
    )

    search_parser.set_defaults(func=cmd_search)

    # Builder subcommand
    builder_parser = subparsers.add_parser(
        "builder",
        help="Interactive query builder",
    )

    builder_parser.set_defaults(func=cmd_builder)

    # Config subcommand
    config_parser = subparsers.add_parser(
        "config",
        help="Show or validate configuration",
    )

    config_parser.set_defaults(func=cmd_config)

    return parser


def cmd_search(args) -> int:
    """Execute search command."""
    logger = setup_logger(__name__, level=args.log_level)

    try:
        # Load configuration
        config = ConfigLoader.from_default_locations()
        if args.config:
            config = ConfigLoader(config_file=args.config)

        # Get API key
        api_key = args.api_key or config.get("api_key")
        if not api_key:
            logger.error("API key not found. Set NASA_ADS_API_KEY or use --api-key")
            return 1

        # Create client
        client = NASAADSClient(api_key=api_key)

        # Build query
        year_range = None
        if args.year_min and args.year_max:
            year_range = (args.year_min, args.year_max)

        query = Query.build_query(
            terms=[args.query],
            author=args.author,
            year_range=year_range,
            min_citations=args.min_citations,
            sort_by=args.sort,
            rows=args.rows,
        )

        logger.info(f"Executing query: {query.q}")

        # Execute search
        results = client.search(query)
        logger.info(f"Found {results.total_count} total papers")
        logger.info(f"Retrieved {len(results.papers)} papers in this batch")

        # Output results
        if args.output:
            validate_output_path(str(args.output))
            formatter = get_formatter(args.format)
            formatter.save(results, args.output)
            logger.info(f"Results saved to {args.output}")
        else:
            # Print to stdout
            formatter = get_formatter(args.format)
            print(formatter.format(results))

        client.close()
        return 0

    except (ValidationError, APIError) as e:
        logger.error(f"Error: {e}")
        return 1
    except KeyboardInterrupt:
        logger.info("Search cancelled by user")
        return 130
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


def cmd_builder(args) -> int:
    """Interactive query builder."""
    logger = setup_logger(__name__, level=args.log_level)

    print("\n=== NASA ADS Query Builder ===\n")
    print("Enter query parameters (press Enter to skip optional fields):\n")

    try:
        # Get basic parameters
        terms = input("Search terms (comma-separated): ").split(",")
        terms = [t.strip() for t in terms if t.strip()]

        author = input("Author (optional): ").strip() or None
        year_min_str = input("Min year (optional): ").strip()
        year_max_str = input("Max year (optional): ").strip()
        min_citations_str = input("Min citations (optional, default: 0): ").strip()

        year_range = None
        if year_min_str and year_max_str:
            year_range = (int(year_min_str), int(year_max_str))

        min_citations = int(min_citations_str) if min_citations_str else 0

        # Build and display query
        query = Query.build_query(
            terms=terms,
            author=author,
            year_range=year_range,
            min_citations=min_citations,
        )

        print(f"\nGenerated Query: {query.q}")
        print(f"Parameters: rows={query.rows}, sort={query.sort}")

        return 0

    except (ValueError, KeyboardInterrupt) as e:
        logger.error(f"Error: {e}")
        return 1


def cmd_config(args) -> int:
    """Show configuration."""
    logger = setup_logger(__name__, level=args.log_level)

    try:
        config = ConfigLoader.from_default_locations()
        config_dict = config.to_dict()

        print("\n=== Configuration ===\n")
        for key, value in config_dict.items():
            # Mask API key
            if key == "api_key":
                value = "***" if value else "(not set)"
            print(f"{key}: {value}")

        print()
        return 0

    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


def main(argv: Optional[list] = None) -> int:
    """
    Main entry point for CLI.

    Args:
        argv: Command-line arguments (default: sys.argv[1:])

    Returns:
        Exit code
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
