"""
Stream2Vec — Qdrant Client Factory.

Provides a configured Qdrant client instance.
"""

from qdrant_client import QdrantClient

from app.core.config import settings


def get_qdrant_client() -> QdrantClient:
    """Create and return a configured Qdrant client.
    
    Returns:
        QdrantClient: Configured Qdrant client instance.
    """
    return QdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
    )
