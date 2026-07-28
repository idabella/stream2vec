"""
Stream2Vec — ProcessingJob ORM Model.

Tracks the async processing pipeline state for each document.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database.base import Base


class ProcessingJob(Base):
    """ProcessingJob model — tracks document pipeline execution."""

    __tablename__ = "processing_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique job identifier",
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        doc="Reference to the associated document",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="queued",
        doc="Job status: queued, extracting, cleaning, chunking, embedding, completed, failed",
    )
    pipeline_stage: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        doc="Current pipeline stage",
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Error message if job failed",
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Job start timestamp",
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Job completion timestamp",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        doc="Job creation timestamp",
    )

    def __repr__(self) -> str:
        return f"<ProcessingJob id={self.id} document_id={self.document_id} status={self.status}>"
