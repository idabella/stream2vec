"""
Stream2Vec — Kafka Configuration.

Producer and consumer configuration dictionaries.
"""

from typing import Dict, Any

from app.core.config import settings


def get_producer_config() -> Dict[str, Any]:
    """Return Kafka producer configuration."""
    return {
        "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
        "client.id": f"{settings.APP_NAME}-producer",
        "acks": "all",
        "retries": 3,
        "retry.backoff.ms": 1000,
        "compression.type": "gzip",
    }


def get_consumer_config() -> Dict[str, Any]:
    """Return Kafka consumer configuration."""
    return {
        "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
        "group.id": settings.KAFKA_CONSUMER_GROUP,
        "client.id": f"{settings.APP_NAME}-consumer",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True,
        "auto.commit.interval.ms": 5000,
    }
