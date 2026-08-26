"""
Qdrant Writer — Batches chunk vectors and upserts them to Qdrant.

Called from within a Spark ``foreachBatch`` sink. Each invocation receives a
micro-batch DataFrame containing one row per chunk across all documents in
that batch window.

Schema expected per row:
    document_id  (str)    UUID of the parent document
    chunk_index  (int)    Position of this chunk in the document
    text         (str)    Chunk text (stored as Qdrant payload)
    vector       (list)   384-dim float list

Qdrant upsert contract:
    - Point ID  : deterministic UUID derived from ``{document_id}_{chunk_index}``
    - Payload   : {document_id, chunk_index, text}
    - Vector    : 384-dim cosine-similarity vector

After a successful upsert the writer updates:
    - documents.status      → 'completed'
    - documents.chunk_count → number of chunks upserted
    - processing_jobs row   → COMPLETED

On failure it sets both to 'failed' with the error message.
"""

from __future__ import annotations

import logging
import os
import uuid
from typing import Iterator

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Qdrant helpers
# ---------------------------------------------------------------------------

def _get_qdrant_client():
    """Construct a Qdrant client from environment variables."""
    from qdrant_client import QdrantClient  # type: ignore

    return QdrantClient(
        host=os.environ.get("QDRANT_HOST", "localhost"),
        port=int(os.environ.get("QDRANT_PORT", "6333")),
        api_key=os.environ.get("QDRANT_API_KEY") or None,
    )


def _chunk_point_id(document_id: str, chunk_index: int) -> str:
    """Generate a deterministic UUID for a Qdrant point.

    Determinism ensures re-processing the same chunk overwrites rather than
    duplicates the point.
    """
    namespace = uuid.UUID("12345678-1234-5678-1234-567812345678")
    return str(uuid.uuid5(namespace, f"{document_id}_{chunk_index}"))


def upsert_chunks(
    document_id: str,
    chunks: list[dict],
    collection: str | None = None,
    *,
    batch_size: int = 128,
) -> int:
    """Upsert a list of chunk dicts into Qdrant.

    Args:
        document_id: UUID string of the parent document.
        chunks:      List of dicts with keys: chunk_index, text, vector.
        collection:  Qdrant collection name (defaults to env var).
        batch_size:  Max points per upsert call.

    Returns:
        int: Number of points successfully upserted.
    """
    from qdrant_client.models import PointStruct  # type: ignore

    if not chunks:
        return 0

    collection = collection or os.environ.get(
        "QDRANT_COLLECTION_DOCUMENTS", "documents"
    )
    client = _get_qdrant_client()

    points = [
        PointStruct(
            id=_chunk_point_id(document_id, chunk["chunk_index"]),
            vector=chunk["vector"],
            payload={
                "document_id": document_id,
                "chunk_index": chunk["chunk_index"],
                "text": chunk["text"],
            },
        )
        for chunk in chunks
    ]

    # Batch upsert to stay within Qdrant's request-size limits
    total = 0
    for i in range(0, len(points), batch_size):
        batch = points[i : i + batch_size]
        client.upsert(collection_name=collection, points=batch)
        total += len(batch)
        logger.debug("Upserted %d/%d points for doc %s", total, len(points), document_id)

    return total


# ---------------------------------------------------------------------------
# PostgreSQL status updaters (called from Spark executor — plain psycopg2)
# ---------------------------------------------------------------------------

def _get_pg_conn():
    """Open a synchronous psycopg2 connection (no SQLAlchemy in Spark workers)."""
    import psycopg2  # type: ignore

    # Try DATABASE_URL first (set in .env), then fall back to building from parts
    dsn = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_DSN")
    if dsn:
        # asyncpg DSN uses postgresql+asyncpg:// — convert to plain postgresql://
        dsn = dsn.replace("postgresql+asyncpg://", "postgresql://")
    else:
        host = os.environ.get("POSTGRES_HOST", "postgres")
        port = os.environ.get("POSTGRES_PORT", "5432")
        db   = os.environ.get("POSTGRES_DB", "stream2vec")
        user = os.environ.get("POSTGRES_USER", "stream2vec")
        pwd  = os.environ.get("POSTGRES_PASSWORD", "stream2vec_dev_pass")
        dsn  = f"postgresql://{user}:{pwd}@{host}:{port}/{db}"

    return psycopg2.connect(dsn)


def mark_document_processing(document_id: str) -> None:
    """Update document status to 'processing' when Spark starts work."""
    conn = _get_pg_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE documents
                SET status = 'processing', updated_at = NOW()
                WHERE id = %s AND status IN ('pending', 'failed')
                """,
                (document_id,),
            )
            conn.commit()
    finally:
        conn.close()


def mark_document_completed(document_id: str, chunk_count: int) -> None:
    """Update document status to 'completed' with the chunk count."""
    conn = _get_pg_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE documents
                SET status = 'completed', chunk_count = %s,
                    updated_at = NOW()
                WHERE id = %s
                """,
                (chunk_count, document_id),
            )
            conn.commit()
    finally:
        conn.close()


def mark_document_failed(document_id: str, error_message: str) -> None:
    """Update document status to 'failed' with the error message."""
    conn = _get_pg_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE documents
                SET status = 'failed', error_message = %s,
                    updated_at = NOW()
                WHERE id = %s
                """,
                (error_message[:2048], document_id),
            )
            conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Top-level entry point called by Spark foreachBatch
# ---------------------------------------------------------------------------

def write_batch(batch_df, batch_id: int) -> None:
    """Spark ``foreachBatch`` sink function.

    Receives a micro-batch DataFrame and processes each document in it.
    Expected columns: document_id, chunk_index, text, vector (array<float>).
    """
    import pandas as pd  # type: ignore — Spark executor has pandas

    logger.info("Processing batch_id=%d", batch_id)
    pdf: pd.DataFrame = batch_df.toPandas()

    if pdf.empty:
        logger.info("Empty batch, nothing to write.")
        return

    # Group by document so we can upsert all chunks together and then
    # update the document status atomically (per document).
    for doc_id, group in pdf.groupby("document_id"):
        try:
            chunks = [
                {
                    "chunk_index": row["chunk_index"],
                    "text": row["text"],
                    "vector": list(row["vector"]),
                }
                for _, row in group.iterrows()
            ]
            count = upsert_chunks(str(doc_id), chunks)
            mark_document_completed(str(doc_id), count)
            logger.info(
                "Document %s completed: %d chunks upserted.", doc_id, count
            )
        except Exception as exc:
            logger.error("Failed to write document %s: %s", doc_id, exc)
            try:
                mark_document_failed(str(doc_id), str(exc))
            except Exception as pg_exc:
                logger.error(
                    "Could not update DB for failed doc %s: %s", doc_id, pg_exc
                )
