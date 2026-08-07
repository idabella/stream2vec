"""
API v1 Router — Registers all v1 route groups.

This module aggregates all sub-routers for the v1 API.
Add new routers here as features are developed.
"""

from fastapi import APIRouter

# TODO: Import feature routers as they are implemented
# from app.api.v1.endpoints import documents, search, health

router = APIRouter(prefix="/api/v1")

# TODO: Include sub-routers
# router.include_router(documents.router, prefix="/documents", tags=["Documents"])
# router.include_router(search.router, prefix="/search", tags=["Search"])
