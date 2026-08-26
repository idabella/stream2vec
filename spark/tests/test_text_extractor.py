"""
Unit Tests for Spark Text Extractor.
"""

from extractors.text_extractor import extract_text, _extract_plain_text


def test_extract_plain_text():
    """Test extracting text from raw UTF-8 bytes."""
    data = "Hello from Stream2Vec text file.".encode("utf-8")
    result = extract_text(data, "document.txt")
    assert result == "Hello from Stream2Vec text file."


def test_extract_markdown():
    """Test extracting text from markdown file."""
    md_data = "# Title\n\nContent in markdown format.".encode("utf-8")
    result = extract_text(md_data, "README.md")
    assert "# Title" in result
    assert "Content in markdown" in result


def test_extract_unsupported_extension():
    """Test graceful handling of unknown file types."""
    binary_data = b"\x00\x01\x02\x03\x04"
    result = extract_text(binary_data, "archive.bin")
    assert result == ""
