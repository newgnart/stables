import os
from typing import Optional, Any, Dict
import logging
import logging.handlers


logger = logging.getLogger(__name__)


def setup_streaming_logging():
    """Sets up console streaming logging only."""
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)


def setup_file_logging(log_file: str):
    """Sets up file logging with rotation."""
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    root_logger = logging.getLogger()

    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
