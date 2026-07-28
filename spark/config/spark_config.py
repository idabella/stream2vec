"""
Stream2Vec — Spark Configuration.

Centralized configuration for the Spark streaming pipeline.
Reads from environment variables with sensible defaults.
"""

import os
from dataclasses import dataclass, field


@dataclass
class SparkConfig:
    """Configuration for the Spark Structured Streaming job."""

    # ── Spark ────────────────────────────────────────────────
    APP_NAME: str = field(
        default_factory=lambda: os.getenv("SPARK_APP_NAME", "Stream2Vec")
    )
    MASTER_URL: str = field(
        default_factory=lambda: os.getenv("SPARK_MASTER_URL", "spark://spark-master:7077")
    )
    SHUFFLE_PARTITIONS: int = field(
        default_factory=lambda: int(os.getenv("SPARK_SHUFFLE_PARTITIONS", "10"))
    )

    # ── Kafka ────────────────────────────────────────────────
    KAFKA_BOOTSTRAP_SERVERS: str = field(
        default_factory=lambda: os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    )
    KAFKA_TOPIC_INPUT: str = field(
        default_factory=lambda: os.getenv("KAFKA_TOPIC_DOCUMENTS", "documents.uploaded")
    )
    KAFKA_TOPIC_OUTPUT: str = field(
        default_factory=lambda: os.getenv("KAFKA_TOPIC_PROCESSED", "documents.processed")
    )
    KAFKA_CONSUMER_GROUP: str = field(
        default_factory=lambda: os.getenv("KAFKA_CONSUMER_GROUP", "spark-stream2vec")
    )

    # ── MinIO ────────────────────────────────────────────────
    MINIO_ENDPOINT: str = field(
        default_factory=lambda: os.getenv("MINIO_ENDPOINT", "minio:9000")
    )
    MINIO_ACCESS_KEY: str = field(
        default_factory=lambda: os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    )
    MINIO_SECRET_KEY: str = field(
        default_factory=lambda: os.getenv("MINIO_SECRET_KEY", "minioadmin123")
    )

    # ── Qdrant ───────────────────────────────────────────────
    QDRANT_HOST: str = field(
        default_factory=lambda: os.getenv("QDRANT_HOST", "qdrant")
    )
    QDRANT_PORT: int = field(
        default_factory=lambda: int(os.getenv("QDRANT_PORT", "6333"))
    )
    QDRANT_COLLECTION: str = field(
        default_factory=lambda: os.getenv("QDRANT_COLLECTION", "documents")
    )

    # ── Embeddings ───────────────────────────────────────────
    EMBEDDING_MODEL: str = field(
        default_factory=lambda: os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    )
    EMBEDDING_DIMENSION: int = field(
        default_factory=lambda: int(os.getenv("EMBEDDING_DIMENSION", "384"))
    )
    EMBEDDING_BATCH_SIZE: int = field(
        default_factory=lambda: int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))
    )

    # ── Chunking ─────────────────────────────────────────────
    CHUNK_SIZE: int = field(
        default_factory=lambda: int(os.getenv("CHUNK_SIZE", "512"))
    )
    CHUNK_OVERLAP: int = field(
        default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "50"))
    )

    # ── Checkpointing ────────────────────────────────────────
    CHECKPOINT_LOCATION: str = field(
        default_factory=lambda: os.getenv("SPARK_CHECKPOINT_LOCATION", "/tmp/spark/checkpoints")
    )
    TRIGGER_INTERVAL: str = field(
        default_factory=lambda: os.getenv("SPARK_TRIGGER_INTERVAL", "10 seconds")
    )
