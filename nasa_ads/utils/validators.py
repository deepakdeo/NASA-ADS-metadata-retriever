"""
Input validation utilities for NASA ADS metadata retriever.

This module provides validation functions for common input types
and parameters used throughout the application.
"""

import re
from typing import List, Optional, Tuple
from pathlib import Path


class ValidationError(Exception):
    """Custom exception for validation failures."""

    pass


def validate_api_key(api_key: str) -> bool:
    """
    Validate NASA ADS API key format.

    Args:
        api_key: API key to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If invalid
    """
    if not api_key:
        raise ValidationError("API key cannot be empty")
    if not isinstance(api_key, str):
        raise ValidationError("API key must be a string")
    if len(api_key) < 10:
        raise ValidationError("API key appears too short (min 10 characters)")
    return True


def validate_query(query: str) -> bool:
    """
    Validate search query string.

    Args:
        query: Query string to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If invalid
    """
    if not query:
        raise ValidationError("Query cannot be empty")
    if not isinstance(query, str):
        raise ValidationError("Query must be a string")
    if len(query) > 1000:
        raise ValidationError("Query exceeds maximum length (1000 chars)")
    return True


def validate_year(year: int) -> bool:
    """
    Validate publication year.

    Args:
        year: Year to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If invalid
    """
    if not isinstance(year, int):
        raise ValidationError("Year must be integer")
    if year < 1800 or year > 2100:
        raise ValidationError(f"Year must be between 1800 and 2100, got {year}")
    return True


def validate_year_range(year_range: Tuple[int, int]) -> bool:
    """
    Validate year range tuple.

    Args:
        year_range: Tuple of (min_year, max_year)

    Returns:
        True if valid

    Raises:
        ValidationError: If invalid
    """
    if not isinstance(year_range, tuple) or len(year_range) != 2:
        raise ValidationError("Year range must be tuple of (min, max)")

    min_year, max_year = year_range
    validate_year(min_year)
    validate_year(max_year)

    if min_year > max_year:
        raise ValidationError(f"Min year ({min_year}) greater than max ({max_year})")

    return True


def validate_citation_count(count: int) -> bool:
    """
    Validate citation count.

    Args:
        count: Citation count to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If invalid
    """
    if not isinstance(count, int):
        raise ValidationError("Citation count must be integer")
    if count < 0:
        raise ValidationError(f"Citation count must be non-negative, got {count}")
    if count > 1000000:
        raise ValidationError(f"Citation count seems unreasonably high: {count}")
    return True


def validate_rows_per_request(rows: int) -> bool:
    """
    Validate rows per request parameter.

    Args:
        rows: Number of rows per request

    Returns:
        True if valid

    Raises:
        ValidationError: If invalid
    """
    if not isinstance(rows, int):
        raise ValidationError("Rows must be integer")
    if not 1 <= rows <= 2000:
        raise ValidationError(f"Rows must be between 1 and 2000, got {rows}")
    return True


def validate_output_format(fmt: str) -> bool:
    """
    Validate output format.

    Args:
        fmt: Output format name

    Returns:
        True if valid

    Raises:
        ValidationError: If invalid
    """
    valid_formats = ["csv", "json", "bibtex"]
    if fmt not in valid_formats:
        raise ValidationError(
            f"Output format must be one of {valid_formats}, got {fmt}"
        )
    return True


def validate_output_path(path: str) -> bool:
    """
    Validate output file path.

    Args:
        path: Output file path

    Returns:
        True if valid

    Raises:
        ValidationError: If invalid
    """
    if not path:
        raise ValidationError("Output path cannot be empty")

    path_obj = Path(path)
    parent = path_obj.parent

    # Check if parent directory exists (or is current dir)
    if not parent.exists() and parent != Path("."):
        raise ValidationError(f"Output directory does not exist: {parent}")

    # Check if parent is writable
    try:
        test_file = parent / ".write_test"
        test_file.touch()
        test_file.unlink()
    except (IOError, OSError):
        raise ValidationError(f"Output directory is not writable: {parent}")

    return True


def validate_timeout(timeout: float) -> bool:
    """
    Validate request timeout in seconds.

    Args:
        timeout: Timeout in seconds

    Returns:
        True if valid

    Raises:
        ValidationError: If invalid
    """
    if not isinstance(timeout, (int, float)):
        raise ValidationError("Timeout must be number")
    if timeout <= 0:
        raise ValidationError(f"Timeout must be positive, got {timeout}")
    if timeout > 300:
        raise ValidationError(f"Timeout seems too large (>300s): {timeout}")
    return True


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If invalid
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        raise ValidationError(f"Invalid email format: {email}")
    return True


def validate_bibcode(bibcode: str) -> bool:
    """
    Validate ADS bibcode format.

    Args:
        bibcode: ADS bibcode to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If invalid
    """
    # Format: YYYY[journal/source code]...author[extra]
    # Minimum length check
    if len(bibcode) < 10:
        raise ValidationError(f"Bibcode too short (min 10 chars): {bibcode}")
    
    pattern = r"^\d{4}[a-zA-Z0-9\.&]{1,}$"
    if not re.match(pattern, bibcode):
        raise ValidationError(f"Invalid bibcode format: {bibcode}")
    return True
