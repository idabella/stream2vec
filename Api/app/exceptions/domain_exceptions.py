"""
Stream2Vec — Domain Exception Classes.

Business logic exceptions (non-HTTP layer).
"""


class Stream2VecException(Exception):
    """Base exception for all Stream2Vec domain errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class DocumentProcessingError(Stream2VecException):
    """Raised when document processing fails."""
    pass


class StorageError(Stream2VecException):
    """Raised when object storage operations fail."""
    pass


class MessagingError(Stream2VecException):
    """Raised when Kafka operations fail."""
    pass


class EmbeddingError(Stream2VecException):
    """Raised when vector embedding generation fails."""
    pass


class VectorStoreError(Stream2VecException):
    """Raised when Qdrant operations fail."""
    pass
