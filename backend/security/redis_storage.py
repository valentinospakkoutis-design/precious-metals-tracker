"""
Redis Persistence Layer
Move REVOKED_TOKENS and FAILED_LOGIN_ATTEMPTS to Redis
"""

import redis
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json
import logging
import os

logger = logging.getLogger(__name__)


class RedisSecurityStorage:
    """
    Redis-backed storage for security features
    
    Provides persistence for:
    - Revoked tokens
    - Failed login attempts
    - Account lockouts
    - Rate limiting
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        decode_responses: bool = True
    ):
        """
        Initialize Redis connection
        
        Args:
            host: Redis server host
            port: Redis server port
            db: Redis database number
            password: Redis password (if required)
            decode_responses: Auto-decode bytes to strings
        """
        self.client = None
        self.connected = False
        
        try:
            self.client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=decode_responses,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            
            # Test connection
            self.client.ping()
            self.connected = True
            logger.info(f"✅ Connected to Redis at {host}:{port}")
        except redis.ConnectionError as e:
            logger.warning(f"⚠️  Failed to connect to Redis: {e} - Using in-memory fallback")
            self.connected = False
            self.client = None
    
    # Token Blacklist Methods
    
    def revoke_token(self, token_hash: str, expires_in: int = 86400) -> None:
        """
        Add token to blacklist
        
        Args:
            token_hash: SHA-256 hash of token
            expires_in: Seconds until auto-removal (default: 24 hours)
        """
        if not self.connected or not self.client:
            return
        key = f"revoked_token:{token_hash}"
        self.client.setex(key, expires_in, datetime.now().isoformat())
        logger.info(f"Token revoked (expires in {expires_in}s)")
    
    def is_token_revoked(self, token_hash: str) -> bool:
        """
        Check if token is revoked
        
        Args:
            token_hash: SHA-256 hash of token
            
        Returns:
            True if token is in blacklist
        """
        if not self.connected or not self.client:
            return False
        key = f"revoked_token:{token_hash}"
        return self.client.exists(key) > 0
    
    def get_revoked_tokens_count(self) -> int:
        """Get total count of revoked tokens"""
        keys = self.client.keys("revoked_token:*")
        return len(keys)
    
    # Failed Login Tracking
    
    def track_failed_login(
        self,
        email: str,
        lockout_threshold: int = 5,
        lockout_duration: int = 3600
    ) -> Dict[str, Any]:
        """
        Track failed login attempt
        
        Args:
            email: User email
            lockout_threshold: Failed attempts before lockout
            lockout_duration: Lockout duration in seconds
            
        Returns:
            Dict with count, locked_until, attempts_remaining
        """
        key = f"failed_login:{email}"
        
        # Increment counter
        count = self.client.incr(key)
        
        # Set expiry on first attempt (resets after 1 hour of no attempts)
        if count == 1:
            self.client.expire(key, 3600)
        
        # Check if should lock
        if count >= lockout_threshold:
            locked_until = datetime.now() + timedelta(seconds=lockout_duration)
            lock_key = f"account_locked:{email}"
            self.client.setex(lock_key, lockout_duration, locked_until.isoformat())
            
            logger.warning(f"Account locked: {email} (until {locked_until})")
            
            return {
                "count": count,
                "locked_until": locked_until.isoformat(),
                "attempts_remaining": 0
            }
        
        return {
            "count": count,
            "locked_until": None,
            "attempts_remaining": lockout_threshold - count
        }
    
    def is_account_locked(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Check if account is locked
        
        Args:
            email: User email
            
        Returns:
            Dict with locked_until and remaining_seconds, or None
        """
        lock_key = f"account_locked:{email}"
        locked_until_str = self.client.get(lock_key)
        
        if not locked_until_str:
            return None
        
        locked_until = datetime.fromisoformat(locked_until_str)
        remaining = (locked_until - datetime.now()).total_seconds()
        
        return {
            "locked_until": locked_until_str,
            "remaining_seconds": int(remaining)
        }
    
    def clear_failed_logins(self, email: str) -> None:
        """
        Clear failed login attempts (after successful login)
        
        Args:
            email: User email
        """
        key = f"failed_login:{email}"
        self.client.delete(key)
    
    def unlock_account(self, email: str) -> None:
        """
        Manually unlock account
        
        Args:
            email: User email
        """
        lock_key = f"account_locked:{email}"
        failed_key = f"failed_login:{email}"
        
        self.client.delete(lock_key)
        self.client.delete(failed_key)
        
        logger.info(f"Account unlocked manually: {email}")
    
    # Rate Limiting (complement to SlowAPI)
    
    def check_rate_limit(
        self,
        key: str,
        limit: int,
        window: int = 60
    ) -> Dict[str, Any]:
        """
        Check rate limit for a key
        
        Args:
            key: Unique identifier (e.g., IP, user_id, endpoint)
            limit: Maximum requests allowed
            window: Time window in seconds
            
        Returns:
            Dict with allowed, remaining, reset_at
        """
        rate_key = f"rate_limit:{key}"
        
        # Get current count
        current = self.client.get(rate_key)
        
        if current is None:
            # First request in window
            self.client.setex(rate_key, window, 1)
            return {
                "allowed": True,
                "remaining": limit - 1,
                "reset_at": (datetime.now() + timedelta(seconds=window)).isoformat()
            }
        
        current = int(current)
        
        if current >= limit:
            # Rate limit exceeded
            ttl = self.client.ttl(rate_key)
            return {
                "allowed": False,
                "remaining": 0,
                "reset_at": (datetime.now() + timedelta(seconds=ttl)).isoformat()
            }
        
        # Increment counter
        self.client.incr(rate_key)
        ttl = self.client.ttl(rate_key)
        
        return {
            "allowed": True,
            "remaining": limit - current - 1,
            "reset_at": (datetime.now() + timedelta(seconds=ttl)).isoformat()
        }
    
    # Session Management
    
    def store_session(
        self,
        session_id: str,
        user_data: dict,
        expires_in: int = 1800
    ) -> None:
        """
        Store user session
        
        Args:
            session_id: Unique session identifier
            user_data: User session data
            expires_in: Session expiration in seconds (default: 30 min)
        """
        key = f"session:{session_id}"
        self.client.setex(key, expires_in, json.dumps(user_data))
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data"""
        key = f"session:{session_id}"
        data = self.client.get(key)
        return json.loads(data) if data else None
    
    def delete_session(self, session_id: str) -> None:
        """Delete session"""
        key = f"session:{session_id}"
        self.client.delete(key)
    
    # Statistics
    
    def get_stats(self) -> dict:
        """Get storage statistics"""
        return {
            "revoked_tokens": len(self.client.keys("revoked_token:*")),
            "locked_accounts": len(self.client.keys("account_locked:*")),
            "failed_login_tracking": len(self.client.keys("failed_login:*")),
            "active_sessions": len(self.client.keys("session:*")),
            "rate_limits_active": len(self.client.keys("rate_limit:*"))
        }
    
    def clear_all_security_data(self) -> None:
        """Clear all security data (use with caution!)"""
        patterns = [
            "revoked_token:*",
            "account_locked:*",
            "failed_login:*",
            "rate_limit:*"
        ]
        
        for pattern in patterns:
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
        
        logger.warning("All security data cleared from Redis")
    
    def close(self):
        """Close Redis connection"""
        self.client.close()


# Initialize global instance
def get_redis_storage() -> RedisSecurityStorage:
    """
    Get Redis storage instance
    
    Uses environment variables for configuration:
    - REDIS_HOST (default: localhost)
    - REDIS_PORT (default: 6379)
    - REDIS_DB (default: 0)
    - REDIS_PASSWORD (optional)
    """
    return RedisSecurityStorage(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=int(os.getenv("REDIS_DB", 0)),
        password=os.getenv("REDIS_PASSWORD")
    )


# Global instance (lazy initialization)
_redis_storage: Optional[RedisSecurityStorage] = None


def get_security_storage() -> RedisSecurityStorage:
    """Get or create global Redis storage instance"""
    global _redis_storage
    
    if _redis_storage is None:
        _redis_storage = get_redis_storage()
    
    return _redis_storage


# Usage in jwt_auth.py
"""
REPLACE IN-MEMORY STORAGE:

