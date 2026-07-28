"""
Stream2Vec — Logging Configuration.

Configures structured JSON logging for production use.
Supports both JSON (production) and text (development) formats.
"""

import logging
import sys
from typing import Any, Dict

from app.core.config import settings


def setup_logging() -> None:
    """Configure application-wide logging.
    
    Sets up structured logging based on LOG_FORMAT setting:
    - 'json': Structured JSON logs (production)
    - 'text': Human-readable logs (development)
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)

    if settings.LOG_FORMAT == "json":
        formatter = _create_json_formatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    handler.setFormatter(formatter)

    logging.basicConfig(
        level=log_level,
        handlers=[handler],
    )

    # Silence noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info(
        "Logging configured",
        extra={"log_level": settings.LOG_LEVEL, "log_format": settings.LOG_FORMAT},
    )


def _create_json_formatter() -> logging.Formatter:
    """Create a JSON log formatter.
    
    Returns:
        logging.Formatter: JSON formatter instance.
    """
    # TODO: Replace with structlog or python-json-logger in production
    return logging.Formatter(
        fmt='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


def get_logger(name: str) -> logging.Logger:
    """Get a named logger instance.
    
    Args:
        name: Logger name (typically __name__).
        
    Returns:
        logging.Logger: Configured logger.
    """
    return logging.getLogger(name)
