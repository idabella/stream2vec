"""
ProcessingJob ORM Model — Tracks the Spark processing run for a document.

One ProcessingJob is created per processing attempt. If retried,
a new job row is inserted while the previous failed one is preserved
for audit purposes.
"""

import enum
import uuid

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class JobStatus(str, enum.Enum):
    """Lifecycle states of a processing job."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingJob(Base):
    """SQLAlchemy ORM model for Spark processing jobs.

    Created when a document event is consumed by the Spark pipeline.
    Tracks per-attempt status so failed runs are auditable.
    """

    __tablename__ = "processing_jobs"

    # ── Primary key ──────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # ── Foreign key ──────────────────────────────────────────────────────────
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Status ───────────────────────────────────────────────────────────────
    status: Mapped[JobStatus] = mapped_column(
        Enum(
            JobStatus,
            name="job_status",
            create_type=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=JobStatus.QUEUED,
        index=True,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Spark job metadata ───────────────────────────────────────────────────
    # Filled in by the Spark job so operators can correlate logs
    spark_app_id: Mapped[str | None] = mapped_column(String(256), nullable=True)

    # ── Timestamps ───────────────────────────────────────────────────────────
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    started_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ── Relationship ─────────────────────────────────────────────────────────
    document: Mapped["Document"] = relationship(  # noqa: F821
        "Document",
        back_populates=None,
        lazy="raise",  # Prevent accidental N+1 in async context
    )

    def __repr__(self) -> str:
        return f"<ProcessingJob id={self.id!s} doc={self.document_id!s} status={self.status}>"
