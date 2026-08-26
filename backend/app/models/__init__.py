"""
Models Package — SQLAlchemy ORM models.

All models inherit from app.database.session.Base.
Importing them here ensures Alembic's autogenerate discovers every table.
"""

from app.models.document import Document, DocumentStatus  # noqa: F401
from app.models.processing_job import JobStatus, ProcessingJob  # noqa: F401

__all__ = ["Document", "DocumentStatus", "ProcessingJob", "JobStatus"]
