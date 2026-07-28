"""
Stream2Vec — ProcessingJob Pydantic Schemas.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProcessingJobResponse(BaseModel):
    """Schema for processing job status responses."""
    id: uuid.UUID
    document_id: uuid.UUID
    status: str = Field(..., description="Job status")
    pipeline_stage: Optional[str] = Field(None, description="Current pipeline stage")
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}
