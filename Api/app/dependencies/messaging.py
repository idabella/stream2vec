"""
Stream2Vec — Messaging Dependency Providers.
"""

from typing import Annotated

from fastapi import Depends

from app.messaging.kafka.producer import KafkaProducerService


def get_kafka_producer() -> KafkaProducerService:
    """Provide a KafkaProducerService instance."""
    # TODO: Implement producer lifecycle management
    return KafkaProducerService()


KafkaProducerDep = Annotated[KafkaProducerService, Depends(get_kafka_producer)]
