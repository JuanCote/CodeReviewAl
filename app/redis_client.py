import os
from redis.asyncio import from_url
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные из .env


class RedisClient:
    _client = None

    @classmethod
    async def get_client(cls):
        if cls._client is None:
            redis_url = os.getenv(
                "REDIS_URL", "redis://localhost:6379"
            )  # По умолчанию localhost
            cls._client = await from_url(
                redis_url, encoding="utf-8", decode_responses=True
            )
        return cls._client

    @classmethod
    async def close_client(cls):
        if cls._client:
            await cls._client.close()
            cls._client = None


async def check_redis_connection():
    redis = await RedisClient.get_client()
    try:
        pong = await redis.ping()
        if not pong:
            raise Exception("Redis connection failed")
    except Exception as e:
        raise RuntimeError(f"Redis connection error: {e}")
