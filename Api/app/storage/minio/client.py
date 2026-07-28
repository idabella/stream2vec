"""
Stream2Vec — MinIO Client Factory.

Provides a configured MinIO client instance.
"""

from minio import Minio

from app.core.config import settings


def get_minio_client() -> Minio:
    """Create and return a configured MinIO client.
    
    Returns:
        Minio: Configured MinIO client instance.
    """
    return Minio(
        endpoint=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE,
    )
