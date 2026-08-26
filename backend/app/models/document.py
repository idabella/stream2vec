"""
Document ORM Model — SQLAlchemy representation of an ingested document.

Each row represents one uploaded file and tracks its lifecycle:
    pending  → The document was received and queued for processing.
    processing → The Spark job is actively processing the document.
    completed → All chunks are embedded and indexed in Qdrant.
    failed   → Processing encountered a non-recoverable error.
"""

import enum
import uuid

from sqlalchemy import DateTime, Enum, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class DocumentStatus(str, enum.Enum):
    """Lifecycle states of a document in the pipeline."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(Base):
    """SQLAlchemy ORM model for ingested documents.

    Stores metadata about each uploaded file. The actual file bytes
    live in MinIO; the text chunks and vectors live in Qdrant.
    """

    __tablename__ = "documents"

    # ── Primary key ──────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # ── File metadata ────────────────────────────────────────────────────────
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    content_type: Mapped[str] = mapped_column(String(128), nullable=False, default="application/octet-stream")
    file_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # ── Storage references ───────────────────────────────────────────────────
    # Path in MinIO: "documents/{id}/{filename}"
    minio_path: Mapped[str] = mapped_column(String(1024), nullable=False)

    # ── Processing state ─────────────────────────────────────────────────────
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(
            DocumentStatus,
            name="document_status",
            create_type=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=DocumentStatus.PENDING,
        index=True,
    )
    chunk_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Timestamps ───────────────────────────────────────────────────────────
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<Document id={self.id!s} filename={self.filename!r} status={self.status}>"
