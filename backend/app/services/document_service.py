"""
DocumentService — Orchestrates the document upload use case.

Responsibilities:
    1. Upload raw file bytes to MinIO.
    2. Create a Document row in PostgreSQL via DocumentRepository.
    3. Publish a `document.uploaded` event to Kafka so Spark picks it up.

This service is intentionally kept thin: no business logic lives here
beyond orchestration. Validation happens in the API layer (schemas).
"""

import logging
import uuid
from typing import Optional

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.messaging.kafka_client import KafkaProducerClient
from app.models.document import Document, DocumentStatus
from app.repositories.document_repository import DocumentRepository
from app.storage.minio_client import MinIOClient

logger = logging.getLogger(__name__)

# Kafka topic for upload events (Spark Structured Streaming subscribes here)
# Must match KAFKA_TOPIC_DOCUMENTS in .env and KAFKA_TOPIC_INPUT default in streaming_job.py
TOPIC_DOCUMENTS_UPLOADED = "documents.raw"


class DocumentService:
    """Coordinates document ingestion: MinIO → PostgreSQL → Kafka."""

    def __init__(
        self,
        document_repo: DocumentRepository,
        minio: MinIOClient,
        kafka: KafkaProducerClient,
    ) -> None:
        self._repo = document_repo
        self._minio = minio
        self._kafka = kafka

    # ── Upload ────────────────────────────────────────────────────────────────

    async def upload_document(
        self,
        session: AsyncSession,
        file: UploadFile,
    ) -> Document:
        """Process an incoming multipart file upload end-to-end.

        Steps:
            1. Read file bytes from the request stream.
            2. Derive a stable MinIO object path: ``documents/{uuid}/{filename}``.
            3. Upload bytes to MinIO.
            4. Insert a Document row (status=PENDING) in PostgreSQL.
            5. Publish a `document.uploaded` Kafka event.
            6. Commit the transaction (session is managed by the caller/dependency).

        Args:
            session: Async SQLAlchemy session (injected, NOT committed here).
            file:    The FastAPI ``UploadFile`` from the multipart request.

        Returns:
            The newly created (and flushed) Document ORM instance.
        """
        # 1. Read bytes
        data = await file.read()
        file_size = len(data)
        doc_uuid = uuid.uuid4()

        # 2. Derive storage path
        safe_filename = file.filename or "unknown"
        minio_path = f"documents/{doc_uuid}/{safe_filename}"

        # 3. Upload to MinIO
        await self._minio.upload_file(
            data=data,
            object_name=minio_path,
            content_type=file.content_type or "application/octet-stream",
        )
        logger.info("File stored in MinIO", extra={"path": minio_path, "size": file_size})

        # 4. Persist to PostgreSQL (flushed inside create(), not yet committed)
        doc = await self._repo.create(
            session,
            id=doc_uuid,
            filename=safe_filename,
            content_type=file.content_type or "application/octet-stream",
            file_size=file_size,
            minio_path=minio_path,
        )

        # 5. Publish Kafka event (fire-and-forget from the DB transaction's
        #    perspective — Spark will read it and update the job status)
        await self._kafka.publish_document_event(
            document_id=str(doc.id),
            payload={
                "event": "document.uploaded",
                "document_id": str(doc.id),
                "filename": doc.filename,
                "content_type": doc.content_type,
                "file_size": doc.file_size,
                "minio_path": doc.minio_path,
            },
        )
        logger.info("Upload complete", extra={"document_id": str(doc.id)})
        return doc

    # ── Read helpers ──────────────────────────────────────────────────────────

    async def get_document(
        self,
        session: AsyncSession,
        document_id: uuid.UUID,
    ) -> Optional[Document]:
        """Fetch a single document by ID, or None if not found."""
        return await self._repo.get_by_id(session, document_id)

    async def list_documents(
        self,
        session: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
        status: Optional[DocumentStatus] = None,
    ) -> tuple[list[Document], int]:
        """Return a paginated list of documents and the total count."""
        return await self._repo.list(
            session, page=page, page_size=page_size, status=status
        )
