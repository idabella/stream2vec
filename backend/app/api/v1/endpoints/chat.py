"""
Chat (RAG) API Endpoint — v1

Routes:
    POST   /api/v1/chat    Ask a question answered from indexed documents via Gemini RAG
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies.common import DBSessionDep
from app.repositories.document_repository import DocumentRepository
from app.schemas.rag import RAGRequest, RAGResponse
from app.services.rag_service import RAGService
from app.storage.qdrant_client import QdrantClientWrapper, get_qdrant_client

router = APIRouter()


# ---------------------------------------------------------------------------
# Dependency helpers
# ---------------------------------------------------------------------------


def get_rag_service(
    qdrant: Annotated[QdrantClientWrapper, Depends(get_qdrant_client)],
) -> RAGService:
    """Construct RAGService with its dependencies."""
    return RAGService(
        document_repo=DocumentRepository(),
        qdrant=qdrant,
    )


RAGServiceDep = Annotated[RAGService, Depends(get_rag_service)]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.post(
    "",
    response_model=RAGResponse,
    summary="Ask a question (RAG)",
    description=(
        "Retrieves the most relevant document chunks from Qdrant using semantic search, "
        "then passes them as context to Google Gemini to generate a precise natural-language answer. "
        "Returns the generated answer plus the source chunks used."
    ),
)
async def chat(
    request: RAGRequest,
    session: DBSessionDep,
    service: RAGServiceDep,
) -> RAGResponse:
    """POST /api/v1/chat — ask a question, get an AI-generated answer from your documents."""
    return await service.chat(session, request)
