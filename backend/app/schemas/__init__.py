"""
Schemas Package — Pydantic request/response schemas.

Defines the data shapes for API input validation and output serialization.
Schemas are separate from ORM models (Clean Architecture).
"""

from app.schemas.document import (
    DocumentBase,
    DocumentCreate,
    DocumentList,
    DocumentResponse,
    DocumentSummary,
)
from app.schemas.search import SearchHit, SearchRequest, SearchResponse

__all__ = [
    "DocumentBase",
    "DocumentCreate",
    "DocumentList",
    "DocumentResponse",
    "DocumentSummary",
    "SearchHit",
    "SearchRequest",
    "SearchResponse",
]
