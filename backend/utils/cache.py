"""
Redis Caching Layer
High-performance caching for prices, predictions, and API responses
"""
import redis
import json
import logging
from typing import Optional, Any, Dict
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)


class RedisCache:
    """Redis caching with automatic serialization"""
    
    def __init__(self):
        self.client = None
        self.connected = False
        
    def connect(self):
        """Connect to Redis"""
        try:
            self.client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                password=REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2  # Add timeout for operations
            )
            # Test connection
            self.client.ping()
            self.connected = True
            logger.info(f"✅ Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
            return True
        except Exception as e:
            logger.warning(f"⚠️  Redis connection failed: {e} - Using in-memory cache only")
            self.connected = False
            self.client = None  # Clear client on failure
            return False
    
    def disconnect(self):
        """Close Redis connection"""
        if self.client:
            try:
                self.client.close()
                logger.info("✅ Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis: {e}")
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> bool:
        """Set cache value with TTL (default 5 minutes)"""
        if not self.connected:
            return False
        
        try:
            # Serialize value to JSON
            serialized = json.dumps(value)
            self.client.setex(key, ttl_seconds, serialized)
            logger.debug(f"Cached {key} for {ttl_seconds}s")
            return True
        except Exception as e:
            logger.error(f"Cache set failed for {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        if not self.connected:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                logger.debug(f"Cache hit: {key}")
                return json.loads(value)
            logger.debug(f"Cache miss: {key}")
            return None
        except Exception as e:
            logger.error(f"Cache get failed for {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete cache key"""
        if not self.connected:
            return False
        
        try:
            self.client.delete(key)
            logger.debug(f"Deleted cache key: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete failed for {key}: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.connected:
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                count = self.client.delete(*keys)
                logger.info(f"Cleared {count} cache keys matching {pattern}")
                return count
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern failed: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.connected:
            return False
        
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists check failed: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """Get remaining TTL in seconds"""
        if not self.connected:
            return -1
        
        try:
            return self.client.ttl(key)
        except Exception as e:
            logger.error(f"TTL check failed: {e}")
            return -1
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter"""
        if not self.connected:
            return None
        
        try:
            return self.client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Increment failed for {key}: {e}")
            return None
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        if not self.connected:
            return {"connected": False}
        
        try:
            info = self.client.info()
            return {
                "connected": True,
                "used_memory": info.get('used_memory_human', 'unknown'),
                "connected_clients": info.get('connected_clients', 0),
                "total_commands": info.get('total_commands_processed', 0),
                "keyspace_hits": info.get('keyspace_hits', 0),
                "keyspace_misses": info.get('keyspace_misses', 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get('keyspace_hits', 0),
                    info.get('keyspace_misses', 0)
                )
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"connected": False, "error": str(e)}
    
    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage"""
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)


# Global cache instance
cache = RedisCache()


# Cache key generators
def price_key(asset_id: str) -> str:
    """Generate cache key for price data"""
    return f"price:{asset_id}"


def prediction_key(asset_id: str, horizon: int) -> str:
    """Generate cache key for predictions"""
    return f"prediction:{asset_id}:{horizon}"


def news_key(asset_name: str) -> str:
    """Generate cache key for news"""
    return f"news:{asset_name}"


def portfolio_key(user_id: str) -> str:
    """Generate cache key for portfolio"""
    return f"portfolio:{user_id}"


# Cache TTL constants (in seconds)
TTL_PRICE = 30          # 30 seconds for real-time prices
TTL_PREDICTION = 300    # 5 minutes for predictions
TTL_NEWS = 1800         # 30 minutes for news
TTL_PORTFOLIO = 60      # 1 minute for portfolio
TTL_ASSETS = 3600       # 1 hour for asset list
