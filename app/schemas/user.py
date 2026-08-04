"""User-related Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Shared user fields."""

    email: EmailStr = Field(..., examples=["alice@example.com"])
    full_name: str = Field(..., min_length=2, max_length=150, examples=["Alice Silva"])


class UserCreate(UserBase):
    """Payload for user registration."""

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        examples=["Str0ngP@ssw0rd"],
        description="Password must be at least 8 characters.",
    )


class UserUpdate(BaseModel):
    """Payload for partial user update."""

    full_name: Optional[str] = Field(None, min_length=2, max_length=150)
    password: Optional[str] = Field(None, min_length=8, max_length=128)


class UserRead(UserBase):
    """Public user representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
