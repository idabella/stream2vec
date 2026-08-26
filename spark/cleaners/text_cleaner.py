"""
Text Cleaner — Normalizes raw extracted text before chunking.

Transformations applied (in order):
    1. Unicode normalization (NFC) — resolve composed vs decomposed forms.
    2. Strip BOM characters.
    3. Replace form-feeds, carriage returns with newlines.
    4. Collapse runs of whitespace-only lines into a single blank line.
    5. Strip leading/trailing whitespace per line.
    6. Drop lines that are clearly OCR artifacts (single-char lines,
       lines that are >90 % non-alphanumeric).
    7. Deduplicate consecutive identical lines (common in headers/footers).
    8. Final strip of the whole string.
"""

from __future__ import annotations

import re
import unicodedata


# ── Public API ────────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """Apply the full normalization pipeline to raw extracted text.

    Args:
        text: Raw text as returned by the extractor.

    Returns:
        str: Cleaned text, ready for chunking.
    """
    if not text:
        return ""

    text = _normalize_unicode(text)
    text = _strip_bom(text)
    text = _normalize_line_endings(text)
    lines = text.splitlines()
    lines = _strip_lines(lines)
    lines = _drop_artifact_lines(lines)
    lines = _deduplicate_consecutive(lines)
    lines = _collapse_blank_lines(lines)
    return "\n".join(lines).strip()


# ── Internal helpers ──────────────────────────────────────────────────────────

def _normalize_unicode(text: str) -> str:
    """Apply NFC normalization — compose code points into canonical forms."""
    return unicodedata.normalize("NFC", text)


def _strip_bom(text: str) -> str:
    """Remove BOM characters that survive encoding conversion."""
    return text.lstrip("\ufeff\u200b\u00a0")


def _normalize_line_endings(text: str) -> str:
    """Unify CR+LF and bare CR to LF; replace form-feed with newline."""
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    text = text.replace("\f", "\n")
    return text


def _strip_lines(lines: list[str]) -> list[str]:
    """Strip leading/trailing whitespace from each individual line."""
    return [line.strip() for line in lines]


# Pattern: >90 % of characters are non-word, non-space chars (e.g., OCR noise)
_ARTIFACT_PATTERN = re.compile(r"^[^\w\s]{3,}$")


def _drop_artifact_lines(lines: list[str]) -> list[str]:
    """Remove lines that are likely OCR/PDF artifacts."""
    cleaned = []
    for line in lines:
        if not line:
            cleaned.append(line)
            continue
        # Drop single isolated special characters
        if len(line) == 1 and not line.isalnum():
            continue
        # Drop lines that are mostly punctuation/noise
        if _ARTIFACT_PATTERN.match(line):
            continue
        # Drop lines where >85 % characters are non-alphanumeric non-space
        non_word = sum(1 for c in line if not c.isalnum() and not c.isspace())
        if len(line) > 4 and non_word / len(line) > 0.85:
            continue
        cleaned.append(line)
    return cleaned


def _deduplicate_consecutive(lines: list[str]) -> list[str]:
    """Remove consecutive duplicate lines (e.g., repeated headers/footers)."""
    if not lines:
        return lines
    result = [lines[0]]
    for line in lines[1:]:
        if line != result[-1]:
            result.append(line)
    return result


def _collapse_blank_lines(lines: list[str]) -> list[str]:
    """Reduce runs of multiple blank lines to a single blank line."""
    result: list[str] = []
    prev_blank = False
    for line in lines:
        is_blank = line == ""
        if is_blank and prev_blank:
            continue
        result.append(line)
        prev_blank = is_blank
    return result
