"""
Logging Middleware — Request/response logging with correlation IDs.

Injects a unique request ID into each request for distributed tracing.
Logs request duration, status code, and correlation ID.
"""

import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """HTTP middleware for structured request/response logging.

    Adds a unique request ID to each request and logs:
    - Incoming request method, path, and client IP
    - Response status code and duration
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request, inject request ID, and log request details.

        Args:
            request: Incoming HTTP request.
            call_next: Next middleware or route handler.

        Returns:
            Response: HTTP response with added X-Request-ID header.
        """
        request_id = str(uuid.uuid4())
        start_time = time.perf_counter()

        # TODO: Inject request_id into logging context (contextvars)
        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown",
            },
        )

        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
            },
        )

        response.headers["X-Request-ID"] = request_id
        return response
