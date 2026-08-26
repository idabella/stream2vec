"""
ProcessingJobRepository — Async CRUD for the ProcessingJob ORM model.

Manages job lifecycle: creation on Kafka event, status updates from Spark worker.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.processing_job import JobStatus, ProcessingJob


class ProcessingJobRepository:
    """Data-access layer for the `processing_jobs` table."""

    # ── Create ────────────────────────────────────────────────────────────────

    async def create(
        self,
        session: AsyncSession,
        *,
        document_id: uuid.UUID,
    ) -> ProcessingJob:
        """Create a new job row in QUEUED state."""
        job = ProcessingJob(
            document_id=document_id,
            status=JobStatus.QUEUED,
        )
        session.add(job)
        await session.flush()
        await session.refresh(job)
        return job

    # ── Read ──────────────────────────────────────────────────────────────────

    async def get_by_id(
        self,
        session: AsyncSession,
        job_id: uuid.UUID,
    ) -> Optional[ProcessingJob]:
        result = await session.execute(
            select(ProcessingJob).where(ProcessingJob.id == job_id)
        )
        return result.scalar_one_or_none()

    async def get_latest_for_document(
        self,
        session: AsyncSession,
        document_id: uuid.UUID,
    ) -> Optional[ProcessingJob]:
        """Return the most recently created job for a document."""
        result = await session.execute(
            select(ProcessingJob)
            .where(ProcessingJob.document_id == document_id)
            .order_by(ProcessingJob.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list_by_status(
        self,
        session: AsyncSession,
        status: JobStatus,
        *,
        limit: int = 100,
    ) -> list[ProcessingJob]:
        """Fetch all jobs with a given status (used by Airflow health checks)."""
        result = await session.execute(
            select(ProcessingJob)
            .where(ProcessingJob.status == status)
            .order_by(ProcessingJob.created_at.asc())
            .limit(limit)
        )
        return result.scalars().all()

    # ── Update ────────────────────────────────────────────────────────────────

    async def mark_running(
        self,
        session: AsyncSession,
        job_id: uuid.UUID,
        *,
        spark_app_id: Optional[str] = None,
    ) -> Optional[ProcessingJob]:
        values: dict = {
            "status": JobStatus.RUNNING,
            "started_at": datetime.now(tz=timezone.utc),
        }
        if spark_app_id:
            values["spark_app_id"] = spark_app_id
        await session.execute(
            update(ProcessingJob).where(ProcessingJob.id == job_id).values(**values)
        )
        return await self.get_by_id(session, job_id)

    async def mark_completed(
        self,
        session: AsyncSession,
        job_id: uuid.UUID,
    ) -> Optional[ProcessingJob]:
        await session.execute(
            update(ProcessingJob)
            .where(ProcessingJob.id == job_id)
            .values(
                status=JobStatus.COMPLETED,
                completed_at=datetime.now(tz=timezone.utc),
            )
        )
        return await self.get_by_id(session, job_id)

    async def mark_failed(
        self,
        session: AsyncSession,
        job_id: uuid.UUID,
        *,
        error_message: str,
    ) -> Optional[ProcessingJob]:
        await session.execute(
            update(ProcessingJob)
            .where(ProcessingJob.id == job_id)
            .values(
                status=JobStatus.FAILED,
                completed_at=datetime.now(tz=timezone.utc),
                error_message=error_message,
            )
        )
        return await self.get_by_id(session, job_id)
