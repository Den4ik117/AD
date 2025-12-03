from __future__ import annotations

from collections.abc import AsyncIterator

from litestar import Litestar
from litestar.di import Provide
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import get_redis_client
from app.controllers import OrderController, ProductController, UserController
from app.db import get_async_db_session
from app.repositories import (
    AddressRepository,
    OrderRepository,
    ProductRepository,
    UserRepository,
)
from app.services import OrderService, ProductService, UserService


async def provide_db_session() -> AsyncIterator[AsyncSession]:
    """Провайдер сессии базы данных."""
    async for session in get_async_db_session():
        yield session


async def provide_redis_client() -> AsyncIterator[Redis]:
    """Провайдер соединения с Redis."""
    async for client in get_redis_client():
        yield client


async def provide_user_repository(db_session: AsyncSession) -> UserRepository:
    """Провайдер репозитория пользователей."""
    return UserRepository(db_session)


async def provide_product_repository(db_session: AsyncSession) -> ProductRepository:
    """Провайдер репозитория продуктов."""
    return ProductRepository(db_session)


async def provide_order_repository(db_session: AsyncSession) -> OrderRepository:
    """Провайдер репозитория заказов."""
    return OrderRepository(db_session)


async def provide_address_repository(db_session: AsyncSession) -> AddressRepository:
    """Провайдер репозитория адресов."""
    return AddressRepository(db_session)


async def provide_user_service(
    user_repository: UserRepository, redis_client: Redis
) -> UserService:
    """Провайдер сервиса пользователей."""
    return UserService(user_repository, redis_client)


async def provide_product_service(
    product_repository: ProductRepository, redis_client: Redis
) -> ProductService:
    """Провайдер сервиса продуктов."""
    return ProductService(product_repository, redis_client)


async def provide_order_service(
    order_repository: OrderRepository,
    product_repository: ProductRepository,
    user_repository: UserRepository,
    address_repository: AddressRepository,
) -> OrderService:
    """Провайдер сервиса заказов."""
    return OrderService(
        order_repository,
        product_repository,
        user_repository,
        address_repository,
    )


app = Litestar(
    route_handlers=[UserController, ProductController, OrderController],
    dependencies={
        "db_session": Provide(provide_db_session),
        "redis_client": Provide(provide_redis_client),
        "user_repository": Provide(provide_user_repository),
        "product_repository": Provide(provide_product_repository),
        "order_repository": Provide(provide_order_repository),
        "address_repository": Provide(provide_address_repository),
        "user_service": Provide(provide_user_service),
        "product_service": Provide(provide_product_service),
        "order_service": Provide(provide_order_service),
    },
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
