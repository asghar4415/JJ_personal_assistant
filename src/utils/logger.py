"""
logger.py - Logging configuration for JJ (JARVIS-inspired)

Sets up structured logging with file and console output
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logger(name, log_level=logging.INFO):
    """
    Configure logger with file and console handlers

    Args:
        name: Logger name (typically __name__)
        log_level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """

    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    # Log format
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_dir / "jj.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
