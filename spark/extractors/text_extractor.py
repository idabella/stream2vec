"""
Text Extractor — Downloads a file from MinIO and extracts plain text.

Supported formats:
    - .txt  / .md  — read as-is (UTF-8)
    - .pdf         — pdfplumber page-by-page extraction
    - .docx        — python-docx paragraph extraction

All other formats return an empty string with a logged warning so the
pipeline degrades gracefully rather than crashing the Spark partition.
"""

from __future__ import annotations

import io
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


def _get_minio_client():
    """Lazy MinIO client — constructed once per Spark executor process."""
    from minio import Minio  # type: ignore

    endpoint = os.environ.get("MINIO_ENDPOINT", "minio:9000")
    if endpoint.startswith("http://"):
        endpoint = endpoint[7:]
    elif endpoint.startswith("https://"):
        endpoint = endpoint[8:]
    endpoint = endpoint.rstrip("/")

    return Minio(
        endpoint=endpoint,
        access_key=os.environ.get("MINIO_ACCESS_KEY", "minio_admin"),
        secret_key=os.environ.get("MINIO_SECRET_KEY", "minio_dev_password"),
        secure=os.environ.get("MINIO_USE_SSL", "false").lower() == "true",
    )


def download_bytes(minio_path: str) -> bytes:
    """Download an object from MinIO and return raw bytes.

    Args:
        minio_path: Full object path as stored in the ``minio_path`` DB column,
                    e.g. ``documents/{uuid}/{filename}``.

    Returns:
        bytes: Raw file content.

    Raises:
        Exception: On any MinIO connectivity or permission error.
    """
    bucket = os.environ.get("MINIO_BUCKET_DOCUMENTS", "documents")
    object_key = minio_path

    client = _get_minio_client()
    response = client.get_object(bucket, object_key)
    try:
        return response.read()
    finally:
        response.close()
        response.release_conn()


def extract_text(data: bytes, filename: str) -> str:
    """Extract plain text from raw file bytes.

    Args:
        data:     Raw file bytes downloaded from MinIO.
        filename: Original filename — used to determine the extraction strategy.

    Returns:
        str: Extracted plain text (may be empty if unsupported format).
    """
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext in {"txt", "md", "rst", "log", "csv", "json", "yaml", "yml"}:
        return _extract_plain_text(data)
    elif ext == "pdf":
        return _extract_pdf(data)
    elif ext == "docx":
        return _extract_docx(data)
    else:
        logger.warning("Unsupported file extension '%s' — skipping text extraction.", ext)
        return ""


def _extract_plain_text(data: bytes) -> str:
    """Decode bytes as UTF-8, falling back to latin-1."""
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1", errors="replace")


def _extract_pdf(data: bytes) -> str:
    """Extract text from a PDF using pdfplumber."""
    try:
        import pdfplumber  # type: ignore

        pages: list[str] = []
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                pages.append(page_text)
        return "\n".join(pages)
    except ImportError:
        logger.error("pdfplumber not installed — cannot extract PDF text.")
        return ""
    except Exception as exc:
        logger.error("PDF extraction failed: %s", exc)
        return ""


def _extract_docx(data: bytes) -> str:
    """Extract text from a DOCX file using python-docx."""
    try:
        import docx  # type: ignore

        doc = docx.Document(io.BytesIO(data))
        return "\n".join(para.text for para in doc.paragraphs if para.text.strip())
    except ImportError:
        logger.error("python-docx not installed — cannot extract DOCX text.")
        return ""
    except Exception as exc:
        logger.error("DOCX extraction failed: %s", exc)
        return ""


def extract_text_from_minio(minio_path: str, filename: str) -> str:
    """Download from MinIO and extract text in one call.

    Convenience wrapper used by the Spark UDF.
    """
    data = download_bytes(minio_path)
    return extract_text(data, filename)
