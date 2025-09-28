"""
Redis cache configuration and utilities
"""

import json
import logging
from typing import Any, Optional
import redis.asyncio as redis
from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Global cache instance
_cache: Optional[redis.Redis] = None


async def init_cache():
    """Initialize Redis cache connection"""
    global _cache
    try:
        _cache = redis.from_url(
            settings.REDIS_URL,
            password=settings.REDIS_PASSWORD,
            encoding="utf-8",
            decode_responses=True
        )
        
        # Test connection
        await _cache.ping()
        logger.info("Redis cache initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing Redis cache: {str(e)}")
        # In development, continue without cache
        if settings.ENVIRONMENT == "development":
            logger.warning("Continuing without cache in development mode")
            _cache = None
        else:
            raise


def get_cache() -> Optional[redis.Redis]:
    """Get Redis cache instance"""
    return _cache


class CacheManager:
    """Cache management utilities"""
    
    def __init__(self):
        self.cache = get_cache()
        self.default_ttl = settings.CACHE_TTL
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.cache:
            return None
        
        try:
            value = await self.cache.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {str(e)}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        if not self.cache:
            return False
        
        try:
            ttl = ttl or self.default_ttl
            serialized_value = json.dumps(value, default=str)
            await self.cache.set(key, serialized_value, ex=ttl)
            return True
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.cache:
            return False
        
        try:
            await self.cache.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {str(e)}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.cache:
            return False
        
        try:
            return bool(await self.cache.exists(key))
        except Exception as e:
            logger.error(f"Error checking cache key {key}: {str(e)}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.cache:
            return 0
        
        try:
            keys = await self.cache.keys(pattern)
            if keys:
                return await self.cache.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error clearing cache pattern {pattern}: {str(e)}")
            return 0


# Global cache manager instance
cache_manager = CacheManager()
