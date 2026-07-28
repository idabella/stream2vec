"""
Stream2Vec — Search Pydantic Schemas.
"""

import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """Single search result item."""
    chunk_id: uuid.UUID = Field(..., description="Chunk identifier")
    document_id: uuid.UUID = Field(..., description="Parent document identifier")
    content: str = Field(..., description="Chunk text content")
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class SearchResponse(BaseModel):
    """Search response with ranked results."""
    query: str = Field(..., description="Original search query")
    results: List[SearchResult] = Field(default_factory=list)
    total: int = Field(..., description="Total number of results")
    took_ms: Optional[float] = Field(None, description="Query execution time in milliseconds")
