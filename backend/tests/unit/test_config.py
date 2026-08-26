"""
Unit Tests for Stream2Vec Configuration and Settings.
"""

from app.core.config import get_settings


def test_settings_defaults():
    """Verify default configuration values."""
    settings = get_settings()
    assert settings.app.name == "Stream2Vec"
    assert settings.app.version == "0.1.0"
    assert settings.database.url.startswith("postgresql+asyncpg://")
    assert settings.qdrant.port == 6333
    assert settings.kafka.consumer_group == "stream2vec-consumers"


def test_database_dsn_construction():
    """Verify async PostgreSQL URL formatting."""
    settings = get_settings()
    assert "stream2vec" in settings.database.url


def test_cors_origins_parsing():
    """Verify ALLOWED_ORIGINS JSON / comma list parsing."""
    settings = get_settings()
    assert isinstance(settings.backend.allowed_origins, list)
    assert len(settings.backend.allowed_origins) >= 1
