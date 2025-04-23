"""Logging configuration."""

import logging
import sys
from logging.handlers import RotatingFileHandler
from stables.config.settings import LOG_LEVEL, LOG_FORMAT, LOG_FILE


def setup_logging():
    """Configure logging for the application."""
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)

    # Check if handlers are already configured to avoid duplicates
    if logger.hasHandlers():
        # If handlers already exist, return the existing logger
        return logger

    # Create formatters
    formatter = logging.Formatter(LOG_FORMAT)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
