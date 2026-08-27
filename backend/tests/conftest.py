"""
Pytest Configuration and Shared Fixtures for Stream2Vec.
"""

from __future__ import annotations

from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.messaging.kafka_client import KafkaProducerClient
from app.storage.minio_client import MinIOClient
from app.storage.qdrant_client import QdrantClientWrapper


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Asynchronous HTTP test client for FastAPI with mocked external services.
    
    Mocks all external service connections (PostgreSQL, MinIO, Kafka, Qdrant)
    to allow unit tests to run in isolation without requiring running services.
    """
    # Mock database engine before importing app/lifespan
    mock_engine = MagicMock()
    mock_conn = AsyncMock()
    mock_engine.connect.return_value.__aenter__.return_value = mock_conn
    mock_engine.connect.return_value.__aexit__.return_value = None
    mock_conn.execute = AsyncMock(return_value=None)
    mock_engine.dispose = AsyncMock(return_value=None)

    with patch("app.database.session.engine", mock_engine), \
         patch("app.storage.minio_client.init_minio_client"), \
         patch("app.messaging.kafka_client.init_kafka_producer", new_callable=AsyncMock), \
         patch("app.storage.qdrant_client.init_qdrant_client"), \
         patch("app.messaging.kafka_client.shutdown_kafka_producer", new_callable=AsyncMock):
        
        # Import app and lifespan after mocks are in place
        from main import app, lifespan
        
        async with lifespan(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
                yield ac


@pytest.fixture
def mock_minio() -> MagicMock:
    """Mock MinIO client for isolated unit testing."""
    mock = MagicMock(spec=MinIOClient)
    mock.ping.return_value = True
    mock.upload_file = AsyncMock(return_value="documents/test-uuid/sample.txt")
    mock.download_file = AsyncMock(return_value=b"Sample document content for unit testing.")
    mock.delete_file = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def mock_kafka() -> MagicMock:
    """Mock Kafka producer client for isolated unit testing."""
    mock = MagicMock(spec=KafkaProducerClient)
    mock.ping = AsyncMock(return_value=True)
    mock.publish_document_event = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def mock_qdrant() -> MagicMock:
    """Mock Qdrant client wrapper for isolated unit testing."""
    mock = MagicMock(spec=QdrantClientWrapper)
    mock.ping.return_value = True
    mock._collection = "documents"
    mock._client = MagicMock()
    return mock


@pytest.fixture
def sample_text() -> str:
    """Sample document text fixture for testing processing steps."""
    return (
        "Stream2Vec is a cloud-native platform for document ingestion and vectorization.\n"
        "It uses Apache Spark Structured Streaming to process documents in real-time.\n"
        "Vector embeddings are indexed into Qdrant for low-latency semantic search.\n"
        "Retrieval-Augmented Generation (RAG) queries use Google Gemini."
    )
