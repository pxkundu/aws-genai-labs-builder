"""
Cache service for GenAI Customer Service
Handles Redis caching operations
"""

import json
import logging
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta

import redis.asyncio as redis
import structlog

from config.settings import settings

logger = structlog.get_logger(__name__)


class CacheService:
    """Cache service for handling Redis operations"""
    
    def __init__(self, settings):
        """Initialize cache service"""
        self.settings = settings
        self.redis_client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.from_url(
                self.settings.REDIS_URL,
                db=self.settings.REDIS_DB,
                decode_responses=True
            )
            
            # Test connection
            await self.redis_client.ping()
            
            logger.info("Cache service connected successfully")
            
        except Exception as e:
            logger.error("Failed to connect to cache service", error=str(e))
            raise
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Cache service disconnected")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if not self.redis_client:
                return None
            
            value = await self.redis_client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            
            return None
            
        except Exception as e:
            logger.error("Failed to get from cache", key=key, error=str(e))
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL"""
        try:
            if not self.redis_client:
                return False
            
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            await self.redis_client.setex(key, ttl, value)
            return True
            
        except Exception as e:
            logger.error("Failed to set cache", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            if not self.redis_client:
                return False
            
            result = await self.redis_client.delete(key)
            return result > 0
            
        except Exception as e:
            logger.error("Failed to delete from cache", key=key, error=str(e))
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            if not self.redis_client:
                return False
            
            result = await self.redis_client.exists(key)
            return result > 0
            
        except Exception as e:
            logger.error("Failed to check cache existence", key=key, error=str(e))
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration for key"""
        try:
            if not self.redis_client:
                return False
            
            result = await self.redis_client.expire(key, ttl)
            return result
            
        except Exception as e:
            logger.error("Failed to set expiration", key=key, error=str(e))
            return False
    
    async def get_multiple(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache"""
        try:
            if not self.redis_client or not keys:
                return {}
            
            values = await self.redis_client.mget(keys)
            result = {}
            
            for key, value in zip(keys, values):
                if value:
                    try:
                        result[key] = json.loads(value)
                    except json.JSONDecodeError:
                        result[key] = value
            
            return result
            
        except Exception as e:
            logger.error("Failed to get multiple from cache", error=str(e))
            return {}
    
    async def set_multiple(self, data: Dict[str, Any], ttl: int = 3600) -> bool:
        """Set multiple values in cache"""
        try:
            if not self.redis_client or not data:
                return False
            
            # Prepare data for mset
            mset_data = {}
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    mset_data[key] = json.dumps(value)
                else:
                    mset_data[key] = str(value)
            
            await self.redis_client.mset(mset_data)
            
            # Set expiration for all keys
            if ttl > 0:
                pipe = self.redis_client.pipeline()
                for key in data.keys():
                    pipe.expire(key, ttl)
                await pipe.execute()
            
            return True
            
        except Exception as e:
            logger.error("Failed to set multiple in cache", error=str(e))
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter in cache"""
        try:
            if not self.redis_client:
                return None
            
            result = await self.redis_client.incrby(key, amount)
            return result
            
        except Exception as e:
            logger.error("Failed to increment counter", key=key, error=str(e))
            return None
    
    async def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """Decrement counter in cache"""
        try:
            if not self.redis_client:
                return None
            
            result = await self.redis_client.decrby(key, amount)
            return result
            
        except Exception as e:
            logger.error("Failed to decrement counter", key=key, error=str(e))
            return None
    
    async def get_keys(self, pattern: str) -> List[str]:
        """Get keys matching pattern"""
        try:
            if not self.redis_client:
                return []
            
            keys = await self.redis_client.keys(pattern)
            return keys
            
        except Exception as e:
            logger.error("Failed to get keys", pattern=pattern, error=str(e))
            return []
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            if not self.redis_client:
                return 0
            
            keys = await self.get_keys(pattern)
            if keys:
                result = await self.redis_client.delete(*keys)
                return result
            
            return 0
            
        except Exception as e:
            logger.error("Failed to clear pattern", pattern=pattern, error=str(e))
            return 0
    
    # Specific cache methods for customer service
    
    async def cache_customer_context(self, customer_id: str, 
                                   context: Dict[str, Any], 
                                   ttl: int = 3600) -> bool:
        """Cache customer context"""
        key = f"customer_context:{customer_id}"
        return await self.set(key, context, ttl)
    
    async def get_customer_context(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get cached customer context"""
        key = f"customer_context:{customer_id}"
        return await self.get(key)
    
    async def cache_conversation_state(self, session_id: str, 
                                     state: Dict[str, Any], 
                                     ttl: int = 1800) -> bool:
        """Cache conversation state"""
        key = f"conversation_state:{session_id}"
        return await self.set(key, state, ttl)
    
    async def get_conversation_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get cached conversation state"""
        key = f"conversation_state:{session_id}"
        return await self.get(key)
    
    async def cache_ai_response(self, query_hash: str, 
                              response: Dict[str, Any], 
                              ttl: int = 3600) -> bool:
        """Cache AI response"""
        key = f"ai_response:{query_hash}"
        return await self.set(key, response, ttl)
    
    async def get_cached_ai_response(self, query_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached AI response"""
        key = f"ai_response:{query_hash}"
        return await self.get(key)
    
    async def increment_request_count(self, customer_id: str, 
                                    window: str = "hour") -> int:
        """Increment request count for rate limiting"""
        key = f"request_count:{customer_id}:{window}"
        count = await self.increment(key)
        
        # Set expiration based on window
        if window == "hour":
            await self.expire(key, 3600)
        elif window == "day":
            await self.expire(key, 86400)
        
        return count or 0
    
    async def get_request_count(self, customer_id: str, 
                              window: str = "hour") -> int:
        """Get request count for rate limiting"""
        key = f"request_count:{customer_id}:{window}"
        count = await self.get(key)
        return int(count) if count else 0
