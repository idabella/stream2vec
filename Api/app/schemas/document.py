"""
Stream2Vec — Document Pydantic Schemas.

Defines request and response models for the Document API.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    """Shared document fields."""
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type")


class DocumentCreate(DocumentBase):
    """Schema for creating a document."""
    file_size: int = Field(..., gt=0, description="File size in bytes")
    minio_path: str = Field(..., description="MinIO storage path")


class DocumentResponse(DocumentBase):
    """Schema for document API responses."""
    id: uuid.UUID
    file_size: int
    minio_path: str
    status: str
    title: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    """Schema for paginated document list."""
    data: list[DocumentResponse]
    total: int
    skip: int
    limit: int
