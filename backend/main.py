"""
Stream2Vec — FastAPI Application Entry Point.

This module creates and configures the FastAPI application instance.
It registers:
- API routers
- Middlewares
- Exception handlers
- Startup/shutdown lifecycle events
- Health check endpoint
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_v1_router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.exceptions.handlers import register_exception_handlers
from app.middlewares.logging_middleware import LoggingMiddleware

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle.

    Startup:
        - Initialize database connections
        - Start Kafka producer
        - Ensure MinIO buckets exist

    Shutdown:
        - Close database connections
        - Stop Kafka producer
    """
    # --- Startup ---
    configure_logging(settings.logging.level, settings.logging.format)
    logger.info(f"Starting {settings.app.name} v{settings.app.version} [{settings.app.env}]")

    # TODO: Initialize database connection pool
    # TODO: Start Kafka producer
    # TODO: Ensure MinIO buckets exist

    yield

    # --- Shutdown ---
    logger.info(f"Shutting down {settings.app.name}")

    # TODO: Close database connections
    # TODO: Stop Kafka producer


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance.

    Returns:
        FastAPI: Configured FastAPI application.
    """
    app = FastAPI(
        title=settings.app.name,
        version=settings.app.version,
        description="Cloud-Native Document Ingestion and Vectorization Platform",
        docs_url="/docs" if settings.app.debug else None,
        redoc_url="/redoc" if settings.app.debug else None,
        lifespan=lifespan,
    )

    # --- Middlewares ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(LoggingMiddleware)

    # --- Exception handlers ---
    register_exception_handlers(app)

    # --- Routers ---
    app.include_router(api_v1_router)

    return app


app = create_app()


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint for Docker and load balancers.

    Returns:
        dict: Status and application version.
    """
    return {
        "status": "healthy",
        "service": settings.app.name,
        "version": settings.app.version,
        "env": settings.app.env,
    }
