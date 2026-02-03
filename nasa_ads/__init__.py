"""
NASA ADS Metadata Retriever - Query and export astronomy paper metadata.

This package provides a Python interface to the NASA ADS API for retrieving
astronomical literature metadata with support for multiple output formats.

Quick Start:
    from nasa_ads import NASAADSClient, Query
    
    client = NASAADSClient(api_key="your-api-key")
    query = Query.build_query(["supernova"], year_range=(2020, 2024))
    results = client.search(query)
    
    for paper in results:
        print(paper.title, paper.year)
"""

from .core.api_client import NASAADSClient, APIError
from .models.paper import Paper, Query, Results
from .config.config_loader import ConfigLoader
from .utils.validators import ValidationError, validate_api_key, validate_query
from .utils.logger import setup_logger, get_logger
from .formatters.output_formatter import (
    get_formatter,
    CSVFormatter,
    JSONFormatter,
    BibTeXFormatter,
)

__version__ = "2.0.0"
__author__ = "Deepak Deo"

__all__ = [
    "NASAADSClient",
    "APIError",
    "Paper",
    "Query",
    "Results",
    "ConfigLoader",
    "ValidationError",
    "validate_api_key",
    "validate_query",
    "setup_logger",
    "get_logger",
    "get_formatter",
    "CSVFormatter",
    "JSONFormatter",
    "BibTeXFormatter",
]
