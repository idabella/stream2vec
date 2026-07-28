"""
Stream2Vec — FastAPI Application Entry Point.

This module initializes the FastAPI application with:
- Lifespan context manager for startup/shutdown events
- CORS middleware
- Logging middleware
- API v1 router
- Health check endpoint
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.
    
    Handles startup and shutdown events:
    - Startup: Initialize connections (DB, MinIO, Kafka, Qdrant)
    - Shutdown: Gracefully close all connections
    """
    # ── Startup ─────────────────────────────────────────
    setup_logging()
    # TODO: Initialize database connection pool
    # TODO: Initialize MinIO client
    # TODO: Initialize Kafka producer
    # TODO: Initialize Qdrant client
    yield
    # ── Shutdown ────────────────────────────────────────
    # TODO: Close database connection pool
    # TODO: Close Kafka producer


def create_application() -> FastAPI:
    """Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured application instance.
    """
    application = FastAPI(
        title=settings.APP_NAME,
        description="Cloud-Native Document Vectorization Platform",
        version=settings.APP_VERSION,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS Middleware ──────────────────────────────────
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ─────────────────────────────────────────
    application.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return application


app = create_application()


@app.get("/health", tags=["Health"])
async def health_check() -> JSONResponse:
    """Health check endpoint.
    
    Returns:
        JSONResponse: Application health status.
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV,
        }
    )
