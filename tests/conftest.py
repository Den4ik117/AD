from __future__ import annotations

import sys
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
import pytest_asyncio
from litestar import Litestar
from litestar.di import Provide
from litestar.testing import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.controllers import OrderController, ProductController, UserController
from app.models import Base
from app.repositories import (
    AddressRepository,
    OrderRepository,
    ProductRepository,
    UserRepository,
)
from app.services import OrderService, ProductService, UserService


@pytest.fixture(scope="function")
def db_session(tmp_path) -> Session:
    """Provide an isolated synchronous SQLite session bound to the app models."""
    db_file = tmp_path / "test.sqlite"
    engine = create_engine(f"sqlite:///{db_file}")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_engine(tmp_path) -> AsyncEngine:
    """Async engine bound to a temporary SQLite database."""
    db_file = tmp_path / "async.sqlite"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_file}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield engine
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest.fixture(scope="function")
def async_session_factory(
    async_engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Factory yielding AsyncSession instances."""
    return async_sessionmaker(async_engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def async_session(
    async_session_factory: async_sessionmaker[AsyncSession],
) -> AsyncSession:
    """Provide a transactional AsyncSession for tests."""
    async with async_session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
def api_client(async_session_factory: async_sessionmaker[AsyncSession]) -> TestClient:
    """Litestar test client wired to the temporary async database."""

    async def provide_db_session() -> AsyncIterator[AsyncSession]:
        async with async_session_factory() as session:
            yield session

    async def provide_user_repository(db_session: AsyncSession) -> UserRepository:
        return UserRepository(db_session)

    async def provide_product_repository(
        db_session: AsyncSession,
    ) -> ProductRepository:
        return ProductRepository(db_session)

    async def provide_order_repository(db_session: AsyncSession) -> OrderRepository:
        return OrderRepository(db_session)

    async def provide_address_repository(
        db_session: AsyncSession,
    ) -> AddressRepository:
        return AddressRepository(db_session)

    async def provide_user_service(user_repository: UserRepository) -> UserService:
        return UserService(user_repository)

    async def provide_product_service(
        product_repository: ProductRepository,
    ) -> ProductService:
        return ProductService(product_repository)

    async def provide_order_service(
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        user_repository: UserRepository,
        address_repository: AddressRepository,
    ) -> OrderService:
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
            "user_repository": Provide(provide_user_repository),
            "product_repository": Provide(provide_product_repository),
            "order_repository": Provide(provide_order_repository),
            "address_repository": Provide(provide_address_repository),
            "user_service": Provide(provide_user_service),
            "product_service": Provide(provide_product_service),
            "order_service": Provide(provide_order_service),
        },
    )

    with TestClient(app=app) as client:
        yield client
