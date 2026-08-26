"""
Search API Endpoint — v1

Routes:
    POST   /api/v1/search    Semantic search across indexed document chunks
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies.common import DBSessionDep
from app.repositories.document_repository import DocumentRepository
from app.schemas.search import SearchRequest, SearchResponse
from app.services.search_service import SearchService
from app.storage.qdrant_client import QdrantClientWrapper, get_qdrant_client

router = APIRouter()

# ---------------------------------------------------------------------------
# Dependency helpers
# ---------------------------------------------------------------------------

def get_search_service(
    qdrant: Annotated[QdrantClientWrapper, Depends(get_qdrant_client)],
) -> SearchService:
    """Construct SearchService with its dependencies."""
    return SearchService(
        document_repo=DocumentRepository(),
        qdrant=qdrant,
    )


SearchServiceDep = Annotated[SearchService, Depends(get_search_service)]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=SearchResponse,
    summary="Semantic search",
    description=(
        "Embeds the query with sentence-transformers (all-MiniLM-L6-v2) and "
        "retrieves the nearest vector neighbours from Qdrant. Results are enriched "
        "with document metadata from PostgreSQL."
    ),
)
async def semantic_search(
    request: SearchRequest,
    session: DBSessionDep,
    service: SearchServiceDep,
) -> SearchResponse:
    """POST /api/v1/search — run a semantic search query."""
    return await service.search(session, request)
