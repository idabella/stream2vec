"""
Stream2Vec — HTTP Exception Handlers.

Custom HTTP exceptions with standardized error responses.
"""

from fastapi import HTTPException, status


class DocumentNotFoundException(HTTPException):
    """Raised when a document is not found."""

    def __init__(self, document_id: str) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found.",
        )


class UnsupportedFileTypeException(HTTPException):
    """Raised when an unsupported file type is uploaded."""

    def __init__(self, content_type: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{content_type}' is not supported.",
        )


class FileTooLargeException(HTTPException):
    """Raised when an uploaded file exceeds the size limit."""

    def __init__(self, max_size_mb: int = 50) -> None:
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {max_size_mb}MB.",
        )


class StorageException(HTTPException):
    """Raised when a storage operation fails."""

    def __init__(self, message: str = "Storage operation failed.") -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message,
        )
