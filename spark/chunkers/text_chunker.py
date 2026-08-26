"""
Text Chunker — Splits cleaned text into overlapping windows for embedding.

Strategy: sentence-aware sliding window
    - Tokenize into sentences using a simple regex splitter (no NLTK dependency
      in Spark workers; NLTK data files are impractical to distribute).
    - Group sentences into chunks until the character budget is exhausted.
    - Slide forward by (chunk_size - overlap) characters.

Parameters (via env vars or defaults):
    CHUNK_MAX_CHARS:     Maximum characters per chunk (default: 2000).
    CHUNK_OVERLAP_CHARS: Characters of overlap between consecutive chunks (default: 200).

This approach is deterministic and fast, which suits a Spark UDF context.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

# ── Configuration ─────────────────────────────────────────────────────────────

CHUNK_MAX_CHARS: int = int(os.environ.get("CHUNK_MAX_CHARS", "2000"))
CHUNK_OVERLAP_CHARS: int = int(os.environ.get("CHUNK_OVERLAP_CHARS", "200"))


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class TextChunk:
    """A single text chunk produced by the chunker."""

    text: str
    chunk_index: int
    char_start: int
    char_end: int


# ── Public API ────────────────────────────────────────────────────────────────

def chunk_text(
    text: str,
    *,
    max_chars: int = CHUNK_MAX_CHARS,
    overlap_chars: int = CHUNK_OVERLAP_CHARS,
) -> list[TextChunk]:
    """Split text into overlapping chunks.

    Args:
        text:          Cleaned input text.
        max_chars:     Maximum character count per chunk.
        overlap_chars: Character overlap between consecutive chunks.

    Returns:
        List[TextChunk]: Ordered, 0-indexed chunk list.

    Notes:
        - Returns a single chunk if text fits within max_chars.
        - Returns an empty list if text is empty.
    """
    text = text.strip()
    if not text:
        return []

    sentences = _split_into_sentences(text)
    return _build_chunks(sentences, max_chars=max_chars, overlap_chars=overlap_chars)


# ── Internal helpers ──────────────────────────────────────────────────────────

# Sentence boundary: period / ? / ! followed by whitespace or end-of-string
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.?!])\s+")


def _split_into_sentences(text: str) -> list[str]:
    """Split text into sentences using punctuation heuristics."""
    parts = _SENTENCE_SPLIT_RE.split(text)
    # Re-attach empty parts that came from the split
    return [p.strip() for p in parts if p.strip()]


def _build_chunks(
    sentences: list[str],
    *,
    max_chars: int,
    overlap_chars: int,
) -> list[TextChunk]:
    """Greedily pack sentences into chunks, sliding with overlap."""
    chunks: list[TextChunk] = []
    current_sentences: list[str] = []
    current_len: int = 0
    char_cursor: int = 0  # tracks position in original text

    for sentence in sentences:
        sentence_len = len(sentence) + 1  # +1 for the space separator

        if current_sentences and current_len + sentence_len > max_chars:
            # Emit current chunk
            chunk_text_str = " ".join(current_sentences)
            char_start = char_cursor
            char_end = char_start + len(chunk_text_str)
            chunks.append(
                TextChunk(
                    text=chunk_text_str,
                    chunk_index=len(chunks),
                    char_start=char_start,
                    char_end=char_end,
                )
            )

            # Slide: drop sentences from front until under overlap budget
            overlap_budget = overlap_chars
            while current_sentences and overlap_budget > 0:
                dropped = current_sentences.pop(0)
                char_cursor += len(dropped) + 1
                overlap_budget -= len(dropped) + 1
                current_len -= len(dropped) + 1

        current_sentences.append(sentence)
        current_len += sentence_len

    # Emit final chunk if anything remains
    if current_sentences:
        chunk_text_str = " ".join(current_sentences)
        char_start = char_cursor
        char_end = char_start + len(chunk_text_str)
        chunks.append(
            TextChunk(
                text=chunk_text_str,
                chunk_index=len(chunks),
                char_start=char_start,
                char_end=char_end,
            )
        )

    return chunks


def chunk_text_to_dicts(text: str, **kwargs) -> list[dict]:
    """Convenience wrapper — returns list of plain dicts (Spark-friendly)."""
    return [
        {
            "text": c.text,
            "chunk_index": c.chunk_index,
            "char_start": c.char_start,
            "char_end": c.char_end,
        }
        for c in chunk_text(text, **kwargs)
    ]
