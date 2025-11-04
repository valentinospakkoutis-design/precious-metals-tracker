"""
Security Module - CORS Configuration
Secure Cross-Origin Resource Sharing configuration
"""

from fastapi.middleware.cors import CORSMiddleware
from typing import List

# Production CORS settings
PRODUCTION_ORIGINS = [
    "https://yourapp.com",
    "https://www.yourapp.com",
    "https://app.yourapp.com",
]

# Development CORS settings (more permissive)
DEVELOPMENT_ORIGINS = [
    "http://localhost:3000",       # React dev server
    "http://localhost:8080",       # Vue dev server
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
    "http://localhost:5173",       # Vite dev server
]

# Mobile app origins (if using web views)
MOBILE_ORIGINS = [
    "capacitor://localhost",       # Capacitor
    "ionic://localhost",           # Ionic
    "http://localhost",            # Cordova
]

def get_cors_origins(environment: str = "development") -> List[str]:
    """
    Get CORS origins based on environment
    
    Args:
        environment: "development", "production", or "testing"
    """
    if environment == "production":
        return PRODUCTION_ORIGINS + MOBILE_ORIGINS
    elif environment == "testing":
        return ["*"]  # Allow all in testing (use with caution)
    else:  # development
        return DEVELOPMENT_ORIGINS + PRODUCTION_ORIGINS + MOBILE_ORIGINS

def configure_cors(app, environment: str = "development"):
    """
    Configure CORS middleware for FastAPI app
    
    Usage:
        from security.cors_config import configure_cors
        configure_cors(app, environment="production")
    """
    origins = get_cors_origins(environment)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "X-API-Key",
            "X-Request-ID",
            "Accept",
            "Origin",
        ],
        expose_headers=[
            "X-Total-Count",
            "X-Page",
            "X-Per-Page",
            "X-Rate-Limit-Remaining",
            "X-Rate-Limit-Reset",
        ],
        max_age=600,  # Cache preflight requests for 10 minutes
    )

# Strict CORS configuration (for highly sensitive endpoints)
def configure_strict_cors(app):
    """
    Configure strict CORS (production only, no wildcards)
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=PRODUCTION_ORIGINS,  # No wildcards
        allow_credentials=True,
        allow_methods=["GET", "POST"],     # Only read and create
        allow_headers=["Content-Type", "X-API-Key"],
        expose_headers=[],
        max_age=300,
    )
