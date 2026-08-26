"""
Logging Configuration — Structured logging for Stream2Vec.

Supports two formats:
  - json: Structured JSON output for production (Prometheus, Loki, etc.)
  - text: Human-readable format for local development

Usage:
    configure_logging(level="INFO", fmt="json")
    logger = get_logger(__name__)
"""

import logging
import sys
from typing import Any

from pythonjsonlogger import jsonlogger


class _JsonFormatter(jsonlogger.JsonFormatter):
    """Extended JSON formatter that adds service metadata to every log record."""

    def add_fields(
        self,
        log_record: dict[str, Any],
        record: logging.LogRecord,
        message_dict: dict[str, Any],
    ) -> None:
        super().add_fields(log_record, record, message_dict)
        log_record["service"] = "stream2vec-backend"
        log_record["level"] = record.levelname
        # Remove the redundant 'levelname' key added by the base class
        log_record.pop("levelname", None)


def configure_logging(level: str = "INFO", fmt: str = "json") -> None:
    """Configure application-wide logging.

    Should be called once at application startup (inside the lifespan handler).

    Args:
        level: Log level string. One of DEBUG, INFO, WARNING, ERROR, CRITICAL.
        fmt:   Output format. 'json' for production, 'text' for development.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove any existing handlers (e.g. from basicConfig called elsewhere)
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)

    if fmt == "json":
        formatter = _JsonFormatter(
            fmt="%(asctime)s %(level)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("aiokafka").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger instance.

    Args:
        name: Logger name, typically ``__name__`` of the calling module.

    Returns:
        logging.Logger: Named logger.
    """
    return logging.getLogger(name)
