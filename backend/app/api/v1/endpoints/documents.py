"""
Documents API Endpoints — v1

Routes:
    POST   /api/v1/documents           Upload a new document (multipart/form-data)
    GET    /api/v1/documents           List documents (paginated)
    GET    /api/v1/documents/{id}      Get a single document by ID
"""

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from app.dependencies.common import DBSessionDep
from app.exceptions.handlers import DocumentNotFoundException
from app.messaging.kafka_client import KafkaProducerClient, get_kafka_producer
from app.models.document import DocumentStatus
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentList, DocumentResponse, DocumentSummary
from app.services.document_service import DocumentService
from app.storage.minio_client import MinIOClient, get_minio_client

router = APIRouter()

# ---------------------------------------------------------------------------
# Dependency helpers
# ---------------------------------------------------------------------------

def get_document_service(
    minio: Annotated[MinIOClient, Depends(get_minio_client)],
    kafka: Annotated[KafkaProducerClient, Depends(get_kafka_producer)],
) -> DocumentService:
    """Construct DocumentService with its dependencies."""
    return DocumentService(
        document_repo=DocumentRepository(),
        minio=minio,
        kafka=kafka,
    )


DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document",
    description=(
        "Accepts a multipart file upload. The file is stored in MinIO, "
        "a Document record is created in PostgreSQL (status=PENDING), "
        "and a Kafka event is published so Spark picks it up for processing."
    ),
)
async def upload_document(
    session: DBSessionDep,
    service: DocumentServiceDep,
    file: UploadFile = File(..., description="The file to ingest."),
) -> DocumentResponse:
    """POST /api/v1/documents — upload a file for processing."""
    doc = await service.upload_document(session, file)
    await session.commit()
    return DocumentResponse.model_validate(doc)


@router.get(
    "",
    response_model=DocumentList,
    summary="List documents",
    description="Returns a paginated list of all documents, optionally filtered by status.",
)
async def list_documents(
    session: DBSessionDep,
    service: DocumentServiceDep,
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)."),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page."),
    status: Optional[DocumentStatus] = Query(
        default=None,
        description="Filter by processing status.",
    ),
) -> DocumentList:
    """GET /api/v1/documents — list documents with pagination."""
    items, total = await service.list_documents(
        session, page=page, page_size=page_size, status=status
    )
    return DocumentList(
        items=[DocumentSummary.model_validate(doc) for doc in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Get a document",
    description="Returns the full document record including processing status.",
)
async def get_document(
    document_id: uuid.UUID,
    session: DBSessionDep,
    service: DocumentServiceDep,
) -> DocumentResponse:
    """GET /api/v1/documents/{document_id} — fetch a single document."""
    doc = await service.get_document(session, document_id)
    if doc is None:
        raise DocumentNotFoundException(str(document_id))
    return DocumentResponse.model_validate(doc)
