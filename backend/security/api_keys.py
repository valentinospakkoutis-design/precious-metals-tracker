"""
Security Module - API Key Authentication
Provides API key-based authentication for external access
"""

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader, APIKeyQuery
from typing import Optional
import secrets
import hashlib
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# API Key configurations
API_KEY_NAME = "X-API-Key"
API_KEY_QUERY_NAME = "api_key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_query = APIKeyQuery(name=API_KEY_QUERY_NAME, auto_error=False)

# In-memory API keys storage (In production, use database)
# Format: {hashed_key: {"name": str, "created": datetime, "expires": datetime, "active": bool}}
API_KEYS = {}

def hash_api_key(key: str) -> str:
    """Hash API key using SHA-256"""
    return hashlib.sha256(key.encode()).hexdigest()

def generate_api_key() -> str:
    """Generate a secure random API key"""
    return secrets.token_urlsafe(32)

def create_api_key(name: str, expires_days: int = 365) -> str:
    """
    Create a new API key
    
    Args:
        name: Descriptive name for the key (e.g., "Mobile App", "Web Dashboard")
        expires_days: Number of days until expiration
        
    Returns:
        The unhashed API key (store this securely, it won't be shown again)
    """
    api_key = generate_api_key()
    hashed_key = hash_api_key(api_key)
    
    API_KEYS[hashed_key] = {
        "name": name,
        "created": datetime.now(),
        "expires": datetime.now() + timedelta(days=expires_days),
        "active": True,
        "last_used": None,
        "usage_count": 0
    }
    
    logger.info(f"API key created: {name}")
    return api_key

def revoke_api_key(api_key: str):
    """Revoke an API key"""
    hashed_key = hash_api_key(api_key)
    if hashed_key in API_KEYS:
        API_KEYS[hashed_key]["active"] = False
        logger.info(f"API key revoked: {API_KEYS[hashed_key]['name']}")
    else:
        logger.warning(f"Attempted to revoke unknown API key")

def validate_api_key(api_key: str) -> bool:
    """
    Validate an API key
    
    Returns:
        True if key is valid and active, False otherwise
    """
    if not api_key:
        return False
        
    hashed_key = hash_api_key(api_key)
    
    if hashed_key not in API_KEYS:
        logger.warning(f"Invalid API key attempted")
        return False
    
    key_data = API_KEYS[hashed_key]
    
    # Check if key is active
    if not key_data["active"]:
        logger.warning(f"Revoked API key attempted: {key_data['name']}")
        return False
    
    # Check if key is expired
    if datetime.now() > key_data["expires"]:
        logger.warning(f"Expired API key attempted: {key_data['name']}")
        return False
    
    # Update usage statistics
    key_data["last_used"] = datetime.now()
    key_data["usage_count"] += 1
    
    return True

async def get_api_key(
    api_key_header: str = Security(api_key_header),
    api_key_query: str = Security(api_key_query),
) -> str:
    """
    Dependency to validate API key from header or query parameter
    
    Usage:
        @app.get("/protected")
        async def protected_route(api_key: str = Depends(get_api_key)):
            return {"message": "Access granted"}
    """
    # Try header first, then query parameter
    api_key = api_key_header or api_key_query
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Provide it via X-API-Key header or api_key query parameter."
        )
    
    if not validate_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired API key"
        )
    
    return api_key

# Optional: API key for specific scopes
SCOPES = {
    "read": ["GET"],
    "write": ["POST", "PUT", "PATCH"],
    "delete": ["DELETE"],
    "admin": ["GET", "POST", "PUT", "PATCH", "DELETE"]
}

def create_scoped_api_key(name: str, scopes: list[str], expires_days: int = 365) -> str:
    """Create API key with specific scopes/permissions"""
    api_key = generate_api_key()
    hashed_key = hash_api_key(api_key)
    
    API_KEYS[hashed_key] = {
        "name": name,
        "created": datetime.now(),
        "expires": datetime.now() + timedelta(days=expires_days),
        "active": True,
        "scopes": scopes,
        "last_used": None,
        "usage_count": 0
    }
    
    logger.info(f"Scoped API key created: {name} with scopes: {scopes}")
    return api_key

def check_scope(api_key: str, required_scope: str) -> bool:
    """Check if API key has required scope"""
    hashed_key = hash_api_key(api_key)
    if hashed_key not in API_KEYS:
        return False
    
    key_data = API_KEYS[hashed_key]
    if "scopes" not in key_data:
        return True  # No scopes defined = full access (backward compatibility)
    
    return required_scope in key_data["scopes"]

# Initialize with a default API key for testing
DEFAULT_API_KEY = create_api_key("Default Testing Key", expires_days=365)
logger.info(f"Default API key created for testing: {DEFAULT_API_KEY}")
logger.info("Store this key securely - it will not be shown again!")
