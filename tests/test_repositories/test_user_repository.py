from __future__ import annotations

import pytest
from uuid import uuid4

from app.repositories import UserNotFoundError, UserRepository
from app.schemas import UserCreate, UserUpdate


pytestmark = pytest.mark.asyncio


async def test_user_repository_crud_flow(async_session):
    repo = UserRepository(async_session)
    suffix = uuid4().hex[:6]

    created = await repo.create(
        UserCreate(
            username=f"user_{suffix}",
            email=f"user_{suffix}@example.com",
            description="Первоначальное описание",
        )
    )
    assert created.id is not None

    fetched = await repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.email == created.email

    updated = await repo.update(created.id, UserUpdate(description="Обновлено"))
    assert updated.description == "Обновлено"

    users, total = await repo.get_by_filter(count=10, page=1)
    assert total == 1
    assert users[0].username == created.username

    await repo.delete(created.id)
    assert await repo.get_by_id(created.id) is None

    with pytest.raises(UserNotFoundError):
        await repo.delete(created.id)
