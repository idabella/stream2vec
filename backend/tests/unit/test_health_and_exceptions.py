"""
Unit Tests for Health Endpoint and Exception Handlers.
"""

import pytest
from httpx import AsyncClient

from app.exceptions.handlers import (
    DocumentNotFoundException,
    MessagingException,
    StorageException,
    VectorStoreException,
)


def test_custom_exception_properties():
    """Verify status codes and messages on custom domain exceptions."""
    exc1 = DocumentNotFoundException("doc-123")
    assert exc1.status_code == 404
    assert "doc-123" in exc1.message

    exc2 = StorageException("MinIO S3 connection refused")
    assert exc2.status_code == 503
    assert "Storage error" in exc2.message

    exc3 = MessagingException("Kafka broker unreachable")
    assert exc3.status_code == 503

    exc4 = VectorStoreException("Qdrant collection not found")
    assert exc4.status_code == 503


@pytest.mark.asyncio
async def test_health_check_endpoint(client: AsyncClient):
    """Test /health endpoint response structure."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "service" in data
    assert data["service"] == "Stream2Vec"
    assert "dependencies" in data
    assert "postgres" in data["dependencies"]
    assert "minio" in data["dependencies"]
    assert "kafka" in data["dependencies"]
    assert "qdrant" in data["dependencies"]
