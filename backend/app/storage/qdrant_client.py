"""
Qdrant Client — Vector database interface for Stream2Vec.

Wraps the Qdrant Python SDK to provide:
- Collection initialization on startup
- Connectivity health check
- Vector upsert / search (stubs ready for Phase 4)

The client is initialized once at application startup (lifespan) and
exposed via FastAPI dependency injection.
"""

import logging

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Embedding dimension for sentence-transformers/all-MiniLM-L6-v2
# Update this constant when changing the embedding model.
DEFAULT_VECTOR_SIZE = 384


class QdrantClientWrapper:
    """Thin wrapper around the Qdrant SDK client.

    Initialized once at startup via ``ensure_collection()``.
    Injected into route handlers via ``Depends(get_qdrant_client)``.
    """

    def __init__(self) -> None:
        """Initialize the Qdrant SDK client with settings from the environment."""
        self._client = QdrantClient(
            host=settings.qdrant.host,
            port=settings.qdrant.port,
            api_key=settings.qdrant.api_key or None,
            # Prefer gRPC for upsert/search performance; HTTP for management
            prefer_grpc=False,
        )
        self._collection = settings.qdrant.collection_documents
        logger.info(
            "QdrantClient initialized",
            extra={
                "host": settings.qdrant.host,
                "port": settings.qdrant.port,
                "collection": self._collection,
            },
        )

    def ensure_collection(self, vector_size: int = DEFAULT_VECTOR_SIZE) -> None:
        """Create the documents collection if it does not already exist.

        Args:
            vector_size: Dimensionality of the embedding vectors.
                         Defaults to 384 (all-MiniLM-L6-v2).

        Raises:
            Exception: If the collection cannot be created.
        """
        try:
            existing = [c.name for c in self._client.get_collections().collections]
            if self._collection not in existing:
                self._client.create_collection(
                    collection_name=self._collection,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(
                    "Qdrant collection created",
                    extra={"collection": self._collection, "vector_size": vector_size},
                )
            else:
                logger.info(
                    "Qdrant collection exists",
                    extra={"collection": self._collection},
                )
        except Exception as exc:
            logger.error(
                "Failed to ensure Qdrant collection",
                extra={"collection": self._collection, "error": str(exc)},
            )
            raise

    def ping(self) -> bool:
        """Check connectivity to Qdrant by fetching collections.

        Returns:
            bool: True if Qdrant is reachable, False otherwise.
        """
        try:
            self._client.get_collections()
            return True
        except Exception as exc:
            logger.warning("Qdrant ping failed", extra={"error": str(exc)})
            return False


# ---------------------------------------------------------------------------
# Singleton instance — initialized at startup
# ---------------------------------------------------------------------------
_qdrant_client: QdrantClientWrapper | None = None


def get_qdrant_client() -> QdrantClientWrapper:
    """FastAPI dependency — return the application-level Qdrant client.

    Raises:
        RuntimeError: If called before the client has been initialized
                      during application startup.
    """
    if _qdrant_client is None:
        raise RuntimeError(
            "QdrantClientWrapper has not been initialized. Check application startup."
        )
    return _qdrant_client


def init_qdrant_client() -> QdrantClientWrapper:
    """Initialize and return the singleton Qdrant client.

    Called once from the FastAPI lifespan handler.
    """
    global _qdrant_client
    _qdrant_client = QdrantClientWrapper()
    _qdrant_client.ensure_collection()
    return _qdrant_client
