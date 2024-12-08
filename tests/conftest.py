from typing import AsyncIterator
import fakeredis
import pytest_asyncio
import redis

from app.redis_client import RedisClient


@pytest_asyncio.fixture(loop_scope="session")
async def redis_client() -> AsyncIterator[redis.Redis]:
    async with fakeredis.FakeAsyncRedis() as client:
        RedisClient._client = client
        yield client
