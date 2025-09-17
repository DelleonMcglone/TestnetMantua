"""Redis client for session management and caching.

This module exposes a singleton Redis connection for use across the
application.  It wraps the redis-py client and provides helper
functions for setting and retrieving session and conversation data.

Redis is primarily used for:
 - storing short‑lived session data (e.g. conversation context)
 - caching expensive API responses (e.g. OpenAI completions)

The connection parameters are read from settings.redis_url.
"""

import redis
from typing import Optional

from .config import settings

_redis_instance: Optional[redis.Redis] = None


def get_redis() -> redis.Redis:
    """Return a singleton Redis client."""
    global _redis_instance
    if _redis_instance is None:
        _redis_instance = redis.Redis.from_url(settings.redis_url)
    return _redis_instance


def cache_set(key: str, value: str, ttl: int = settings.cache_ttl_seconds) -> None:
    """Store a value in Redis with an optional TTL."""
    get_redis().setex(key, ttl, value)


def cache_get(key: str) -> Optional[str]:
    """Retrieve a value from Redis or return None."""
    value = get_redis().get(key)
    return value.decode("utf-8") if value is not None else None


__all__ = ["get_redis", "cache_set", "cache_get"]