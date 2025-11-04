"""
Security Module - Input Sanitization
Protects against XSS, SQL injection, and other injection attacks
"""

import re
from typing import Any
import html
import logging

logger = logging.getLogger(__name__)

# Dangerous patterns to detect
DANGEROUS_PATTERNS = [
    r"<script",           # XSS
    r"javascript:",       # XSS
    r"on\w+\s*=",        # Event handlers
    r"<iframe",          # Iframe injection
    r"<object",          # Object injection
    r"<embed",           # Embed injection
    r"\.\.\/",           # Path traversal
    r"union\s+select",   # SQL injection
    r"drop\s+table",     # SQL injection
    r"exec\s*\(",        # Code execution
    r"eval\s*\(",        # Code execution
    r"__import__",       # Python injection
]

# Compile patterns for performance
DANGEROUS_REGEX = [re.compile(pattern, re.IGNORECASE) for pattern in DANGEROUS_PATTERNS]

def contains_dangerous_content(text: str) -> bool:
    """Check if text contains dangerous patterns"""
    if not isinstance(text, str):
        return False
    
    for pattern in DANGEROUS_REGEX:
        if pattern.search(text):
            return True
    return False

def sanitize_string(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input string
    
    - HTML escapes dangerous characters
    - Removes null bytes
    - Limits length
    - Detects dangerous patterns
    """
    if not isinstance(text, str):
        return str(text)
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Check for dangerous patterns
    if contains_dangerous_content(text):
        logger.warning(f"Dangerous pattern detected in input: {text[:50]}...")
        raise ValueError("Input contains potentially dangerous content")
    
    # HTML escape
    text = html.escape(text)
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
        logger.warning(f"Input truncated to {max_length} characters")
    
    return text

def sanitize_asset_id(asset_id: str) -> str:
    """
    Sanitize asset ID (only allows alphanumeric and underscore)
    """
    if not asset_id:
        raise ValueError("Asset ID cannot be empty")
    
    # Only allow uppercase letters, numbers, and hyphen
    if not re.match(r'^[A-Z0-9\-]+$', asset_id):
        raise ValueError("Asset ID must contain only uppercase letters, numbers, and hyphens")
    
    if len(asset_id) > 20:
        raise ValueError("Asset ID too long (max 20 characters)")
    
    return asset_id

def sanitize_number(value: Any, min_value: float = None, max_value: float = None) -> float:
    """
    Sanitize numeric input
    """
    try:
        num = float(value)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid number: {value}")
    
    if min_value is not None and num < min_value:
        raise ValueError(f"Number must be >= {min_value}")
    
    if max_value is not None and num > max_value:
        raise ValueError(f"Number must be <= {max_value}")
    
    return num

def sanitize_email(email: str) -> str:
    """Sanitize email address"""
    email = email.strip().lower()
    
    # Basic email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValueError("Invalid email format")
    
    return email

def sanitize_url(url: str) -> str:
    """Sanitize URL"""
    url = url.strip()
    
    # Only allow http and https
    if not url.startswith(('http://', 'https://')):
        raise ValueError("URL must start with http:// or https://")
    
    # Check for dangerous content
    if contains_dangerous_content(url):
        raise ValueError("URL contains dangerous content")
    
    return url

def sanitize_dict(data: dict, allowed_keys: set = None) -> dict:
    """
    Sanitize dictionary
    
    - Removes keys not in allowed_keys (if provided)
    - Sanitizes string values
    - Validates numeric values
    """
    sanitized = {}
    
    for key, value in data.items():
        # Check if key is allowed
        if allowed_keys and key not in allowed_keys:
            logger.warning(f"Unauthorized key removed: {key}")
            continue
        
        # Sanitize value based on type
        if isinstance(value, str):
            sanitized[key] = sanitize_string(value)
        elif isinstance(value, (int, float)):
            sanitized[key] = value  # Already validated by Pydantic
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value, allowed_keys)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_string(item) if isinstance(item, str) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized

# SQL Injection protection (already handled by parameterized queries, but extra layer)
def is_safe_sql_param(value: Any) -> bool:
    """
    Check if value is safe to use as SQL parameter
    (This is redundant if using parameterized queries, but provides extra safety)
    """
    if isinstance(value, (int, float, bool)):
        return True
    
    if isinstance(value, str):
        # Check for SQL injection patterns
        dangerous_sql = [
            'union', 'select', 'insert', 'update', 'delete', 'drop',
            'create', 'alter', 'exec', 'execute', '--', ';', '/*', '*/'
        ]
        value_lower = value.lower()
        return not any(pattern in value_lower for pattern in dangerous_sql)
    
    return False

def validate_sql_params(*params) -> bool:
    """Validate multiple SQL parameters"""
    return all(is_safe_sql_param(param) for param in params)
