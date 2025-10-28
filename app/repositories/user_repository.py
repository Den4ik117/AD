from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas.user import UserCreate, UserUpdate


class UserNotFoundError(LookupError):
    """Raised when a user is not present in the database."""


class UserRepository:
    """Async repository for user persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Return a single user by identifier."""
        return await self._session.get(User, user_id)

    async def get_by_filter(
        self,
        count: int,
        page: int,
        **filters: Any,
    ) -> tuple[list[User], int]:
        """Return paginated users matching the provided filters along with total count."""
        query = self._apply_filters(select(User), filters)
        total_query = self._apply_filters(select(func.count()).select_from(User), filters)

        limited_query = query.order_by(User.created_at.desc()).limit(count).offset((page - 1) * count)
        result = await self._session.execute(limited_query)
        users = result.scalars().all()

        total = await self._session.scalar(total_query)
        return users, int(total or 0)

    async def create(self, user_data: UserCreate) -> User:
        """Persist a new user."""
        user = User(**user_data.model_dump())
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def update(self, user_id: UUID, user_data: UserUpdate) -> User:
        """Update an existing user."""
        user = await self.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User {user_id} does not exist")

        for field, value in user_data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def delete(self, user_id: UUID) -> None:
        """Remove a user."""
        user = await self.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User {user_id} does not exist")

        await self._session.delete(user)
        await self._session.commit()

    @staticmethod
    def _apply_filters(query: Select[Any], filters: dict[str, Any]) -> Select[Any]:
        """Attach equality filters for columns present on the User model."""
        for field, value in filters.items():
            if value is None:
                continue
            column = getattr(User, field, None)
            if column is not None:
                query = query.where(column == value)
        return query
