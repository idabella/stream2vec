"""
RAGService — Retrieval-Augmented Generation with Google Gemini.

RAG flow:
    1. Embed the query with sentence-transformers.
    2. Retrieve top-k relevant chunks from Qdrant (via SearchService).
    3. Build a context prompt from the retrieved chunks.
    4. Call Google Gemini API to generate a natural-language answer.
    5. Return the answer + source chunks used.
"""

import logging
import time

from google import genai
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.repositories.document_repository import DocumentRepository
from app.schemas.rag import RAGRequest, RAGResponse
from app.schemas.search import SearchRequest
from app.services.search_service import SearchService
from app.storage.qdrant_client import QdrantClientWrapper

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Gemini client — lazy singleton
# ---------------------------------------------------------------------------
_gemini_client = None


def _get_gemini_client():
    """Initialise and cache the Gemini client."""
    global _gemini_client
    if _gemini_client is None:
        settings = get_settings()
        api_key = settings.gemini.api_key
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set. Add it to your .env file."
            )
        _gemini_client = genai.Client(api_key=api_key)
        logger.info("Gemini client initialised")
    return _gemini_client


# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """You are a precise document assistant.
Answer the user's question using ONLY the context provided below.
If the answer is not found in the context, say "I could not find this information in the indexed documents."
Be concise, factual, and helpful. If the answer contains structured data (phone, email, dates), present it clearly.

Context extracted from indexed documents:
{context}

User question: {query}

Answer:"""


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class RAGService:
    """Orchestrates retrieval from Qdrant and generation via Gemini."""

    def __init__(
        self,
        document_repo: DocumentRepository,
        qdrant: QdrantClientWrapper,
    ) -> None:
        self._search_service = SearchService(
            document_repo=document_repo,
            qdrant=qdrant,
        )

    async def chat(
        self,
        session: AsyncSession,
        request: RAGRequest,
    ) -> RAGResponse:
        """Run RAG: retrieve relevant chunks, then generate an answer.

        Args:
            session: Async SQLAlchemy session.
            request: Validated RAGRequest payload.

        Returns:
            RAGResponse with generated answer and source chunks.
        """
        t0 = time.perf_counter()

        # 1. Retrieve relevant chunks via vector search
        search_req = SearchRequest(
            query=request.query,
            top_k=request.top_k,
            score_threshold=request.score_threshold,
        )
        search_resp = await self._search_service.search(session, search_req)

        if not search_resp.hits:
            elapsed = round((time.perf_counter() - t0) * 1000, 2)
            return RAGResponse(
                query=request.query,
                answer="I could not find any relevant information in the indexed documents for your query.",
                sources=[],
                total_sources=0,
                processing_time_ms=elapsed,
            )

        # 2. Build context from retrieved chunks
        context_parts = []
        for i, hit in enumerate(search_resp.hits, 1):
            context_parts.append(
                f"[Source {i} — {hit.filename}, chunk {hit.chunk_index}, score {hit.score:.3f}]\n{hit.text}"
            )
        context = "\n\n".join(context_parts)

        # 3. Build final prompt
        prompt = _SYSTEM_PROMPT.format(context=context, query=request.query)

        # 4. Call Gemini
        try:
            client = _get_gemini_client()
            response = client.models.generate_content(
                model=get_settings().gemini.model,
                contents=prompt,
            )
            answer = response.text.strip()
            logger.info("Gemini generated answer (%d chars)", len(answer))
        except Exception as exc:
            logger.error("Gemini generation failed: %s", exc)
            answer = f"Generation error: {exc}"

        elapsed = round((time.perf_counter() - t0) * 1000, 2)

        return RAGResponse(
            query=request.query,
            answer=answer,
            sources=search_resp.hits,
            total_sources=len(search_resp.hits),
            processing_time_ms=elapsed,
        )
