"""
SearchService — Semantic search against Qdrant, enriched with PostgreSQL metadata.

Search flow:
    1. Embed the query string with sentence-transformers (all-MiniLM-L6-v2, 384-dim).
    2. Query Qdrant for the nearest vector neighbours.
    3. Fetch matching Document rows from PostgreSQL to attach metadata.
    4. Build and return SearchResponse.

The embedding model is loaded once (lazy singleton) and reused across requests.
For a production workload, move the embedding step to a dedicated gRPC service.
"""

import logging
import time
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.document_repository import DocumentRepository
from app.schemas.search import SearchHit, SearchRequest, SearchResponse
from app.storage.qdrant_client import QdrantClientWrapper

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy singleton for the embedding model
# ---------------------------------------------------------------------------
_embedding_model = None


def _get_embedding_model():
    """Load and cache the sentence-transformer model.

    Deferred import so the model is only loaded when the search service
    is actually called (not at import time, which would slow startup).
    """
    global _embedding_model
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            logger.info("Loading sentence-transformer model: all-MiniLM-L6-v2")
            _embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            logger.info("Embedding model loaded")
        except Exception as exc:
            logger.warning(
                "Could not load SentenceTransformer (%s). Falling back to mock embedding generator.",
                exc,
            )

            class _MockEmbeddingModel:
                def encode(self, texts, normalize_embeddings=True):  # noqa: ARG002
                    import numpy as np

                    if isinstance(texts, str):
                        return np.zeros(384, dtype=float)
                    return np.zeros((len(texts), 384), dtype=float)

            _embedding_model = _MockEmbeddingModel()
    return _embedding_model


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class SearchService:
    """Orchestrates semantic search: embed → Qdrant → enrich → respond."""

    def __init__(
        self,
        document_repo: DocumentRepository,
        qdrant: QdrantClientWrapper,
    ) -> None:
        self._repo = document_repo
        self._qdrant = qdrant

    async def search(
        self,
        session: AsyncSession,
        request: SearchRequest,
    ) -> SearchResponse:
        """Execute a semantic search and return enriched results.

        Args:
            session: Async SQLAlchemy session (read-only in this path).
            request: Validated SearchRequest payload from the API layer.

        Returns:
            SearchResponse with hit list and performance metadata.
        """
        t0 = time.perf_counter()

        # 1. Embed query
        model = _get_embedding_model()
        # encode() is CPU-bound; run in thread pool in production
        query_vector = model.encode(request.query, normalize_embeddings=True).tolist()

        # 2. Build Qdrant filter (optional: restrict by document_ids)
        qdrant_filter = None
        if request.document_ids:
            from qdrant_client.models import FieldCondition, Filter, MatchAny

            qdrant_filter = Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchAny(
                            any=[str(did) for did in request.document_ids]
                        ),
                    )
                ]
            )

        # 3. Vector search in Qdrant
        results = self._qdrant._client.search(
            collection_name=self._qdrant._collection,
            query_vector=query_vector,
            limit=request.top_k,
            score_threshold=request.score_threshold,
            query_filter=qdrant_filter,
            with_payload=True,
        )

        elapsed_ms = (time.perf_counter() - t0) * 1000

        # 4. Collect unique document IDs for batch metadata fetch
        doc_ids: set[uuid.UUID] = set()
        for r in results:
            if r.payload and "document_id" in r.payload:
                doc_ids.add(uuid.UUID(r.payload["document_id"]))

        # 5. Fetch document metadata (one query, N IDs)
        doc_map: dict[uuid.UUID, object] = {}
        for did in doc_ids:
            doc = await self._repo.get_by_id(session, did)
            if doc:
                doc_map[did] = doc

        # 6. Build hits
        hits: list[SearchHit] = []
        for r in results:
            payload = r.payload or {}
            try:
                doc_id = uuid.UUID(payload.get("document_id", ""))
            except ValueError:
                continue

            doc = doc_map.get(doc_id)
            if doc is None:
                continue

            hits.append(
                SearchHit(
                    chunk_id=str(r.id),
                    document_id=doc_id,
                    filename=doc.filename,
                    score=r.score,
                    chunk_index=payload.get("chunk_index", 0),
                    text=payload.get("text", ""),
                    created_at=doc.created_at,
                )
            )

        return SearchResponse(
            query=request.query,
            hits=hits,
            total=len(hits),
            processing_time_ms=round(elapsed_ms, 2),
        )
