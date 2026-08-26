"""
Repositories Package — Data access layer.

Implements the Repository pattern for abstracting database operations.
Repositories encapsulate all CRUD logic and return domain objects.
"""

from app.repositories.document_repository import DocumentRepository
from app.repositories.processing_job_repository import ProcessingJobRepository

__all__ = [
    "DocumentRepository",
    "ProcessingJobRepository",
]
