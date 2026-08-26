"""
Integration Tests for Documents API Endpoints (/api/v1/documents).
"""

import io
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_upload_and_get_document(client: AsyncClient):
    """Test uploading a text document and retrieving its metadata."""
    file_content = b"Stream2Vec document ingestion integration test payload."
    files = {
        "file": ("test_integration_doc.txt", io.BytesIO(file_content), "text/plain")
    }

    # 1. Upload
    upload_response = await client.post("/api/v1/documents", files=files)
    assert upload_response.status_code == 201
    data = upload_response.json()
    assert "id" in data
    assert data["filename"] == "test_integration_doc.txt"
    assert data["file_size"] == len(file_content)
    assert data["status"] in ["pending", "processing", "completed"]

    doc_id = data["id"]

    # 2. Get by ID
    get_response = await client.get(f"/api/v1/documents/{doc_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["id"] == doc_id
    assert get_data["filename"] == "test_integration_doc.txt"


@pytest.mark.asyncio
async def test_list_documents(client: AsyncClient):
    """Test listing documents with pagination."""
    response = await client.get("/api/v1/documents?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert data["page"] == 1
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_get_nonexistent_document(client: AsyncClient):
    """Test 404 response for non-existent document UUID."""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/api/v1/documents/{fake_uuid}")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert "DocumentNotFoundException" in data["error"]
