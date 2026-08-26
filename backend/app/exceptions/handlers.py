"""
Exception Handlers — FastAPI exception handler registrations.

Maps custom exceptions and built-in FastAPI/HTTP exceptions to structured,
consistent JSON error responses.

All error responses follow this schema:
    {
        "error":   "<ExceptionClassName>",
        "message": "<human-readable description>",
        "path":    "<request path>"
    }

For validation errors (422), the 'detail' field contains the full list of
validation failures returned by Pydantic.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


# =============================================================================
# Domain Exceptions
# =============================================================================


class Stream2VecException(Exception):
    """Base exception for all Stream2Vec domain errors."""

    def __init__(self, message: str, status_code: int = 500) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class DocumentNotFoundException(Stream2VecException):
    """Raised when a requested document does not exist."""

    def __init__(self, document_id: str) -> None:
        super().__init__(f"Document '{document_id}' not found.", status_code=404)


class StorageException(Stream2VecException):
    """Raised when a MinIO storage operation fails."""

    def __init__(self, detail: str) -> None:
        super().__init__(f"Storage error: {detail}", status_code=503)


class MessagingException(Stream2VecException):
    """Raised when a Kafka messaging operation fails."""

    def __init__(self, detail: str) -> None:
        super().__init__(f"Messaging error: {detail}", status_code=503)


class VectorStoreException(Stream2VecException):
    """Raised when a Qdrant vector store operation fails."""

    def __init__(self, detail: str) -> None:
        super().__init__(f"Vector store error: {detail}", status_code=503)


# =============================================================================
# Handler Registration
# =============================================================================


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI application.

    Args:
        app: The FastAPI application instance.
    """

    @app.exception_handler(Stream2VecException)
    async def stream2vec_exception_handler(
        request: Request, exc: Stream2VecException
    ) -> JSONResponse:
        """Handle all Stream2Vec domain exceptions."""
        logger.warning(
            "Domain exception",
            extra={
                "exception": type(exc).__name__,
                "error_detail": exc.message,
                "path": request.url.path,
                "status_code": exc.status_code,
            },
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": type(exc).__name__,
                "message": exc.message,
                "path": request.url.path,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle Pydantic request validation errors (422 Unprocessable Entity).

        Returns the full list of validation failures so clients can display
        precise field-level error messages.
        """
        logger.warning(
            "Request validation failed",
            extra={"path": request.url.path, "errors": exc.errors()},
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "ValidationError",
                "message": "Request validation failed.",
                "path": request.url.path,
                "detail": exc.errors(),
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """Handle standard HTTP exceptions (e.g. 404, 405, 401)."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTPException",
                "message": exc.detail,
                "path": request.url.path,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Catch-all handler for unexpected server errors (500).

        Logs the full traceback but returns a safe, opaque error message
        to the client to avoid leaking implementation details.
        """
        logger.exception(
            "Unhandled exception",
            extra={"path": request.url.path},
            exc_info=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred. Please try again later.",
                "path": request.url.path,
            },
        )
