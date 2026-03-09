import os

import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST: str | None = os.getenv("REDIS_HOST")
REDIS_PORT: str | None = os.getenv("REDIS_PORT")


def create_redis_client() -> redis.Redis:
    """
    Create and return a Redis client instance.
    """
    return redis.Redis(
        host=REDIS_HOST,
        port=int(REDIS_PORT) if REDIS_PORT is not None else 6379,
        decode_responses=True
    )


redis_client: redis.Redis = create_redis_client()