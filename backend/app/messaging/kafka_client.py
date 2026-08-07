"""
Kafka Client — Message broker interface.

Provides methods for interacting with Apache Kafka:
- Publishing document events to topics
- Consuming messages from topics (for status updates)
- Topic management

The Kafka producer is the primary interface used by the backend.
The Spark Structured Streaming consumer is defined in the spark/ module.
"""

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class KafkaProducer:
    """Async Kafka producer for publishing document events.

    Publishes events to the documents topic when new files are ingested.
    Events are consumed downstream by Spark Structured Streaming.
    """

    def __init__(self) -> None:
        """Initialize the Kafka producer.

        TODO: Initialize aiokafka AIOKafkaProducer with settings.
        """
        # TODO: Implement Kafka producer initialization
        # self._producer = AIOKafkaProducer(
        #     bootstrap_servers=settings.kafka.bootstrap_servers
        # )
        self._topic = settings.kafka.topic_documents
        logger.info("KafkaProducer initialized (stub)")

    async def start(self) -> None:
        """Start the Kafka producer.

        Must be called before publishing messages.
        Typically called during FastAPI startup.

        Raises:
            NotImplementedError: Until messaging is implemented.
        """
        # TODO: await self._producer.start()
        raise NotImplementedError("Kafka producer start not yet implemented.")

    async def stop(self) -> None:
        """Stop the Kafka producer and flush pending messages.

        Must be called during FastAPI shutdown.

        Raises:
            NotImplementedError: Until messaging is implemented.
        """
        # TODO: await self._producer.stop()
        raise NotImplementedError("Kafka producer stop not yet implemented.")

    async def publish_document_event(self, document_id: str, payload: dict) -> None:
        """Publish a document ingestion event to Kafka.

        Args:
            document_id: Unique identifier of the ingested document.
            payload: Event payload containing document metadata.

        Raises:
            NotImplementedError: Until messaging is implemented.
        """
        # TODO: Implement event publishing
        raise NotImplementedError("Kafka publish not yet implemented.")
