"""
Global constants for NASA ADS metadata retriever.

This module centralizes all constants used throughout the application,
including API endpoints, default parameters, and query limits.
"""

# ==============================================================================
# API ENDPOINTS
# ==============================================================================

API_BASE_URL: str = "https://api.adsabs.harvard.edu/v1"
API_SEARCH_ENDPOINT: str = f"{API_BASE_URL}/search/query"
API_EXPORT_ENDPOINT: str = f"{API_BASE_URL}/export/bibtex"

# ==============================================================================
# QUERY PARAMETERS
# ==============================================================================

DEFAULT_ROWS_PER_REQUEST: int = 100
MAX_ROWS_PER_REQUEST: int = 2000
MAX_TOTAL_PAPERS_PER_DAY: int = 5000

# ==============================================================================
# OUTPUT FIELDS
# ==============================================================================

DEFAULT_FIELDS: list = [
    "bibcode",
    "title",
    "year",
    "pub",
    "abstract",
    "keyword",
    "citation_count",
]

OUTPUT_FIELDS_CSV: list = [
    "bibcode",
    "title",
    "year",
    "pub",
    "abstract",
    "keyword",
    "citation_count",
    "BibTeX",
    "ADS_URL",
]

OUTPUT_FIELDS_JSON: list = DEFAULT_FIELDS + ["BibTeX", "ADS_URL"]

# ==============================================================================
# VALIDATION RANGES
# ==============================================================================

MIN_YEAR: int = 1850
MAX_YEAR: int = 2100
MIN_CITATION_COUNT: int = 0
MAX_CITATION_COUNT: int = 100000

# ==============================================================================
# API BEHAVIOR
# ==============================================================================

REQUEST_TIMEOUT_SECONDS: int = 30
MAX_RETRIES: int = 3
RETRY_BACKOFF_FACTOR: float = 0.5  # Exponential backoff: 0.5s, 1s, 2s, etc.

RATE_LIMIT_DELAY_SECONDS: float = 0.1  # Minimum delay between requests
RATE_LIMIT_MAX_PER_MINUTE: int = 600  # Conservative limit

# ==============================================================================
# OUTPUT/LOGGING
# ==============================================================================

DEFAULT_OUTPUT_FORMAT: str = "csv"
SUPPORTED_OUTPUT_FORMATS: list = ["csv", "json", "bibtex"]

DEFAULT_LOG_LEVEL: str = "INFO"
LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ==============================================================================
# ERROR MESSAGES
# ==============================================================================

ERROR_INVALID_API_KEY: str = "Invalid or missing API key"
ERROR_API_RATE_LIMIT: str = "API rate limit exceeded"
ERROR_API_CONNECTION: str = "Failed to connect to NASA ADS API"
ERROR_INVALID_QUERY: str = "Invalid query parameters"

# ==============================================================================
# QUALITY ASSURANCE
# ==============================================================================

ASSERT_VALID_OUTPUT_FORMATS = all(fmt in SUPPORTED_OUTPUT_FORMATS for fmt in SUPPORTED_OUTPUT_FORMATS)
assert ASSERT_VALID_OUTPUT_FORMATS, "Output formats must be in SUPPORTED_OUTPUT_FORMATS"

assert DEFAULT_ROWS_PER_REQUEST <= MAX_ROWS_PER_REQUEST, "Default rows must not exceed max"
assert MAX_ROWS_PER_REQUEST <= MAX_TOTAL_PAPERS_PER_DAY, "Max rows must not exceed daily limit"
