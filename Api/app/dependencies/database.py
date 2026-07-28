"""
Stream2Vec — Database Dependency Providers.

FastAPI dependency injection for database sessions and repositories.
"""

from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.repositories.document_repository import DocumentRepository
from app.repositories.job_repository import JobRepository
from app.repositories.user_repository import UserRepository


DbSession = Annotated[AsyncSession, Depends(get_db_session)]


def get_document_repository(session: DbSession) -> DocumentRepository:
    """Provide a DocumentRepository instance."""
    return DocumentRepository(session)


def get_job_repository(session: DbSession) -> JobRepository:
    """Provide a JobRepository instance."""
    return JobRepository(session)


def get_user_repository(session: DbSession) -> UserRepository:
    """Provide a UserRepository instance."""
    return UserRepository(session)


DocumentRepo = Annotated[DocumentRepository, Depends(get_document_repository)]
JobRepo = Annotated[JobRepository, Depends(get_job_repository)]
UserRepo = Annotated[UserRepository, Depends(get_user_repository)]
