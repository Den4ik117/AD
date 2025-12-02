from __future__ import annotations

import os
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Async database configuration shared between the API and background consumers.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://ad:ad@127.0.0.1:5432/ad")

engine = create_async_engine(DATABASE_URL, echo=True)
async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_async_db_session() -> AsyncIterator[AsyncSession]:
    """Yield a database session for dependency injection."""
    async with async_session_factory() as session:
        yield session
