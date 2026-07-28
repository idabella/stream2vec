"""
Stream2Vec — Kafka Consumer Service.

Consumes events from Kafka topics for backend processing.
Note: Main stream processing is handled by Spark, this consumer
is for backend-level event handling (e.g., status updates).
"""

import logging
from typing import Callable, List, Optional

from app.messaging.kafka.topics import topics

logger = logging.getLogger(__name__)


class KafkaConsumerService:
    """Service for consuming events from Kafka topics."""

    def __init__(self, topics_to_subscribe: List[str]) -> None:
        """Initialize Kafka consumer.
        
        Args:
            topics_to_subscribe: List of topic names to subscribe to.
        """
        self._topics = topics_to_subscribe
        self._consumer = None
        self._running = False
        # TODO: Initialize confluent_kafka Consumer with get_consumer_config()

    def connect(self) -> None:
        """Connect and subscribe to configured topics."""
        # TODO: Implement
        raise NotImplementedError

    def disconnect(self) -> None:
        """Close the consumer connection."""
        # TODO: Implement
        raise NotImplementedError

    async def consume(self, handler: Callable, poll_timeout: float = 1.0) -> None:
        """Start consuming messages and pass them to handler.
        
        Args:
            handler: Async callable to process each message.
            poll_timeout: Polling timeout in seconds.
        """
        # TODO: Implement consumption loop
        raise NotImplementedError
