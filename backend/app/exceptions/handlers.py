"""
Exception Handlers — FastAPI exception handler registrations.

Maps custom exceptions to structured HTTP error responses.
All errors follow a consistent JSON schema.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


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


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI app.

    Args:
        app: The FastAPI application instance.
    """

    @app.exception_handler(Stream2VecException)
    async def stream2vec_exception_handler(
        request: Request, exc: Stream2VecException
    ) -> JSONResponse:
        """Handle all Stream2Vec domain exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": type(exc).__name__,
                "message": exc.message,
                "path": request.url.path,
            },
        )

    # TODO: Add handler for RequestValidationError (422)
    # TODO: Add handler for generic 500 errors
