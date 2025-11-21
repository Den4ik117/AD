from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest

from app.repositories import UserRepository
from app.schemas import UserCreate, UserUpdate
from app.services import UserService


@pytest.fixture
def user_repository_mock() -> AsyncMock:
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def user_service(user_repository_mock: AsyncMock) -> UserService:
    return UserService(user_repository_mock)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_get_user_by_id_calls_repository(
    user_service: UserService, user_repository_mock: AsyncMock
):
    user_id = uuid4()
    user_repository_mock.get_by_id.return_value = {"id": user_id}

    result = await user_service.get_user_by_id(user_id)

    assert result == {"id": user_id}
    user_repository_mock.get_by_id.assert_awaited_once_with(user_id)


@pytest.mark.asyncio
async def test_get_users_returns_pagination(
    user_service: UserService, user_repository_mock: AsyncMock
):
    user_repository_mock.get_by_filter.return_value = (["user1"], 1)

    items, total = await user_service.get_users(count=5, page=2)

    assert items == ["user1"]
    assert total == 1
    user_repository_mock.get_by_filter.assert_awaited_once_with(count=5, page=2)


@pytest.mark.asyncio
async def test_create_user_delegates_to_repository(
    user_service: UserService, user_repository_mock: AsyncMock
):
    payload = UserCreate(
        username="tester", email="tester@example.com", description=None
    )
    user_repository_mock.create.return_value = {"username": "tester"}

    result = await user_service.create_user(payload)

    assert result == {"username": "tester"}
    user_repository_mock.create.assert_awaited_once_with(payload)


@pytest.mark.asyncio
async def test_update_user_delegates(
    user_service: UserService, user_repository_mock: AsyncMock
):
    user_id = uuid4()
    payload = UserUpdate(description="new")
    user_repository_mock.update.return_value = {"id": user_id, "description": "new"}

    result = await user_service.update_user(user_id, payload)

    assert result["description"] == "new"
    user_repository_mock.update.assert_awaited_once_with(user_id, payload)


@pytest.mark.asyncio
async def test_delete_user_calls_repository(
    user_service: UserService, user_repository_mock: AsyncMock
):
    user_id = uuid4()

    await user_service.delete_user(user_id)

    user_repository_mock.delete.assert_awaited_once_with(user_id)
