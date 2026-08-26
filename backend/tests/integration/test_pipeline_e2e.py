"""
End-to-End Pipeline Integration Test.
"""

import io
import time
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_end_to_end_ingestion_and_search(client: AsyncClient):
    """Full cycle test: Upload document -> verify record -> search for indexed chunks."""
    unique_keyword = f"Stream2VecUniqueTag_{int(time.time())}"
    doc_content = (
        f"Stream2Vec Enterprise Knowledge Base.\n"
        f"This document contains a special identifier {unique_keyword} for end-to-end verification.\n"
        f"Apache Spark processes this text stream and indexes vectors into Qdrant."
    ).encode("utf-8")

    files = {
        "file": ("e2e_verification.txt", io.BytesIO(doc_content), "text/plain")
    }

    # 1. Upload
    upload_res = await client.post("/api/v1/documents", files=files)
    assert upload_res.status_code == 201
    doc_id = upload_res.json()["id"]

    # 2. Check document initially recorded
    get_res = await client.get(f"/api/v1/documents/{doc_id}")
    assert get_res.status_code == 200
    assert get_res.json()["filename"] == "e2e_verification.txt"

    # 3. Perform a semantic search query
    search_payload = {
        "query": f"{unique_keyword} Enterprise Knowledge Base",
        "top_k": 5,
        "score_threshold": 0.0,
    }
    search_res = await client.post("/api/v1/search", json=search_payload)
    assert search_res.status_code == 200
    assert "hits" in search_res.json()
