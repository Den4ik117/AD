from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr
    description: str | None = None


class UserCreate(UserBase):
    """Schema for creating a user."""


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    username: str | None = None
    email: EmailStr | None = None
    description: str | None = None

    model_config = ConfigDict(extra="forbid")


class UserResponse(UserBase):
    """Schema returned to clients."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Paginated user payload."""

    total: int
    items: list[UserResponse]
