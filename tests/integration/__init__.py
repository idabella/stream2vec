"""
Integration Tests Package.

Integration tests require the Docker Compose stack to be running.
They test the interaction between components (API, database, storage, messaging).

Prerequisites:
    - Run `make up` before executing integration tests
    - Ensure the backend service is healthy: http://localhost:8000/health
"""
