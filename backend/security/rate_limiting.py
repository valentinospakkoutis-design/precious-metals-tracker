"""
Security Module - Rate Limiting
Protects API from abuse and DDoS attacks
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
from typing import Callable
import logging

logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],  # Global limit
    storage_uri="redis://localhost:6379/1",  # Separate Redis DB for rate limiting
    strategy="fixed-window"
)

# Custom rate limit configurations for different endpoints
RATE_LIMITS = {
    # Critical endpoints - stricter limits
    "predict": "10/minute",      # ML predictions are expensive
    "backtest": "5/minute",      # Backtesting is CPU-intensive
    "portfolio": "30/minute",    # Portfolio operations
    
    # Read endpoints - more permissive
    "price": "60/minute",        # Price data
    "assets": "120/minute",      # Asset lists
    "health": "300/minute",      # Health checks
    
    # Authentication - very strict
    "login": "5/minute",         # Prevent brute force
    "register": "3/hour",        # Prevent spam accounts
}

def get_rate_limit(endpoint: str) -> str:
    """Get rate limit for specific endpoint"""
    return RATE_LIMITS.get(endpoint, "100/minute")

async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded"""
    logger.warning(f"Rate limit exceeded for {request.client.host} on {request.url.path}")
    
    return {
        "error": True,
        "status_code": 429,
        "message": "Rate limit exceeded. Please try again later.",
        "retry_after": exc.retry_after if hasattr(exc, 'retry_after') else 60,
        "limit": str(exc.limit) if hasattr(exc, 'limit') else "unknown",
        "path": str(request.url.path),
    }

# Decorators for different rate limits
def rate_limit_predict(func: Callable):
    """Rate limit for prediction endpoints"""
    return limiter.limit(RATE_LIMITS["predict"])(func)

def rate_limit_portfolio(func: Callable):
    """Rate limit for portfolio endpoints"""
    return limiter.limit(RATE_LIMITS["portfolio"])(func)

def rate_limit_price(func: Callable):
    """Rate limit for price endpoints"""
    return limiter.limit(RATE_LIMITS["price"])(func)

def rate_limit_auth(func: Callable):
    """Rate limit for authentication endpoints"""
    return limiter.limit(RATE_LIMITS["login"])(func)


# IP Blacklist (for blocking malicious IPs)
BLACKLISTED_IPS = set()

async def check_ip_blacklist(request: Request):
    """Check if IP is blacklisted"""
    client_ip = request.client.host
    if client_ip in BLACKLISTED_IPS:
        logger.error(f"Blacklisted IP attempted access: {client_ip}")
        raise HTTPException(
            status_code=403,
            detail="Access denied. Your IP has been blacklisted."
        )

def blacklist_ip(ip: str):
    """Add IP to blacklist"""
    BLACKLISTED_IPS.add(ip)
    logger.info(f"IP added to blacklist: {ip}")

def whitelist_ip(ip: str):
    """Remove IP from blacklist"""
    BLACKLISTED_IPS.discard(ip)
    logger.info(f"IP removed from blacklist: {ip}")


# Request size limits
MAX_REQUEST_SIZE = 1024 * 1024  # 1MB

async def check_request_size(request: Request):
    """Prevent large payload attacks"""
    content_length = request.headers.get('content-length')
    if content_length and int(content_length) > MAX_REQUEST_SIZE:
        logger.warning(f"Large request blocked: {content_length} bytes from {request.client.host}")
        raise HTTPException(
            status_code=413,
            detail=f"Request too large. Maximum size: {MAX_REQUEST_SIZE} bytes"
        )
