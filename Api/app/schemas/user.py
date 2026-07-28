"""
Stream2Vec — User Pydantic Schemas.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Shared user fields."""
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, description="User full name")


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(..., min_length=8, description="Plain text password")


class UserResponse(UserBase):
    """Schema for user API responses."""
    id: uuid.UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
