import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema containing shared profile fields."""

    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    avatar_url: str | None = Field(default=None, max_length=500)


class UserCreate(UserBase):
    """Schema for user creation with password requirements."""

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password must contain at least 8 characters.",
    )


class UserUpdate(BaseModel):
    """Schema for updating user profile fields."""

    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    avatar_url: str | None = Field(default=None, max_length=500)
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserResponse(UserBase):
    """Safe public user representation without sensitive fields."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
