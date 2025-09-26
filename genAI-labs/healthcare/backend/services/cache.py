"""
Healthcare ChatGPT Clone - Cache Service
This module handles Redis caching for improved performance.
"""

import logging
import json
import asyncio
from typing import Any, Optional, Dict
import redis.asyncio as redis
from redis.asyncio import Redis

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Global Redis client
_redis_client = None


def get_cache() -> Redis:
    """Get the Redis cache client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            decode_responses=True
        )
    return _redis_client


async def init_cache():
    """Initialize the cache connection."""
    try:
        cache = get_cache()
        await cache.ping()
        logger.info("Cache connection initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize cache: {e}")
        # Cache is optional, so we don't raise the exception
        logger.warning("Continuing without cache")


async def close_cache():
    """Close cache connections."""
    global _redis_client
    try:
        if _redis_client:
            await _redis_client.close()
            logger.info("Cache connection closed")
    except Exception as e:
        logger.error(f"Error closing cache connection: {e}")


async def set_cache(key: str, value: Any, expire: Optional[int] = None) -> bool:
    """Set a value in the cache."""
    try:
        cache = get_cache()
        serialized_value = json.dumps(value) if not isinstance(value, str) else value
        await cache.set(key, serialized_value, ex=expire)
        return True
    except Exception as e:
        logger.error(f"Failed to set cache key {key}: {e}")
        return False


async def get_cache(key: str) -> Optional[Any]:
    """Get a value from the cache."""
    try:
        cache = get_cache()
        value = await cache.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    except Exception as e:
        logger.error(f"Failed to get cache key {key}: {e}")
        return None


async def delete_cache(key: str) -> bool:
    """Delete a value from the cache."""
    try:
        cache = get_cache()
        await cache.delete(key)
        return True
    except Exception as e:
        logger.error(f"Failed to delete cache key {key}: {e}")
        return False


async def exists_cache(key: str) -> bool:
    """Check if a key exists in the cache."""
    try:
        cache = get_cache()
        return await cache.exists(key) > 0
    except Exception as e:
        logger.error(f"Failed to check cache key {key}: {e}")
        return False


async def expire_cache(key: str, seconds: int) -> bool:
    """Set expiration for a cache key."""
    try:
        cache = get_cache()
        await cache.expire(key, seconds)
        return True
    except Exception as e:
        logger.error(f"Failed to set expiration for cache key {key}: {e}")
        return False


async def get_cache_info() -> Dict[str, Any]:
    """Get cache information."""
    try:
        cache = get_cache()
        info = await cache.info()
        return {
            "status": "healthy",
            "connected_clients": info.get("connected_clients", 0),
            "used_memory": info.get("used_memory_human", "0B"),
            "total_commands_processed": info.get("total_commands_processed", 0),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0)
        }
    except Exception as e:
        logger.error(f"Failed to get cache info: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# Cache decorators for common use cases
def cache_result(expire: int = 3600, key_prefix: str = ""):
    """Decorator to cache function results."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = await get_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await set_cache(cache_key, result, expire)
            return result
        
        return wrapper
    return decorator


# Healthcare-specific cache functions
async def cache_user_session(user_id: str, session_data: Dict[str, Any]) -> bool:
    """Cache user session data."""
    key = f"user_session:{user_id}"
    return await set_cache(key, session_data, expire=3600)


async def get_user_session(user_id: str) -> Optional[Dict[str, Any]]:
    """Get cached user session data."""
    key = f"user_session:{user_id}"
    return await get_cache(key)


async def cache_chat_history(session_id: str, messages: list) -> bool:
    """Cache chat history for a session."""
    key = f"chat_history:{session_id}"
    return await set_cache(key, messages, expire=1800)


async def get_chat_history(session_id: str) -> Optional[list]:
    """Get cached chat history for a session."""
    key = f"chat_history:{session_id}"
    return await get_cache(key)


async def cache_knowledge_search(query: str, results: list) -> bool:
    """Cache knowledge base search results."""
    key = f"knowledge_search:{hash(query)}"
    return await set_cache(key, results, expire=3600)


async def get_cached_knowledge_search(query: str) -> Optional[list]:
    """Get cached knowledge base search results."""
    key = f"knowledge_search:{hash(query)}"
    return await get_cache(key)
