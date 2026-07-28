"""
Stream2Vec — Kafka Topics Registry.

Centralizes all Kafka topic names to avoid magic strings.
"""

from dataclasses import dataclass

from app.core.config import settings


@dataclass(frozen=True)
class KafkaTopics:
    """Registry of all Kafka topic names used in Stream2Vec."""

    DOCUMENTS_UPLOADED: str = settings.KAFKA_TOPIC_DOCUMENTS
    """Topic for newly uploaded documents — triggers Spark pipeline."""

    DOCUMENTS_PROCESSED: str = settings.KAFKA_TOPIC_PROCESSED
    """Topic for successfully processed documents."""

    DOCUMENTS_FAILED: str = settings.KAFKA_TOPIC_FAILED
    """Topic for failed document processing."""

    EMBEDDINGS_READY: str = "embeddings.ready"
    """Topic signaling that embeddings are stored in Qdrant."""


topics = KafkaTopics()
