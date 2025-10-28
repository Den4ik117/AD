from __future__ import annotations

from uuid import UUID

from litestar import Controller, delete, get, post, put
from litestar.exceptions import NotFoundException
from litestar.params import Parameter
from litestar.status_codes import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from app.repositories import UserNotFoundError
from app.schemas import UserCreate, UserListResponse, UserResponse, UserUpdate
from app.services import UserService


class UserController(Controller):
    path = "/users"

    @get("/{user_id:uuid}")
    async def get_user_by_id(
        self,
        user_service: UserService,
        user_id: UUID,
    ) -> UserResponse:
        """Get a user by ID."""
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise NotFoundException(detail=f"User with ID {user_id} not found")
        return UserResponse.model_validate(user)

    @get()
    async def get_all_users(
        self,
        user_service: UserService,
        count: int = Parameter(default=10, ge=1, le=100),
        page: int = Parameter(default=1, ge=1),
    ) -> UserListResponse:
        """Return paginated users with total count."""
        users, total = await user_service.get_users(count=count, page=page)
        return UserListResponse(
            total=total,
            items=[UserResponse.model_validate(user) for user in users],
        )

    @post(status_code=HTTP_201_CREATED)
    async def create_user(
        self,
        user_service: UserService,
        user_data: UserCreate,
    ) -> UserResponse:
        """Create a new user."""
        user = await user_service.create_user(user_data)
        return UserResponse.model_validate(user)

    @delete("/{user_id:uuid}", status_code=HTTP_204_NO_CONTENT)
    async def delete_user(
        self,
        user_service: UserService,
        user_id: UUID,
    ) -> None:
        """Delete a user by ID."""
        try:
            await user_service.delete_user(user_id)
        except UserNotFoundError as exc:
            raise NotFoundException(detail=str(exc)) from exc

    @put("/{user_id:uuid}")
    async def update_user(
        self,
        user_service: UserService,
        user_id: UUID,
        user_data: UserUpdate,
    ) -> UserResponse:
        """Update a user."""
        try:
            user = await user_service.update_user(user_id, user_data)
        except UserNotFoundError as exc:
            raise NotFoundException(detail=str(exc)) from exc
        return UserResponse.model_validate(user)
