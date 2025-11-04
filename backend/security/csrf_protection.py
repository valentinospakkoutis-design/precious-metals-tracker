"""
CSRF Protection Module
Protects against Cross-Site Request Forgery attacks
"""

from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from pydantic import BaseModel
import secrets

class CsrfSettings(BaseModel):
    """CSRF configuration settings"""
    secret_key: str = secrets.token_urlsafe(32)
    cookie_samesite: str = "strict"
    cookie_secure: bool = False  # Set to True in production with HTTPS
    cookie_httponly: bool = True

@CsrfProtect.load_config
def get_csrf_config():
    """Load CSRF configuration"""
    return CsrfSettings()

# Initialize CSRF protection
csrf_protect = CsrfProtect()

__all__ = ['csrf_protect', 'CsrfProtectError']
