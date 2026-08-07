"""
Common Dependencies — Shared FastAPI dependency functions.

These dependencies are injected into route handlers via Depends().
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.database.session import get_db

# Type aliases for cleaner route signatures
SettingsDep = Annotated[Settings, Depends(get_settings)]
DBSessionDep = Annotated[AsyncSession, Depends(get_db)]

# TODO: Add authentication dependency
# CurrentUserDep = Annotated[User, Depends(get_current_user)]

# TODO: Add service dependencies as features are implemented
# DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]
