"""
Redis Integration for JWT Authentication
Migrates REVOKED_TOKENS and FAILED_LOGIN_ATTEMPTS to Redis
"""

import os
from typing import Optional
from datetime import datetime, timedelta
from security.redis_storage import get_security_storage

# Initialize Redis storage
redis_storage = get_security_storage()

# Configuration
USE_REDIS = os.getenv("USE_REDIS", "true").lower() == "true"

# Fallback to in-memory if Redis not available
if not USE_REDIS:
    print("⚠️  Redis disabled - using in-memory storage (not recommended for production)")
    REVOKED_TOKENS_MEMORY = set()
    FAILED_LOGIN_ATTEMPTS_MEMORY = {}


class RedisAuthStorage:
    """
    Redis-backed authentication storage
    Handles token revocation and failed login tracking
    """
    
    def __init__(self, use_redis: bool = True):
        self.use_redis = use_redis
        if use_redis:
            self.redis = redis_storage
        else:
            self.memory_tokens = REVOKED_TOKENS_MEMORY
            self.memory_attempts = FAILED_LOGIN_ATTEMPTS_MEMORY
    
    # ==================== Token Blacklist ====================
    
    def revoke_token(self, token: str, expires_in: int = 86400):
        """Revoke a token (add to blacklist)"""
        if self.use_redis:
            import hashlib
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            self.redis.revoke_token(token_hash, expires_in)
        else:
            self.memory_tokens.add(token)
    
    def is_token_revoked(self, token: str) -> bool:
        """Check if token is revoked"""
        if self.use_redis:
            import hashlib
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            return self.redis.is_token_revoked(token_hash)
        else:
            return token in self.memory_tokens
    
    def get_revoked_count(self) -> int:
        """Get count of revoked tokens"""
        if self.use_redis:
            return self.redis.get_revoked_tokens_count()
        else:
            return len(self.memory_tokens)
    
    # ==================== Failed Login Tracking ====================
    
    def track_failed_login(
        self,
        email: str,
        lockout_threshold: int = 5,
        lockout_duration: int = 3600
    ) -> dict:
        """
        Track failed login attempt
        
        Returns:
            {
                "count": int,
                "locked_until": str (ISO format) or None,
                "attempts_remaining": int
            }
        """
        if self.use_redis:
            return self.redis.track_failed_login(email, lockout_threshold, lockout_duration)
        else:
            # In-memory implementation
            if email not in self.memory_attempts:
                self.memory_attempts[email] = {
                    'count': 0,
                    'last_attempt': datetime.now()
                }
            
            attempt_data = self.memory_attempts[email]
            attempt_data['count'] += 1
            attempt_data['last_attempt'] = datetime.now()
            
            if attempt_data['count'] >= lockout_threshold:
                locked_until = datetime.now() + timedelta(seconds=lockout_duration)
                attempt_data['locked_until'] = locked_until
                
                return {
                    "count": attempt_data['count'],
                    "locked_until": locked_until.isoformat(),
                    "attempts_remaining": 0
                }
            
            return {
                "count": attempt_data['count'],
                "locked_until": None,
                "attempts_remaining": lockout_threshold - attempt_data['count']
            }
    
    def is_account_locked(self, email: str) -> Optional[dict]:
        """
        Check if account is locked
        
        Returns:
            {
                "locked_until": str (ISO format),
                "remaining_seconds": int
            }
            or None if not locked
        """
        if self.use_redis:
            return self.redis.is_account_locked(email)
        else:
            if email not in self.memory_attempts:
                return None
            
            attempt_data = self.memory_attempts[email]
            
            if 'locked_until' not in attempt_data:
                return None
            
            locked_until = attempt_data['locked_until']
            
            # Check if lock expired
            if datetime.now() > locked_until:
                del attempt_data['locked_until']
                attempt_data['count'] = 0
                return None
            
            remaining = (locked_until - datetime.now()).total_seconds()
            
            return {
                "locked_until": locked_until.isoformat(),
                "remaining_seconds": int(remaining)
            }
    
    def clear_failed_logins(self, email: str):
        """Clear failed login attempts for user"""
        if self.use_redis:
            self.redis.clear_failed_logins(email)
        else:
            if email in self.memory_attempts:
                del self.memory_attempts[email]
    
    def unlock_account(self, email: str):
        """Manually unlock an account"""
        if self.use_redis:
            self.redis.unlock_account(email)
        else:
            if email in self.memory_attempts:
                if 'locked_until' in self.memory_attempts[email]:
                    del self.memory_attempts[email]['locked_until']
                self.memory_attempts[email]['count'] = 0
    
    # ==================== Statistics ====================
    
    def get_stats(self) -> dict:
        """Get authentication storage statistics"""
        if self.use_redis:
            return self.redis.get_stats()
        else:
            locked_accounts = sum(
                1 for data in self.memory_attempts.values()
                if 'locked_until' in data and datetime.now() < data['locked_until']
            )
            
            return {
                "revoked_tokens": len(self.memory_tokens),
                "locked_accounts": locked_accounts,
                "failed_login_tracking": len(self.memory_attempts),
                "storage_backend": "in-memory"
            }


# Global instance
auth_storage = RedisAuthStorage(use_redis=USE_REDIS)


# Backward compatibility functions
def revoke_token(token: str):
    """Revoke a token"""
    auth_storage.revoke_token(token)

def is_token_revoked(token: str) -> bool:
    """Check if token is revoked"""
    return auth_storage.is_token_revoked(token)


if __name__ == "__main__":
    # Test the integration
    print("🧪 Testing Redis Auth Storage Integration")
    print("=" * 60)
    
    print("\n1️⃣  Testing Token Revocation...")
    test_token = "test_jwt_token_12345"
    auth_storage.revoke_token(test_token)
    print(f"   ✅ Token revoked: {auth_storage.is_token_revoked(test_token)}")
    
    print("\n2️⃣  Testing Failed Login Tracking...")
    test_email = "test@example.com"
    
    for i in range(6):
        result = auth_storage.track_failed_login(test_email)
        if result.get('locked_until'):
            print(f"   🔒 Account locked after {i+1} attempts")
            print(f"   ⏰ Locked until: {result['locked_until']}")
            break
        else:
            print(f"   ⚠️  Attempt {i+1}: {result['attempts_remaining']} remaining")
    
    print("\n3️⃣  Testing Account Lock Check...")
    lock_info = auth_storage.is_account_locked(test_email)
    if lock_info:
        print(f"   🔒 Account is locked")
        print(f"   ⏰ Remaining: {lock_info['remaining_seconds']} seconds")
    
    print("\n4️⃣  Testing Account Unlock...")
    auth_storage.unlock_account(test_email)
    print(f"   ✅ Account unlocked")
    
    print("\n5️⃣  Statistics:")
    stats = auth_storage.get_stats()
    for key, value in stats.items():
        print(f"   📊 {key}: {value}")
    
    print("\n✅ All tests completed!")
