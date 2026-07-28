"""
Stream2Vec — Storage Dependency Providers.
"""

from typing import Annotated

from fastapi import Depends

from app.storage.minio.client import get_minio_client
from app.storage.minio.service import MinioService


def get_minio_service() -> MinioService:
    """Provide a MinioService instance."""
    client = get_minio_client()
    return MinioService(client)


MinioServiceDep = Annotated[MinioService, Depends(get_minio_service)]
