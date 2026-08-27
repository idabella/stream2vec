"""
Application Configuration — Centralized settings using Pydantic Settings.

All configuration values are loaded from environment variables or .env file.
No hardcoded secrets. All sensitive values must be provided via environment.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Core application settings."""

    name: str = Field(default="Stream2Vec", alias="APP_NAME")
    version: str = Field(default="0.1.0", alias="APP_VERSION")
    env: Literal["development", "staging", "production"] = Field(
        default="development", alias="APP_ENV"
    )
    debug: bool = Field(default=False, alias="DEBUG")
    secret_key: str = Field(alias="SECRET_KEY")


class BackendSettings(BaseSettings):
    """FastAPI server settings."""

    host: str = Field(default="0.0.0.0", alias="BACKEND_HOST")
    port: int = Field(default=8000, alias="BACKEND_PORT")
    workers: int = Field(default=1, alias="BACKEND_WORKERS")
    allowed_origins: list[str] | str = Field(default=["*"], alias="ALLOWED_ORIGINS")

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, v: object) -> list[str]:
        """Parse comma-separated or JSON origins string into a list."""
        if isinstance(v, str):
            v_str = v.strip()
            if not v_str:
                return ["*"]
            if v_str.startswith("[") and v_str.endswith("]"):
                import json
                try:
                    return json.loads(v_str)
                except Exception:
                    pass
            return [origin.strip() for origin in v_str.split(",") if origin.strip()]
        if isinstance(v, list):
            return v
        return ["*"]


class DatabaseSettings(BaseSettings):
    """PostgreSQL database settings."""

    url: str = Field(alias="DATABASE_URL")
    pool_size: int = Field(default=10)
    max_overflow: int = Field(default=20)
    pool_timeout: int = Field(default=30)
    echo: bool = Field(default=False)


class MinIOSettings(BaseSettings):
    """MinIO object storage settings."""

    endpoint: str = Field(alias="MINIO_ENDPOINT")
    access_key: str = Field(alias="MINIO_ACCESS_KEY")
    secret_key: str = Field(alias="MINIO_SECRET_KEY")
    bucket_documents: str = Field(default="documents", alias="MINIO_BUCKET_DOCUMENTS")
    use_ssl: bool = Field(default=False, alias="MINIO_USE_SSL")


class KafkaSettings(BaseSettings):
    """Apache Kafka settings."""

    bootstrap_servers: str = Field(alias="KAFKA_BOOTSTRAP_SERVERS")
    topic_documents: str = Field(default="documents.raw", alias="KAFKA_TOPIC_DOCUMENTS")
    consumer_group: str = Field(
        default="stream2vec-consumers", alias="KAFKA_CONSUMER_GROUP"
    )


class QdrantSettings(BaseSettings):
    """Qdrant vector database settings."""

    host: str = Field(default="qdrant", alias="QDRANT_HOST")
    port: int = Field(default=6333, alias="QDRANT_PORT")
    collection_documents: str = Field(
        default="documents", alias="QDRANT_COLLECTION_DOCUMENTS"
    )
    api_key: str = Field(default="", alias="QDRANT_API_KEY")


class LoggingSettings(BaseSettings):
    """Logging settings."""

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", alias="LOG_LEVEL"
    )
    format: Literal["json", "text"] = Field(default="json", alias="LOG_FORMAT")


class GeminiSettings(BaseSettings):
    """Google Gemini API settings."""

    api_key: str = Field(default="", alias="GEMINI_API_KEY")
    model: str = Field(default="gemini-3.6-flash", alias="GEMINI_MODEL")


class Settings(BaseSettings):
    """Root settings — aggregates all sub-settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app: AppSettings = AppSettings()
    backend: BackendSettings = BackendSettings()
    database: DatabaseSettings = DatabaseSettings()
    minio: MinIOSettings = MinIOSettings()
    kafka: KafkaSettings = KafkaSettings()
    qdrant: QdrantSettings = QdrantSettings()
    logging: LoggingSettings = LoggingSettings()
    gemini: GeminiSettings = GeminiSettings()


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings.

    Uses lru_cache to ensure settings are loaded only once per process.
    Inject via FastAPI dependency injection where possible.

    Returns:
        Settings: The application settings instance.
    """
    return Settings()
