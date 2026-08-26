"""
DocumentRepository — Async CRUD operations for the Document ORM model.

Follows the Repository pattern: all SQL lives here, services stay SQL-free.
All methods accept an AsyncSession injected by the FastAPI dependency system.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentStatus


class DocumentRepository:
    """Data-access layer for the `documents` table."""

    # ── Create ────────────────────────────────────────────────────────────────

    async def create(
        self,
        session: AsyncSession,
        *,
        id: Optional[uuid.UUID] = None,
        filename: str,
        content_type: str,
        file_size: int,
        minio_path: str,
    ) -> Document:
        """Insert a new Document row and return the persisted instance."""
        doc = Document(
            id=id or uuid.uuid4(),
            filename=filename,
            content_type=content_type,
            file_size=file_size,
            minio_path=minio_path,
            status=DocumentStatus.PENDING,
        )
        session.add(doc)
        await session.flush()   # assigns `doc.id` without committing
        await session.refresh(doc)
        return doc

    # ── Read ──────────────────────────────────────────────────────────────────

    async def get_by_id(
        self,
        session: AsyncSession,
        document_id: uuid.UUID,
    ) -> Optional[Document]:
        """Fetch a single Document by primary key, or None if not found."""
        result = await session.execute(
            select(Document).where(Document.id == document_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        session: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
        status: Optional[DocumentStatus] = None,
    ) -> tuple[list[Document], int]:
        """Return a paginated list of documents and the total count.

        Returns:
            (items, total)  where ``total`` is the un-paginated count.
        """
        query = select(Document)
        count_query = select(func.count(Document.id))

        if status is not None:
            query = query.where(Document.status == status)
            count_query = count_query.where(Document.status == status)

        # total count (cheap: uses index on status)
        total_result = await session.execute(count_query)
        total = total_result.scalar_one()

        # paginated rows, newest first
        query = (
            query
            .order_by(Document.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await session.execute(query)
        return result.scalars().all(), total

    # ── Update ────────────────────────────────────────────────────────────────

    async def update_status(
        self,
        session: AsyncSession,
        document_id: uuid.UUID,
        status: DocumentStatus,
        *,
        chunk_count: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> Optional[Document]:
        """Update the processing status (and optionally chunk_count / error_message).

        Uses a single UPDATE statement for efficiency; refreshes and returns the
        updated row so callers have fresh data.
        """
        values: dict = {
            "status": status,
            "updated_at": datetime.now(tz=timezone.utc),
        }
        if chunk_count is not None:
            values["chunk_count"] = chunk_count
        if error_message is not None:
            values["error_message"] = error_message

        await session.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(**values)
        )
        return await self.get_by_id(session, document_id)

    # ── Delete ────────────────────────────────────────────────────────────────

    async def delete(
        self,
        session: AsyncSession,
        document_id: uuid.UUID,
    ) -> bool:
        """Delete a document row.  Returns True if a row was deleted."""
        doc = await self.get_by_id(session, document_id)
        if doc is None:
            return False
        await session.delete(doc)
        return True
