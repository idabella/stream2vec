"""
Integration Tests for RAG Chat API Endpoint (/api/v1/chat).
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_chat_endpoint_structure(client: AsyncClient):
    """Test RAG chat endpoint response contract."""
    payload = {
        "query": "How does Stream2Vec ingest files?",
        "top_k": 3,
        "score_threshold": 0.0,
    }
    response = await client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert data["query"] == payload["query"]
    assert "answer" in data
    assert isinstance(data["answer"], str)
    assert "sources" in data
    assert isinstance(data["sources"], list)
    assert "processing_time_ms" in data


@pytest.mark.asyncio
async def test_chat_endpoint_validation_error(client: AsyncClient):
    """Test 422 error on empty query."""
    payload = {"query": ""}
    response = await client.post("/api/v1/chat", json=payload)
    assert response.status_code == 422
