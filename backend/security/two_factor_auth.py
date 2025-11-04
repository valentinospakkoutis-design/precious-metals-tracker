"""
Two-Factor Authentication (2FA)
TOTP-based implementation using pyotp
"""

import pyotp
import qrcode
from io import BytesIO
import base64
from typing import Optional, Tuple
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


class TwoFactorAuth:
    """
    TOTP-based Two-Factor Authentication
    
    Uses Google Authenticator compatible tokens
    """
    
    def __init__(self, issuer_name: str = "Financial Prediction API"):
        self.issuer_name = issuer_name
    
    def generate_secret(self) -> str:
        """
        Generate a new secret key for 2FA
        
        Returns:
            Base32 encoded secret key
        """
        return pyotp.random_base32()
    
    def get_provisioning_uri(self, email: str, secret: str) -> str:
        """
        Generate provisioning URI for QR code
        
        Args:
            email: User's email address
            secret: User's 2FA secret
            
        Returns:
            otpauth:// URI for QR code generation
        """
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=email,
            issuer_name=self.issuer_name
        )
    
    def generate_qr_code(self, email: str, secret: str) -> str:
        """
        Generate QR code image as base64 string
        
        Args:
            email: User's email
            secret: User's 2FA secret
            
        Returns:
            Base64 encoded PNG image
        """
        uri = self.get_provisioning_uri(email, secret)
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_base64}"
    
    def verify_token(self, secret: str, token: str, window: int = 1) -> bool:
        """
        Verify a TOTP token
        
        Args:
            secret: User's 2FA secret
            token: 6-digit code from authenticator app
            window: Number of time windows to check (allows for time drift)
            
        Returns:
            True if token is valid
        """
        totp = pyotp.TOTP(secret)
        
        try:
            # Remove any spaces or dashes
            token = token.replace(" ", "").replace("-", "")
            
            # Verify token (allows ±1 time window for clock drift)
            return totp.verify(token, valid_window=window)
        except Exception as e:
            logger.error(f"2FA verification error: {e}")
            return False
    
    def get_current_token(self, secret: str) -> str:
        """
        Get current valid token (for testing)
        
        Args:
            secret: User's 2FA secret
            
        Returns:
            Current 6-digit token
        """
        totp = pyotp.TOTP(secret)
        return totp.now()
    
    def generate_backup_codes(self, count: int = 10) -> list:
        """
        Generate backup codes for account recovery
        
        Args:
            count: Number of backup codes to generate
            
        Returns:
            List of backup codes
        """
        import secrets
        return [
            f"{secrets.randbelow(10000):04d}-{secrets.randbelow(10000):04d}"
            for _ in range(count)
        ]


# Global 2FA instance
two_factor_auth = TwoFactorAuth()


# Database models (add to your User model)
"""
Add to UserInDB model:

class UserInDB(BaseModel):
    email: str
    hashed_password: str
    full_name: Optional[str] = None
    disabled: bool = False
    
    # 2FA fields
    two_factor_enabled: bool = False
    two_factor_secret: Optional[str] = None
    backup_codes: list = []  # Hashed backup codes
"""


