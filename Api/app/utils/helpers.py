"""
Stream2Vec — Utility Helpers.

Common utility functions used across the application.
"""

import hashlib
import uuid
from pathlib import Path
from typing import Optional

# Supported document types
SUPPORTED_CONTENT_TYPES = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "text/plain": ".txt",
    "text/markdown": ".md",
    "text/html": ".html",
}

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB


def generate_minio_path(document_id: str, filename: str) -> str:
    """Generate a MinIO object path for a document.
    
    Args:
        document_id: Unique document identifier.
        filename: Original filename.
        
    Returns:
        str: MinIO object path (e.g., 'raw/uuid/filename.pdf').
    """
    extension = Path(filename).suffix.lower()
    return f"raw/{document_id}/{document_id}{extension}"


def compute_file_hash(content: bytes) -> str:
    """Compute SHA-256 hash of file content.
    
    Args:
        content: File binary content.
        
    Returns:
        str: Hex-encoded SHA-256 hash.
    """
    return hashlib.sha256(content).hexdigest()


def is_supported_file(content_type: str) -> bool:
    """Check if a content type is supported for processing.
    
    Args:
        content_type: MIME type to check.
        
    Returns:
        bool: True if supported, False otherwise.
    """
    return content_type in SUPPORTED_CONTENT_TYPES


def generate_uuid() -> str:
    """Generate a new UUID4 string.
    
    Returns:
        str: UUID4 string.
    """
    return str(uuid.uuid4())
