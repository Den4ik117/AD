from __future__ import annotations

import os
from collections.abc import AsyncIterator

from redis.asyncio import Redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


async def get_redis_client() -> AsyncIterator[Redis]:
    """Yield a Redis client configured from the environment."""
    client = Redis.from_url(REDIS_URL, decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()