# FastAPI endpoints
"""
USAGE IN API:

from security.two_factor_auth import two_factor_auth, TwoFactorAuth
from pydantic import BaseModel

class Enable2FARequest(BaseModel):
    email: str
    password: str

class Verify2FARequest(BaseModel):
    email: str
    password: str
    token: str

class TwoFactorResponse(BaseModel):
    secret: str
    qr_code: str
    backup_codes: list

@app.post("/api/v1/auth/2fa/enable", response_model=TwoFactorResponse)
async def enable_2fa(request: Enable2FARequest):
    '''
    Enable 2FA for user
    
    Steps:
    1. Verify password
    2. Generate secret
    3. Return QR code
    4. User scans QR code
    5. User verifies with token (separate endpoint)
    '''
    # Verify user password
    user = authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate secret
    secret = two_factor_auth.generate_secret()
    
    # Generate QR code
    qr_code = two_factor_auth.generate_qr_code(request.email, secret)
    
    # Generate backup codes
    backup_codes = two_factor_auth.generate_backup_codes()
    
    # Store secret temporarily (confirm with token verification)
    # In production, store in database with user
    
    return {
        "secret": secret,
        "qr_code": qr_code,
        "backup_codes": backup_codes
    }


@app.post("/api/v1/auth/2fa/verify")
async def verify_2fa_setup(request: Verify2FARequest):
    '''
    Verify 2FA setup with first token
    
    After user scans QR code, they enter first token to confirm
    '''
    # Get user's temporary secret
    user = get_user(request.email)
    
    # Verify token
    if not two_factor_auth.verify_token(user.two_factor_secret, request.token):
        raise HTTPException(status_code=400, detail="Invalid token")
    
    # Enable 2FA for user
    user.two_factor_enabled = True
    update_user(user)
    
    return {"message": "2FA enabled successfully"}


@app.post("/api/v1/auth/login")
async def login_with_2fa(credentials: UserLogin):
    '''
    Modified login to support 2FA
    '''
    # Step 1: Verify password
    user = authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Step 2: Check if 2FA is enabled
    if user.two_factor_enabled:
        # Return special response requiring 2FA token
        return {
            "requires_2fa": True,
            "message": "Please provide 2FA token"
        }
    
    # No 2FA, issue token normally
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/v1/auth/login/2fa")
async def complete_login_with_2fa(
    email: str,
    password: str,
    token: str
):
    '''
    Complete login with 2FA token
    '''
    # Verify password again
    user = authenticate_user(email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify 2FA token
    if not two_factor_auth.verify_token(user.two_factor_secret, token):
        # Log failed 2FA attempt
        security_logger.log_failed_2fa(email, get_client_ip(request))
        raise HTTPException(status_code=401, detail="Invalid 2FA token")
    
    # Issue access token
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/v1/auth/2fa/disable")
async def disable_2fa(
    current_user: User = Depends(get_current_user),
    token: str
):
    '''
    Disable 2FA (requires current token for verification)
    '''
    # Verify current 2FA token
    if not two_factor_auth.verify_token(current_user.two_factor_secret, token):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Disable 2FA
    current_user.two_factor_enabled = False
    current_user.two_factor_secret = None
    current_user.backup_codes = []
    update_user(current_user)
    
    return {"message": "2FA disabled successfully"}


@app.post("/api/v1/auth/2fa/backup-code")
async def use_backup_code(email: str, password: str, backup_code: str):
    '''
    Login using backup code (if 2FA device is lost)
    '''
    # Verify password
    user = authenticate_user(email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify backup code
    import hashlib
    code_hash = hashlib.sha256(backup_code.encode()).hexdigest()
    
    if code_hash not in user.backup_codes:
        raise HTTPException(status_code=401, detail="Invalid backup code")
    
    # Remove used backup code
    user.backup_codes.remove(code_hash)
    update_user(user)
    
    # Issue token
    access_token = create_access_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Backup code used. Please regenerate backup codes."
    }
"""


# Testing
if __name__ == "__main__":
    # Test 2FA flow
    tfa = TwoFactorAuth()
    
    # Generate secret
    secret = tfa.generate_secret()
    print(f"Secret: {secret}")
    
    # Generate QR code
    qr_code = tfa.generate_qr_code("user@example.com", secret)
    print(f"QR Code (base64): {qr_code[:100]}...")
    
    # Get current token
    token = tfa.get_current_token(secret)
    print(f"Current Token: {token}")
    
    # Verify token
    is_valid = tfa.verify_token(secret, token)
    print(f"Token Valid: {is_valid}")
    
    # Generate backup codes
    backup_codes = tfa.generate_backup_codes()
    print(f"Backup Codes: {backup_codes}")
