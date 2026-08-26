"""
Unit Tests for Pydantic API Schemas.
"""

import uuid
import pytest
from pydantic import ValidationError

from app.schemas.document import DocumentCreate
from app.schemas.search import SearchRequest
from app.schemas.rag import RAGRequest


def test_document_create_schema():
    """Test valid and invalid DocumentCreate schema instantiation."""
    doc_data = {
        "filename": "pipeline_guide.md",
        "content_type": "text/markdown",
        "file_size": 1024,
        "minio_path": "documents/123/pipeline_guide.md",
    }
    doc = DocumentCreate(**doc_data)
    assert doc.filename == "pipeline_guide.md"
    assert doc.file_size == 1024

    with pytest.raises(ValidationError):
        DocumentCreate(filename="bad.txt", file_size=-10, minio_path="doc/bad.txt")


def test_search_request_schema():
    """Test SearchRequest defaults and constraints."""
    req = SearchRequest(query="machine learning pipeline")
    assert req.top_k == 10
    assert req.score_threshold == 0.0
    assert req.document_ids is None

    custom_id = uuid.uuid4()
    req2 = SearchRequest(
        query="spark streaming",
        top_k=5,
        score_threshold=0.75,
        document_ids=[custom_id],
    )
    assert req2.top_k == 5
    assert req2.score_threshold == 0.75
    assert req2.document_ids == [custom_id]

    with pytest.raises(ValidationError):
        SearchRequest(query="")


def test_rag_request_schema():
    """Test RAGRequest defaults and validation."""
    rag_req = RAGRequest(query="What is Stream2Vec?")
    assert rag_req.top_k == 5
    assert rag_req.score_threshold == 0.3

    with pytest.raises(ValidationError):
        RAGRequest(query="")
