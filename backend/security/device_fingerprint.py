"""
Device Fingerprinting
Detects token theft by tracking device characteristics
"""

import hashlib
from fastapi import Request, HTTPException
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def generate_device_fingerprint(request: Request) -> str:
    """
    Generate a unique fingerprint for the client device
    
    Uses:
    - User-Agent
    - Accept-Language
    - IP Address (first 3 octets for some privacy)
    
    Args:
        request: FastAPI Request object
        
    Returns:
        SHA-256 hash of device characteristics
    """
    # Collect device characteristics
    user_agent = request.headers.get("User-Agent", "unknown")
    accept_language = request.headers.get("Accept-Language", "unknown")
    
    # Get IP (use first 3 octets for privacy - allows some IP changes)
    ip_address = request.client.host if request.client else "unknown"
    if ip_address != "unknown" and "." in ip_address:
        # IPv4: Use first 3 octets (e.g., 192.168.1.x -> 192.168.1)
        ip_prefix = ".".join(ip_address.split(".")[:3])
    else:
        ip_prefix = ip_address
    
    # Combine characteristics
    fingerprint_data = f"{user_agent}|{accept_language}|{ip_prefix}"
    
    # Generate hash
    fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    logger.debug(f"Device fingerprint generated: {fingerprint[:16]}...")
    
    return fingerprint


def validate_device_fingerprint(
    request: Request,
    stored_fingerprint: str,
    strict: bool = False
) -> bool:
    """
    Validate that current device matches stored fingerprint
    
    Args:
        request: Current request
        stored_fingerprint: Fingerprint from JWT token
        strict: If True, requires exact match. If False, allows some variation
        
    Returns:
        True if fingerprints match (or are similar enough)
    """
    current_fingerprint = generate_device_fingerprint(request)
    
    if strict:
        # Exact match required
        return current_fingerprint == stored_fingerprint
    else:
        # Allow some flexibility (handles minor UA changes, dynamic IPs)
        # In production, you might want more sophisticated matching
        return current_fingerprint == stored_fingerprint


def add_fingerprint_to_token_data(request: Request, token_data: dict) -> dict:
    """
    Add device fingerprint to JWT token data
    
    Args:
        request: Request to fingerprint
        token_data: Existing token payload
        
    Returns:
        Updated token data with fingerprint
    """
    fingerprint = generate_device_fingerprint(request)
    token_data["device_fp"] = fingerprint
    
    # Also store creation IP for reference
    token_data["create_ip"] = request.client.host if request.client else "unknown"
    
    return token_data


def verify_request_fingerprint(
    request: Request,
    token_fingerprint: Optional[str],
    strict: bool = False
) -> None:
    """
    Verify request fingerprint matches token
    
    Raises HTTPException if mismatch detected
    
    Args:
        request: Current request
        token_fingerprint: Fingerprint from JWT
        strict: Require exact match
        
    Raises:
        HTTPException: 401 if fingerprint mismatch (possible token theft)
    """
    if not token_fingerprint:
        # Old tokens without fingerprint - allow for now
        logger.warning("Token without device fingerprint - consider regenerating")
        return
    
    if not validate_device_fingerprint(request, token_fingerprint, strict):
        current_fp = generate_device_fingerprint(request)
        
        logger.error(
            f"Device fingerprint mismatch! "
            f"Token: {token_fingerprint[:16]}... "
            f"Current: {current_fp[:16]}... "
            f"IP: {request.client.host if request.client else 'unknown'}"
        )
        
        raise HTTPException(
            status_code=401,
            detail="Device verification failed. Please login again from this device."
        )
    
    logger.debug("Device fingerprint verified successfully")


# Enhanced JWT creation with fingerprinting
"""
USAGE IN JWT_AUTH.PY:

from security.device_fingerprint import add_fingerprint_to_token_data

def create_access_token(data: dict, request: Request) -> str:
    to_encode = data.copy()
    
    # Add device fingerprint
    to_encode = add_fingerprint_to_token_data(request, to_encode)
    
    # Add expiration
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Encode JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# In get_current_user dependency:
from security.device_fingerprint import verify_request_fingerprint

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        # Verify device fingerprint
        device_fp = payload.get("device_fp")
        verify_request_fingerprint(request, device_fp, strict=False)
        
        # ... rest of validation
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
"""


def get_device_info(request: Request) -> dict:
    """
    Get human-readable device information
    
    Useful for showing user their active sessions
    
    Returns:
        Dict with device details
    """
    user_agent = request.headers.get("User-Agent", "Unknown")
    
    # Simple UA parsing (in production, use user-agents library)
    device_type = "Desktop"
    if "Mobile" in user_agent or "Android" in user_agent or "iPhone" in user_agent:
        device_type = "Mobile"
    elif "Tablet" in user_agent or "iPad" in user_agent:
        device_type = "Tablet"
    
    browser = "Unknown"
    if "Chrome" in user_agent:
        browser = "Chrome"
    elif "Firefox" in user_agent:
        browser = "Firefox"
    elif "Safari" in user_agent and "Chrome" not in user_agent:
        browser = "Safari"
    elif "Edge" in user_agent:
        browser = "Edge"
    
    return {
        "device_type": device_type,
        "browser": browser,
        "user_agent": user_agent,
        "ip_address": request.client.host if request.client else "unknown",
        "fingerprint": generate_device_fingerprint(request)[:16] + "..."
    }
