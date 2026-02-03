"""
Logging configuration for NASA ADS metadata retriever.

This module provides centralized logging setup with console
and optional file output.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str,
    level: str = "INFO",
    log_file: Optional[Path] = None,
    log_format: Optional[str] = None,
) -> logging.Logger:
    """
    Set up and return a configured logger.

    Args:
        name: Logger name (typically __name__)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging (in addition to console)
        log_format: Custom log format string

    Returns:
        Configured logger instance

    Example:
        >>> logger = setup_logger(__name__, level="DEBUG")
        >>> logger.info("Application started")
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))

    # Avoid duplicate handlers if logger already configured
    if logger.handlers:
        return logger

    # Create format string
    if log_format is None:
        log_format = (
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        )

    formatter = logging.Formatter(log_format)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get an already-configured logger by name.

    Args:
        name: Logger name

    Returns:
        Logger instance (must be configured first with setup_logger)
    """
    return logging.getLogger(name)
