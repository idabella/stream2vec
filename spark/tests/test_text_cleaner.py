"""
Unit Tests for Spark Text Cleaner.
"""

from cleaners.text_cleaner import clean_text


def test_clean_text_basic():
    """Test standard whitespace and newline normalization."""
    raw = "  Hello   world!  \n\n\n\n  Line 2 with \r\n Windows endings.  "
    cleaned = clean_text(raw)
    assert "Hello   world!" in cleaned
    assert "\r" not in cleaned
    assert "\n\n\n" not in cleaned
    assert "Line 2 with" in cleaned
    assert "Windows endings." in cleaned


def test_clean_text_bom_and_unicode():
    """Test removal of BOM characters and unicode normalization."""
    raw = "\ufeff\u200bDocument with zero-width characters and é accents."
    cleaned = clean_text(raw)
    assert not cleaned.startswith("\ufeff")
    assert not cleaned.startswith("\u200b")
    assert "Document with zero-width characters" in cleaned


def test_clean_text_artifacts_and_duplicates():
    """Test stripping OCR noise lines and deduplicating header lines."""
    raw = (
        "Header Title\n"
        "Header Title\n"
        "###$$$%%%\n"
        "Valid text content line.\n"
        "Valid text content line 2."
    )
    cleaned = clean_text(raw)
    lines = cleaned.splitlines()
    assert lines.count("Header Title") == 1
    assert "###$$$%%%" not in cleaned
    assert "Valid text content line." in cleaned


def test_clean_text_empty():
    """Test clean_text on empty / whitespace input."""
    assert clean_text("") == ""
    assert clean_text("   \n\n  ") == ""
