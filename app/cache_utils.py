import json
from typing import Any, Optional
from app.redis_client import RedisClient


async def get_from_cache(key: str) -> Optional[Any]:
    """
    Get a value from Redis cache.

    :param key: The cache key.
    :return: The cached value, or None if not found.
    """
    redis = await RedisClient.get_client()
    cached_value = await redis.get(key)
    if cached_value:
        return json.loads(cached_value)
    return None


async def set_to_cache(key: str, value: Any, expiration: int = 3600):
    """
    Set a value in Redis cache.

    :param key: The cache key.
    :param value: The value to cache.
    :param expiration: Expiration time in seconds (default is 1 hour).
    """
    redis = await RedisClient.get_client()
    await redis.set(key, json.dumps(value), ex=expiration)
