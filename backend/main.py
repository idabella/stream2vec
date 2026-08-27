"""
Stream2Vec — FastAPI Application Entry Point.

Creates and configures the FastAPI application instance.

Registers:
    - API routers
    - Middlewares (CORS, request logging)
    - Exception handlers
    - Application lifespan (startup / shutdown)
    - Prometheus /metrics endpoint (prometheus-fastapi-instrumentator)

Lifespan initializes and verifies all external service connections:
    - PostgreSQL  (SQLAlchemy async engine)
    - MinIO       (object storage)
    - Kafka       (message broker)
    - Qdrant      (vector database)
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.v1.router import router as api_v1_router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.exceptions.handlers import register_exception_handlers
from app.middlewares.logging_middleware import LoggingMiddleware

settings = get_settings()
configure_logging(settings.logging.level, settings.logging.format)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle.

    Startup sequence:
        1. Initialize database connection pool and verify connectivity.
        2. Initialize MinIO client and ensure the documents bucket exists.
        3. Start Kafka producer and verify broker connectivity.
        4. Initialize Qdrant client and ensure the documents collection exists.

    Shutdown sequence:
        1. Stop Kafka producer and flush pending messages.
        2. Dispose SQLAlchemy engine (closes all pooled connections).
    """
    import asyncio
    import time

    logger.info(
        "Starting Stream2Vec",
        extra={"version": settings.app.version, "env": settings.app.env},
    )

    # -------------------------------------------------------------------------
    # 1. PostgreSQL — Test database connectivity
    # -------------------------------------------------------------------------
    from app.database.session import engine
    from sqlalchemy import text

    async def _init_postgres() -> None:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

    for attempt in range(1, 7):
        try:
            await _init_postgres()
            logger.info("PostgreSQL connection established")
            break
        except Exception as exc:
            if attempt == 6:
                logger.error("PostgreSQL connection failed after 6 attempts", extra={"error": str(exc)})
                raise
            logger.warning("PostgreSQL connection attempt %d/6 failed: %s. Retrying in 2s...", attempt, exc)
            await asyncio.sleep(2)

    # -------------------------------------------------------------------------
    # 2. MinIO — Initialize client and ensure bucket exists
    # -------------------------------------------------------------------------
    from app.storage.minio_client import init_minio_client

    for attempt in range(1, 7):
        try:
            init_minio_client()
            logger.info("MinIO initialized")
            break
        except Exception as exc:
            if attempt == 6:
                logger.error("MinIO initialization failed after 6 attempts", extra={"error": str(exc)})
                raise
            logger.warning("MinIO initialization attempt %d/6 failed: %s. Retrying in 2s...", attempt, exc)
            time.sleep(2)

    # -------------------------------------------------------------------------
    # 3. Kafka — Start producer and verify broker connectivity
    # -------------------------------------------------------------------------
    from app.messaging.kafka_client import init_kafka_producer

    for attempt in range(1, 7):
        try:
            await init_kafka_producer()
            logger.info("Kafka producer started")
            break
        except Exception as exc:
            if attempt == 6:
                logger.error("Kafka producer initialization failed after 6 attempts", extra={"error": str(exc)})
                raise
            logger.warning("Kafka producer initialization attempt %d/6 failed: %s. Retrying in 2s...", attempt, exc)
            await asyncio.sleep(2)

    # -------------------------------------------------------------------------
    # 4. Qdrant — Initialize client and ensure collection exists
    # -------------------------------------------------------------------------
    from app.storage.qdrant_client import init_qdrant_client

    for attempt in range(1, 7):
        try:
            init_qdrant_client()
            logger.info("Qdrant initialized")
            break
        except Exception as exc:
            if attempt == 6:
                logger.error("Qdrant initialization failed after 6 attempts", extra={"error": str(exc)})
                raise
            logger.warning("Qdrant initialization attempt %d/6 failed: %s. Retrying in 2s...", attempt, exc)
            time.sleep(2)

    logger.info("All services initialized — Stream2Vec is ready")

    yield

    # -------------------------------------------------------------------------
    # Shutdown
    # -------------------------------------------------------------------------
    logger.info("Shutting down Stream2Vec")

    from app.messaging.kafka_client import shutdown_kafka_producer
    await shutdown_kafka_producer()

    await engine.dispose()
    logger.info("Stream2Vec shutdown complete")


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
        openapi_url="/openapi.json" if settings.app.debug else None,
        lifespan=lifespan,
    )

    # -------------------------------------------------------------------------
    # Middlewares — order matters: last added = outermost
    # -------------------------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(LoggingMiddleware)

    # -------------------------------------------------------------------------
    # Exception handlers
    # -------------------------------------------------------------------------
    register_exception_handlers(app)

    # -------------------------------------------------------------------------
    # Routers
    # -------------------------------------------------------------------------
    app.include_router(api_v1_router)

    # -------------------------------------------------------------------------
    # Prometheus — expose /metrics for Prometheus scraping
    # -------------------------------------------------------------------------
    Instrumentator().instrument(app).expose(app)

    return app


app = create_app()


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------

@app.get("/health", tags=["Health"], summary="Application health check")
async def health_check() -> dict:
    """Comprehensive health check for Docker healthchecks and load balancers.

    Verifies connectivity to all external dependencies and returns their
    individual status so operators can identify which service is unhealthy.

    Returns:
        dict: Overall status and per-dependency health.
    """
    from app.database.session import engine
    from app.messaging.kafka_client import get_kafka_producer
    from app.storage.minio_client import get_minio_client
    from app.storage.qdrant_client import get_qdrant_client
    from sqlalchemy import text

    dependencies: dict[str, str] = {}

    # PostgreSQL
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        dependencies["postgres"] = "healthy"
    except Exception:
        dependencies["postgres"] = "unhealthy"

    # MinIO
    try:
        dependencies["minio"] = "healthy" if get_minio_client().ping() else "unhealthy"
    except RuntimeError:
        dependencies["minio"] = "not initialized"

    # Kafka
    try:
        dependencies["kafka"] = "healthy" if await get_kafka_producer().ping() else "unhealthy"
    except RuntimeError:
        dependencies["kafka"] = "not initialized"

    # Qdrant
    try:
        dependencies["qdrant"] = "healthy" if get_qdrant_client().ping() else "unhealthy"
    except RuntimeError:
        dependencies["qdrant"] = "not initialized"

    overall = "healthy" if all(v == "healthy" for v in dependencies.values()) else "degraded"

    return {
        "status": overall,
        "service": settings.app.name,
        "version": settings.app.version,
        "env": settings.app.env,
        "dependencies": dependencies,
    }
