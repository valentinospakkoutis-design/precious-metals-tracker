"""
Security Module
Comprehensive security implementation for FastAPI application

Components:
- Rate Limiting: Protect against DDoS and abuse
- API Key Authentication: External access control
- Input Sanitization: XSS and injection protection
- CORS Configuration: Secure cross-origin requests
"""

from .rate_limiting import (
    limiter,
    rate_limit_exceeded_handler,
    rate_limit_predict,
    rate_limit_portfolio,
    rate_limit_price,
    rate_limit_auth,
    check_ip_blacklist,
    blacklist_ip,
    whitelist_ip,
    check_request_size,
)

from .api_keys import (
    get_api_key,
    create_api_key,
    revoke_api_key,
    validate_api_key,
    create_scoped_api_key,
    check_scope,
    DEFAULT_API_KEY,
)

from .sanitization import (
    sanitize_string,
    sanitize_asset_id,
    sanitize_number,
    sanitize_email,
    sanitize_url,
    sanitize_dict,
    is_safe_sql_param,
    validate_sql_params,
    contains_dangerous_content,
)

from .cors_config import (
    configure_cors,
    configure_strict_cors,
    get_cors_origins,
)

from .csrf_protection import (
    csrf_protect,
    CsrfProtectError,
)

__all__ = [
    # Rate Limiting
    "limiter",
    "rate_limit_exceeded_handler",
    "rate_limit_predict",
    "rate_limit_portfolio",
    "rate_limit_price",
    "rate_limit_auth",
    "check_ip_blacklist",
    "blacklist_ip",
    "whitelist_ip",
    "check_request_size",
    
    # API Keys
    "get_api_key",
    "create_api_key",
    "revoke_api_key",
    "validate_api_key",
    "create_scoped_api_key",
    "check_scope",
    "DEFAULT_API_KEY",
    
    # Sanitization
    "sanitize_string",
    "sanitize_asset_id",
    "sanitize_number",
    "sanitize_email",
    "sanitize_url",
    "sanitize_dict",
    "is_safe_sql_param",
    "validate_sql_params",
    "contains_dangerous_content",
    
    # CORS
    "configure_cors",
    "configure_strict_cors",
    "get_cors_origins",
    
    # CSRF Protection
    "csrf_protect",
    "CsrfProtectError",
]