# OLD:
FAILED_LOGIN_ATTEMPTS = {}
REVOKED_TOKENS = set()

# NEW:
from security.redis_storage import get_security_storage

redis_storage = get_security_storage()

# Replace track_failed_login:
def authenticate_user(email: str, password: str):
    # Check if locked
    lock_info = redis_storage.is_account_locked(email)
    if lock_info:
        raise HTTPException(
            status_code=423,
            detail=f"Account locked. Try again in {lock_info['remaining_seconds']}s"
        )
    
    # Verify password
    user = get_user(email)
    if not user or not verify_password(password, user.hashed_password):
        # Track failed attempt
        result = redis_storage.track_failed_login(email)
        raise HTTPException(
            status_code=401,
            detail=f"Invalid credentials. {result['attempts_remaining']} attempts remaining"
        )
    
    # Success - clear failed attempts
    redis_storage.clear_failed_logins(email)
    return user

# Replace revoke_token:
def revoke_token(token: str):
    import hashlib
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    redis_storage.revoke_token(token_hash, expires_in=86400)

# Replace token check in get_current_user:
async def get_current_user(credentials):
    token = credentials.credentials
    
    # Check if revoked
    import hashlib
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    if redis_storage.is_token_revoked(token_hash):
        raise HTTPException(status_code=401, detail="Token has been revoked")
    
    # ... rest of validation
"""


# Testing
if __name__ == "__main__":
    try:
        # Test Redis connection
        storage = get_security_storage()
        
        # Test failed login tracking
        print("\n🔐 Testing Failed Login Tracking:")
        for i in range(6):
            result = storage.track_failed_login("test@example.com")
            print(f"  Attempt {i+1}: {result}")
        
        # Test account lock check
        print("\n🔒 Testing Account Lock:")
        lock_info = storage.is_account_locked("test@example.com")
        print(f"  Locked: {lock_info}")
        
        # Test token revocation
        print("\n🎫 Testing Token Revocation:")
        storage.revoke_token("test_token_hash_123")
        is_revoked = storage.is_token_revoked("test_token_hash_123")
        print(f"  Token revoked: {is_revoked}")
        
        # Test rate limiting
        print("\n⏱️ Testing Rate Limiting:")
        for i in range(6):
            result = storage.check_rate_limit("test_ip", limit=5, window=60)
            print(f"  Request {i+1}: {result}")
        
        # Get stats
        print("\n📊 Storage Statistics:")
        stats = storage.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Cleanup
        storage.unlock_account("test@example.com")
        
    except redis.ConnectionError:
        print("❌ Redis not running. Start Redis with: redis-server")
    except Exception as e:
        print(f"❌ Error: {e}")
