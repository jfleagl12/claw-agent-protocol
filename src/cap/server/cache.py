"""
Cache Manager

Provides in-memory caching for CAP data to reduce API calls.
"""

from typing import Any, Optional
import time
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self, ttl: int = 300):
        """
        Initialize the cache manager.
        
        Args:
            ttl: Time-to-live in seconds
        """
        self.ttl = ttl
        self._cache: dict[str, tuple[Any, float]] = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            return None
        
        value, expires_at = self._cache[key]
        
        if time.time() > expires_at:
            # Expired
            del self._cache[key]
            return None
        
        logger.debug(f"Cache hit: {key}")
        return value
    
    async def set(self, key: str, value: Any) -> None:
        """
        Set a value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        expires_at = time.time() + self.ttl
        self._cache[key] = (value, expires_at)
        logger.debug(f"Cache set: {key} (TTL: {self.ttl}s)")
    
    async def clear(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        return {
            "size": len(self._cache),
            "ttl": self.ttl
        }
