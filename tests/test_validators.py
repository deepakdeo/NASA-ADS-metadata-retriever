"""
Tests for input validators.

Tests for validation functions used throughout the application.
"""

import pytest
from pathlib import Path
import tempfile

from nasa_ads.utils.validators import (
    ValidationError,
    validate_api_key,
    validate_query,
    validate_year,
    validate_year_range,
    validate_citation_count,
    validate_rows_per_request,
    validate_output_format,
    validate_output_path,
    validate_timeout,
    validate_email,
    validate_bibcode,
)


class TestValidateAPIKey:
    """Tests for API key validation."""

    def test_valid_api_key(self):
        """Test with valid API key."""
        assert validate_api_key("abc1234567890def") is True

    def test_empty_api_key(self):
        """Test with empty API key."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_api_key("")

    def test_short_api_key(self):
        """Test with too short API key."""
        with pytest.raises(ValidationError, match="too short"):
            validate_api_key("short")

    def test_non_string_api_key(self):
        """Test with non-string API key."""
        with pytest.raises(ValidationError, match="must be a string"):
            validate_api_key(12345)


class TestValidateQuery:
    """Tests for query validation."""

    def test_valid_query(self):
        """Test with valid query."""
        assert validate_query("supernova") is True

    def test_empty_query(self):
        """Test with empty query."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_query("")

    def test_long_query(self):
        """Test with query exceeding max length."""
        long_query = "a" * 1001
        with pytest.raises(ValidationError, match="exceeds maximum"):
            validate_query(long_query)

    def test_non_string_query(self):
        """Test with non-string query."""
        with pytest.raises(ValidationError, match="must be a string"):
            validate_query(123)


class TestValidateYear:
    """Tests for year validation."""

    def test_valid_year(self):
        """Test with valid year."""
        assert validate_year(2021) is True
        assert validate_year(1900) is True
        assert validate_year(2100) is True

    def test_year_too_old(self):
        """Test with year too old."""
        with pytest.raises(ValidationError, match="must be between"):
            validate_year(1700)

    def test_year_too_new(self):
        """Test with year too new."""
        with pytest.raises(ValidationError, match="must be between"):
            validate_year(2200)

    def test_non_integer_year(self):
        """Test with non-integer year."""
        with pytest.raises(ValidationError, match="must be integer"):
            validate_year("2021")


class TestValidateYearRange:
    """Tests for year range validation."""

    def test_valid_year_range(self):
        """Test with valid year range."""
        assert validate_year_range((2010, 2020)) is True

    def test_inverted_year_range(self):
        """Test with inverted year range."""
        with pytest.raises(ValidationError, match="Min year.*greater than max"):
            validate_year_range((2020, 2010))

    def test_non_tuple_year_range(self):
        """Test with non-tuple year range."""
        with pytest.raises(ValidationError, match="must be tuple"):
            validate_year_range([2010, 2020])


class TestValidateCitationCount:
    """Tests for citation count validation."""

    def test_valid_citation_count(self):
        """Test with valid citation count."""
        assert validate_citation_count(0) is True
        assert validate_citation_count(100) is True
        assert validate_citation_count(10000) is True

    def test_negative_citation_count(self):
        """Test with negative citation count."""
        with pytest.raises(ValidationError, match="must be non-negative"):
            validate_citation_count(-5)

    def test_unreasonably_high_count(self):
        """Test with unreasonably high citation count."""
        with pytest.raises(ValidationError, match="unreasonably high"):
            validate_citation_count(10000000)

    def test_non_integer_count(self):
        """Test with non-integer count."""
        with pytest.raises(ValidationError, match="must be integer"):
            validate_citation_count("100")


class TestValidateRowsPerRequest:
    """Tests for rows per request validation."""

    def test_valid_rows(self):
        """Test with valid rows count."""
        assert validate_rows_per_request(1) is True
        assert validate_rows_per_request(100) is True
        assert validate_rows_per_request(2000) is True

    def test_rows_too_high(self):
        """Test with rows count exceeding max."""
        with pytest.raises(ValidationError, match="must be between"):
            validate_rows_per_request(3000)

    def test_rows_zero(self):
        """Test with zero rows."""
        with pytest.raises(ValidationError, match="must be between"):
            validate_rows_per_request(0)


class TestValidateOutputFormat:
    """Tests for output format validation."""

    def test_valid_format_csv(self):
        """Test with valid CSV format."""
        assert validate_output_format("csv") is True

    def test_valid_format_json(self):
        """Test with valid JSON format."""
        assert validate_output_format("json") is True

    def test_valid_format_bibtex(self):
        """Test with valid BibTeX format."""
        assert validate_output_format("bibtex") is True

    def test_invalid_format(self):
        """Test with invalid format."""
        with pytest.raises(ValidationError, match="must be one of"):
            validate_output_format("yaml")


class TestValidateOutputPath:
    """Tests for output path validation."""

    def test_valid_output_path(self):
        """Test with valid output path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output.csv"
            assert validate_output_path(str(output_path)) is True

    def test_invalid_output_directory(self):
        """Test with non-existent output directory."""
        with pytest.raises(ValidationError, match="does not exist"):
            validate_output_path("/nonexistent/directory/output.csv")

    def test_empty_output_path(self):
        """Test with empty output path."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_output_path("")


class TestValidateTimeout:
    """Tests for timeout validation."""

    def test_valid_timeout(self):
        """Test with valid timeout."""
        assert validate_timeout(30) is True
        assert validate_timeout(5.5) is True

    def test_zero_timeout(self):
        """Test with zero timeout."""
        with pytest.raises(ValidationError, match="must be positive"):
            validate_timeout(0)

    def test_too_large_timeout(self):
        """Test with timeout too large."""
        with pytest.raises(ValidationError, match="seems too large"):
            validate_timeout(400)


class TestValidateEmail:
    """Tests for email validation."""

    def test_valid_email(self):
        """Test with valid email."""
        assert validate_email("user@example.com") is True
        assert validate_email("test.user+tag@domain.co.uk") is True

    def test_invalid_email(self):
        """Test with invalid email."""
        with pytest.raises(ValidationError, match="Invalid email"):
            validate_email("not-an-email")

    def test_email_without_domain(self):
        """Test with email without domain."""
        with pytest.raises(ValidationError, match="Invalid email"):
            validate_email("user@")


class TestValidateBibcode:
    """Tests for bibcode validation."""

    def test_valid_bibcode(self):
        """Test with valid bibcode."""
        assert validate_bibcode("2021ApJ...919..136K") is True
        assert validate_bibcode("1999MNRAS.305..325B") is True

    def test_invalid_bibcode_format(self):
        """Test with invalid bibcode format."""
        with pytest.raises(ValidationError, match="Invalid bibcode"):
            validate_bibcode("not-a-bibcode")

    def test_bibcode_too_short(self):
        """Test with too short bibcode."""
        with pytest.raises(ValidationError, match="too short"):
            validate_bibcode("2021A")
