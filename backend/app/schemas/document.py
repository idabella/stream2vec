"""
Document Pydantic Schemas — Request/response shapes for document endpoints.

Keeps ORM models separate from API contracts (Clean Architecture).
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.document import DocumentStatus


# ── Shared base ──────────────────────────────────────────────────────────────

class DocumentBase(BaseModel):
    """Fields shared by create and response schemas."""

    filename: str = Field(..., description="Original filename of the uploaded file.")
    content_type: str = Field(
        default="application/octet-stream",
        description="MIME type of the uploaded file.",
    )


# ── Request schema ────────────────────────────────────────────────────────────

class DocumentCreate(DocumentBase):
    """Internal schema used by DocumentService after receiving the upload.

    Not used directly as a request body — the actual upload is multipart/form-data.
    This schema is constructed programmatically from the UploadFile object.
    """

    file_size: int = Field(..., ge=0, description="File size in bytes.")
    minio_path: str = Field(..., description="Path in MinIO where the file is stored.")


# ── Response schemas ──────────────────────────────────────────────────────────

class DocumentResponse(DocumentBase):
    """Full document representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    file_size: int
    minio_path: str
    status: DocumentStatus
    chunk_count: int
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class DocumentSummary(BaseModel):
    """Lightweight representation used in list responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str
    content_type: str
    status: DocumentStatus
    chunk_count: int
    created_at: datetime


class DocumentList(BaseModel):
    """Paginated list of documents."""

    items: list[DocumentSummary]
    total: int
    page: int
    page_size: int
