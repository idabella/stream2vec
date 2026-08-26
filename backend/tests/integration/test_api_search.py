"""
Integration Tests for Semantic Search API Endpoint (/api/v1/search).
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_search_endpoint_valid_query(client: AsyncClient):
    """Test semantic search returns structured response with execution time."""
    payload = {
        "query": "document vectorization and retrieval",
        "top_k": 3,
        "score_threshold": 0.0,
    }
    response = await client.post("/api/v1/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert data["query"] == payload["query"]
    assert "hits" in data
    assert isinstance(data["hits"], list)
    assert "processing_time_ms" in data
    assert data["processing_time_ms"] >= 0


@pytest.mark.asyncio
async def test_search_endpoint_validation_error(client: AsyncClient):
    """Test 422 error on empty or invalid search payload."""
    payload = {"query": "", "top_k": -1}
    response = await client.post("/api/v1/search", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"] == "ValidationError"
