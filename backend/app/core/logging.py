"""
Logging Configuration — Structured logging setup for Stream2Vec.

Configures structured JSON logging for production and human-readable
text logging for development. Uses Python standard logging library.
"""

import logging
import sys
from typing import Any


def configure_logging(level: str = "INFO", fmt: str = "json") -> None:
    """Configure application-wide logging.

    Args:
        level: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        fmt: Output format — 'json' for production, 'text' for development.
    """
    # TODO: Implement structured JSON logging (e.g., with python-json-logger)
    # TODO: Add request ID injection into log context
    # TODO: Configure log handlers (stdout, file, remote)

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        stream=sys.stdout,
    )

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger instance.

    Args:
        name: Logger name, typically __name__ of the calling module.

    Returns:
        logging.Logger: Configured logger instance.
    """
    return logging.getLogger(name)
