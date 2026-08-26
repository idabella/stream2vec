"""
Sentence Transformer Embedding — Generates 384-dim vectors for text chunks.

Uses ``sentence-transformers/all-MiniLM-L6-v2`` (Apache 2.0 license).

Spark Integration Strategy:
    - The model is broadcast to workers via ``SparkContext.broadcast``.
    - Each worker loads the model once per executor process (lazy singleton).
    - Batch encoding is used to amortize GPU/CPU overhead per partition.

Public API:
    embed_texts(texts)          → list[list[float]]
    get_model()                 → SentenceTransformer (singleton)
    VECTOR_DIM                  = 384
"""

from __future__ import annotations

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# Public constant — used by Qdrant collection creation and migration
VECTOR_DIM: int = 384
MODEL_NAME: str = os.environ.get(
    "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)

# ---------------------------------------------------------------------------
# Lazy singleton — one model per executor process
# ---------------------------------------------------------------------------
_model = None


def get_model():
    """Return the cached SentenceTransformer model, loading it on first call.

    Thread safety: Spark runs one Python worker per partition (forked process),
    so GIL issues and concurrent init races do not apply.
    """
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer  # type: ignore

        logger.info("Loading embedding model: %s", MODEL_NAME)
        _model = SentenceTransformer(MODEL_NAME)
        logger.info("Embedding model loaded (dim=%d)", VECTOR_DIM)
    return _model


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def embed_texts(
    texts: list[str],
    *,
    batch_size: int = 64,
    normalize: bool = True,
) -> list[list[float]]:
    """Embed a batch of texts into 384-dimensional vectors.

    Args:
        texts:      List of text strings to embed.
        batch_size: Number of texts to encode in a single forward pass.
        normalize:  If True, L2-normalize vectors (required for cosine similarity).

    Returns:
        list[list[float]]: One 384-dim vector per input text.
    """
    if not texts:
        return []

    model = get_model()
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=normalize,
        show_progress_bar=False,
    )
    # Convert numpy arrays to plain Python lists (Spark-serialisable)
    return [vec.tolist() for vec in embeddings]


def embed_single(text: str) -> list[float]:
    """Convenience wrapper for embedding a single text string."""
    results = embed_texts([text])
    return results[0] if results else []
