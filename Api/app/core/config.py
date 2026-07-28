"""
Stream2Vec — Centralized Application Configuration.

All settings are loaded from environment variables using Pydantic Settings.
Sensitive values must be set in the .env file (never hardcoded).
"""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ─────────────────────────────────────
    APP_NAME: str = Field(default="Stream2Vec", description="Application name")
    APP_VERSION: str = Field(default="0.1.0", description="Application version")
    APP_ENV: str = Field(default="development", description="Environment (development/staging/production)")
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    SECRET_KEY: str = Field(..., description="Secret key for JWT signing")
    ALLOWED_HOSTS: List[str] = Field(default=["*"], description="Allowed CORS origins")

    # ── API ─────────────────────────────────────────────
    API_V1_PREFIX: str = Field(default="/api/v1", description="API v1 prefix")

    # ── PostgreSQL ───────────────────────────────────────
    POSTGRES_HOST: str = Field(default="postgres", description="PostgreSQL host")
    POSTGRES_PORT: int = Field(default=5432, description="PostgreSQL port")
    POSTGRES_DB: str = Field(default="stream2vec", description="PostgreSQL database name")
    POSTGRES_USER: str = Field(default="stream2vec", description="PostgreSQL user")
    POSTGRES_PASSWORD: str = Field(..., description="PostgreSQL password")
    DATABASE_URL: str = Field(..., description="Full database connection URL")

    # ── MinIO ────────────────────────────────────────────
    MINIO_ENDPOINT: str = Field(default="minio:9000", description="MinIO endpoint")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin", description="MinIO access key")
    MINIO_SECRET_KEY: str = Field(..., description="MinIO secret key")
    MINIO_BUCKET_DOCUMENTS: str = Field(default="documents", description="MinIO bucket for raw documents")
    MINIO_BUCKET_PROCESSED: str = Field(default="processed", description="MinIO bucket for processed documents")
    MINIO_SECURE: bool = Field(default=False, description="Use TLS for MinIO connection")

    # ── Kafka ────────────────────────────────────────────
    KAFKA_BOOTSTRAP_SERVERS: str = Field(default="kafka:9092", description="Kafka bootstrap servers")
    KAFKA_TOPIC_DOCUMENTS: str = Field(default="documents.uploaded", description="Kafka topic for uploaded documents")
    KAFKA_TOPIC_PROCESSED: str = Field(default="documents.processed", description="Kafka topic for processed documents")
    KAFKA_TOPIC_FAILED: str = Field(default="documents.failed", description="Kafka topic for failed processing")
    KAFKA_CONSUMER_GROUP: str = Field(default="stream2vec-group", description="Kafka consumer group ID")

    # ── Qdrant ───────────────────────────────────────────
    QDRANT_HOST: str = Field(default="qdrant", description="Qdrant host")
    QDRANT_PORT: int = Field(default=6333, description="Qdrant port")
    QDRANT_COLLECTION: str = Field(default="documents", description="Qdrant collection name")

    # ── Embeddings ───────────────────────────────────────
    EMBEDDING_MODEL: str = Field(default="all-MiniLM-L6-v2", description="SentenceTransformers model")
    EMBEDDING_DIMENSION: int = Field(default=384, description="Embedding vector dimension")

    # ── Logging ──────────────────────────────────────────
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Log format (json/text)")

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, v: str | List[str]) -> List[str]:
        """Parse ALLOWED_HOSTS from comma-separated string."""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance.
    
    Uses lru_cache to avoid re-reading .env on every call.
    
    Returns:
        Settings: Singleton settings instance.
    """
    return Settings()


settings: Settings = get_settings()
