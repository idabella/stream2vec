"""
Pytest Configuration and Shared Fixtures.

Defines fixtures shared across all test modules:
- FastAPI test client
- In-memory database session
- Mock MinIO client
- Mock Kafka producer
"""

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    """FastAPI test client fixture.

    Returns:
        TestClient: Synchronous test client for FastAPI.
    """
    # TODO: Configure test database URL (SQLite for unit tests)
    # TODO: Override dependencies for mocked services
    return TestClient(app)


# TODO: Add async_client fixture for async tests
# TODO: Add db_session fixture with test database
# TODO: Add mock_minio fixture
# TODO: Add mock_kafka fixture
