"""
Stream2Vec — Error Handling Middleware.

Catches unhandled exceptions and returns standardized error responses.
"""

import logging
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware to catch and format unhandled exceptions."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and catch unhandled exceptions."""
        try:
            return await call_next(request)
        except Exception as exc:
            logger.exception(
                "Unhandled exception",
                extra={"path": str(request.url.path), "method": request.method},
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": "internal_server_error",
                    "message": "An unexpected error occurred.",
                },
            )
