"""
Stream2Vec — Chunk Pydantic Schemas.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ChunkResponse(BaseModel):
    """Schema for chunk API responses."""
    id: uuid.UUID
    document_id: uuid.UUID
    content: str
    chunk_index: int
    qdrant_id: Optional[str] = None
    token_count: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}
