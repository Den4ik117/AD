from __future__ import annotations

from typing import Any
from uuid import UUID

from redis.asyncio import Redis

from app.models import User
from app.repositories import UserRepository
from app.schemas import UserCreate, UserResponse, UserUpdate

USER_CACHE_TTL_SECONDS = 3600


class UserService:
    """Business logic for user operations."""

    def __init__(
        self, user_repository: UserRepository, cache: Redis | None = None
    ) -> None:
        self._user_repository = user_repository
        self._cache = cache

    async def get_user_by_id(self, user_id: UUID) -> User | UserResponse | None:
        """Return a single user if present."""
        cache_key = self._user_cache_key(user_id)
        if self._cache:
            cached_user = await self._cache.get(cache_key)
            if cached_user:
                return UserResponse.model_validate_json(cached_user)

        user = await self._user_repository.get_by_id(user_id)
        if user and self._cache:
            await self._cache.setex(
                cache_key,
                USER_CACHE_TTL_SECONDS,
                UserResponse.model_validate(user).model_dump_json(),
            )
        return user

    async def get_users(
        self,
        count: int,
        page: int,
        **filters: Any,
    ) -> tuple[list[User], int]:
        """Return users and total count."""
        return await self._user_repository.get_by_filter(
            count=count, page=page, **filters
        )

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        return await self._user_repository.create(user_data)

    async def update_user(self, user_id: UUID, user_data: UserUpdate) -> User:
        """Update an existing user."""
        user = await self._user_repository.update(user_id, user_data)
        if self._cache:
            await self._cache.delete(self._user_cache_key(user_id))
        return user

    async def delete_user(self, user_id: UUID) -> None:
        """Remove a user."""
        await self._user_repository.delete(user_id)
        if self._cache:
            await self._cache.delete(self._user_cache_key(user_id))

    @staticmethod
    def _user_cache_key(user_id: UUID) -> str:
        return f"user:{user_id}"
