from __future__ import annotations

from typing import Any
from uuid import UUID

from app.models import User
from app.repositories import UserRepository
from app.schemas import UserCreate, UserUpdate


class UserService:
    """Business logic for user operations."""

    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        """Return a single user if present."""
        return await self._user_repository.get_by_id(user_id)

    async def get_users(
        self,
        count: int,
        page: int,
        **filters: Any,
    ) -> tuple[list[User], int]:
        """Return users and total count."""
        return await self._user_repository.get_by_filter(count=count, page=page, **filters)

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        return await self._user_repository.create(user_data)

    async def update_user(self, user_id: UUID, user_data: UserUpdate) -> User:
        """Update an existing user."""
        return await self._user_repository.update(user_id, user_data)

    async def delete_user(self, user_id: UUID) -> None:
        """Remove a user."""
        await self._user_repository.delete(user_id)
