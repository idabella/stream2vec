"""
Unit Tests for Spark Text Chunker.
"""

from chunkers.text_chunker import chunk_text, chunk_text_to_dicts, TextChunk


def test_chunk_text_empty():
    """Test chunking on empty input."""
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_chunk_text_single_chunk():
    """Test short text producing a single chunk."""
    text = "Stream2Vec is a streaming vectorization platform. It uses Spark and Qdrant."
    chunks = chunk_text(text, max_chars=500, overlap_chars=50)
    assert len(chunks) == 1
    assert isinstance(chunks[0], TextChunk)
    assert chunks[0].chunk_index == 0
    assert "Stream2Vec" in chunks[0].text
    assert chunks[0].char_start == 0


def test_chunk_text_multiple_overlapping_chunks():
    """Test long text split into multiple overlapping chunks."""
    sentences = [
        "First sentence discussing architectural foundations of Stream2Vec.",
        "Second sentence describing Kafka event streaming mechanisms.",
        "Third sentence on Apache Spark structured streaming transformations.",
        "Fourth sentence detailing SentenceTransformer vector embedding.",
        "Fifth sentence highlighting Qdrant vector database storage.",
        "Sixth sentence discussing Airflow orchestration DAGs.",
    ]
    text = " ".join(sentences)
    chunks = chunk_text(text, max_chars=120, overlap_chars=30)
    assert len(chunks) > 1
    for i, c in enumerate(chunks):
        assert c.chunk_index == i
        assert len(c.text) <= 150  # sentence bounded
        assert len(c.text) > 0


def test_chunk_text_to_dicts():
    """Test serialization to Spark-compatible dictionaries."""
    text = "Sentence one. Sentence two. Sentence three."
    dict_chunks = chunk_text_to_dicts(text, max_chars=50, overlap_chars=10)
    assert isinstance(dict_chunks, list)
    assert len(dict_chunks) >= 1
    assert "text" in dict_chunks[0]
    assert "chunk_index" in dict_chunks[0]
    assert "char_start" in dict_chunks[0]
    assert "char_end" in dict_chunks[0]
