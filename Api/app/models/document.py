"""
Stream2Vec — Document ORM Model.

Represents an uploaded document in the system.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database.base import Base


class Document(Base):
    """Document model — represents an uploaded document."""

    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique document identifier",
    )
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Original filename",
    )
    content_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="MIME type of the document",
    )
    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="File size in bytes",
    )
    minio_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        doc="Path to the file in MinIO storage",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        doc="Processing status: pending, processing, completed, failed",
    )
    title: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        doc="Extracted document title",
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Document description or summary",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        doc="Document creation timestamp",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        doc="Last update timestamp",
    )

    def __repr__(self) -> str:
        return f"<Document id={self.id} filename={self.filename} status={self.status}>"
