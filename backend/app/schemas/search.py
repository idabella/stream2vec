"""
Search Pydantic Schemas — Request/response shapes for the semantic search endpoint.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Request ───────────────────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    """Semantic search query payload."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=2048,
        description="Natural-language query to embed and search.",
    )
    top_k: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of results to return.",
    )
    score_threshold: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Minimum cosine-similarity score; results below are dropped.",
    )
    document_ids: Optional[list[uuid.UUID]] = Field(
        default=None,
        description="Restrict search to these document IDs (optional).",
    )


# ── Response ──────────────────────────────────────────────────────────────────

class SearchHit(BaseModel):
    """A single result from the Qdrant vector search, enriched with document metadata."""

    chunk_id: str = Field(..., description="Qdrant point ID for this chunk.")
    document_id: uuid.UUID = Field(..., description="Parent document UUID.")
    filename: str = Field(..., description="Original filename of the parent document.")
    score: float = Field(..., description="Cosine-similarity score (0–1).")
    chunk_index: int = Field(..., description="Position of this chunk in the document.")
    text: str = Field(..., description="The raw text of this chunk.")
    created_at: datetime = Field(..., description="When the parent document was created.")


class SearchResponse(BaseModel):
    """Full response for a semantic search query."""

    query: str = Field(..., description="The original query string.")
    hits: list[SearchHit] = Field(default_factory=list)
    total: int = Field(..., description="Total number of matching hits returned.")
    processing_time_ms: float = Field(
        ...,
        description="Time spent on embedding + Qdrant query (milliseconds).",
    )
