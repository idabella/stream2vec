"""
Stream2Vec — Chunk ORM Model.

Represents a text chunk extracted from a document.
Each chunk is independently vectorized and stored in Qdrant.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database.base import Base


class Chunk(Base):
    """Chunk model — represents a text segment of a document."""

    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique chunk identifier",
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        doc="Reference to the parent document",
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Raw text content of the chunk",
    )
    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Position of this chunk within the document (0-indexed)",
    )
    qdrant_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        doc="Corresponding Qdrant point ID",
    )
    token_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="Number of tokens in this chunk",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        doc="Chunk creation timestamp",
    )

    def __repr__(self) -> str:
        return f"<Chunk id={self.id} document_id={self.document_id} index={self.chunk_index}>"
