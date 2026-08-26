"""
Kafka Client — Async Kafka producer for Stream2Vec.

Wraps aiokafka's AIOKafkaProducer to publish document ingestion events
to the Kafka topic consumed downstream by Spark Structured Streaming.

Lifecycle:
    - start() is called during FastAPI lifespan startup.
    - stop()  is called during FastAPI lifespan shutdown.

The producer is exposed as a FastAPI dependency via get_kafka_producer().
"""

import json
import logging

from aiokafka import AIOKafkaProducer

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class KafkaProducerClient:
    """Async Kafka producer that serializes events as JSON.

    Messages are keyed by document_id (UTF-8 bytes) so that all events
    for the same document are routed to the same partition.
    """

    def __init__(self) -> None:
        """Create the AIOKafkaProducer instance (not yet connected)."""
        self._producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            # Acknowledge after the leader and all in-sync replicas receive the message
            acks="all",
            # aiokafka handles retries internally; no explicit `retries` kwarg supported
        )
        self._topic = settings.kafka.topic_documents
        logger.info(
            "KafkaProducerClient created",
            extra={"bootstrap_servers": settings.kafka.bootstrap_servers},
        )

    async def start(self) -> None:
        """Connect to the Kafka broker.

        Must be called before publishing messages.
        Called automatically during FastAPI lifespan startup.

        Raises:
            KafkaConnectionError: If the broker is not reachable.
        """
        await self._producer.start()
        logger.info("Kafka producer started")

    async def stop(self) -> None:
        """Flush pending messages and disconnect from the Kafka broker.

        Called automatically during FastAPI lifespan shutdown.
        """
        await self._producer.stop()
        logger.info("Kafka producer stopped")

    async def ping(self) -> bool:
        """Check broker connectivity by fetching cluster metadata.

        Returns:
            bool: True if the broker responds, False otherwise.
        """
        try:
            await self._producer.client.fetch_all_metadata()
            return True
        except Exception as exc:
            logger.warning("Kafka ping failed", extra={"error": str(exc)})
            return False

    async def publish_document_event(
        self, document_id: str, payload: dict
    ) -> None:
        """Publish a document ingestion event to the documents topic.

        Args:
            document_id: Unique identifier of the ingested document (used as
                         the message key for partition affinity).
            payload:     Event payload containing document metadata.

        Raises:
            MessagingException: If the message cannot be published.
        """
        try:
            await self._producer.send_and_wait(
                topic=self._topic,
                key=document_id,
                value=payload,
            )
            logger.info(
                "Document event published",
                extra={"document_id": document_id, "topic": self._topic},
            )
        except Exception as exc:
            from app.exceptions.handlers import MessagingException

            logger.error(
                "Failed to publish document event",
                extra={"document_id": document_id, "error": str(exc)},
            )
            raise MessagingException(str(exc)) from exc


# ---------------------------------------------------------------------------
# Singleton instance — initialized at startup
# ---------------------------------------------------------------------------
_kafka_producer: KafkaProducerClient | None = None


def get_kafka_producer() -> KafkaProducerClient:
    """FastAPI dependency — return the application-level Kafka producer.

    Raises:
        RuntimeError: If called before the producer has been started
                      during application startup.
    """
    if _kafka_producer is None:
        raise RuntimeError("KafkaProducerClient has not been initialized. Check application startup.")
    return _kafka_producer


async def init_kafka_producer() -> KafkaProducerClient:
    """Initialize, connect, and return the singleton Kafka producer.

    Called once from the FastAPI lifespan handler.
    """
    global _kafka_producer
    _kafka_producer = KafkaProducerClient()
    await _kafka_producer.start()
    return _kafka_producer


async def shutdown_kafka_producer() -> None:
    """Stop the Kafka producer gracefully.

    Called from the FastAPI lifespan shutdown handler.
    """
    global _kafka_producer
    if _kafka_producer is not None:
        await _kafka_producer.stop()
        _kafka_producer = None
