"""
JWT Authentication Module
Provides user authentication with JWT tokens
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
import secrets

# Configuration
SECRET_KEY = secrets.token_urlsafe(32)  # Generate secure key (store in .env in production!)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing - Using SHA256 instead of bcrypt to avoid 72-byte limit issues
import hashlib

def hash_password_sha256(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password_sha256(plain_password: str, hashed_password: str) -> bool:
    """Verify password using SHA256"""
    return hash_password_sha256(plain_password) == hashed_password

# Password hashing - Switched to SHA256 for simplicity
# pwd_context = CryptContext(
#     schemes=["bcrypt"],
#     deprecated="auto",
#     bcrypt__truncate_error=False
# )

# HTTP Bearer token security
security = HTTPBearer()

# Security events integration
try:
    from security.security_events import (
        notify_account_locked,
        log_successful_login,
        log_failed_login,
        notify_2fa_enabled,
        notify_2fa_disabled
    )
    SECURITY_EVENTS_ENABLED = True
except ImportError:
    SECURITY_EVENTS_ENABLED = False
    notify_account_locked = lambda *args, **kwargs: None
    log_successful_login = lambda *args, **kwargs: None
    log_failed_login = lambda *args, **kwargs: None
    notify_2fa_enabled = lambda *args, **kwargs: None
    notify_2fa_disabled = lambda *args, **kwargs: None

# In-memory user database (replace with real database in production)
USERS_DB = {}

# Security tracking - REDIS DISABLED (using in-memory only)
# Redis integration COMPLETELY DISABLED
USE_REDIS_AUTH = False
print("⚠️  Redis authentication storage DISABLED - using in-memory")

# In-memory fallback storage
FAILED_LOGIN_ATTEMPTS = {}
REVOKED_TOKENS = set()

# Dummy Redis objects (not used, but must be defined for type checking)
class DummyAuthStorage:
    def is_account_locked(self, email): return None
    def track_failed_login(self, email, **kwargs): return {'count': 0}
    def get_failed_login_count(self, email): return 0
    def clear_failed_logins(self, email): pass

auth_storage = DummyAuthStorage()
def redis_revoke_token(token): pass
def redis_is_token_revoked(token): return False

# Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    disabled: bool = False
    created_at: datetime
    two_factor_enabled: bool = False

class UserInDB(User):
    hashed_password: str
    two_factor_secret: Optional[str] = None
    backup_codes: Optional[list[str]] = None

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Optional[User] = None

class TokenData(BaseModel):
    email: Optional[str] = None


# Password utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash using SHA256"""
    return hash_password_sha256(plain_password) == hashed_password

def get_password_hash(password: str) -> str:
    """Hash a password using SHA256"""
    return hash_password_sha256(password)

def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    Returns: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    if not (has_upper and has_lower and has_digit):
        return False, "Password must contain uppercase, lowercase, and numbers"
    
    if not has_special:
        return False, "Password must contain at least one special character"
    
    return True, ""


# User database operations
def get_user(email: str) -> Optional[UserInDB]:
    """Get user from database"""
    user_dict = USERS_DB.get(email)
    if user_dict:
        return UserInDB(**user_dict)
    return None

def create_user(user_create: UserCreate) -> User:
    """Create a new user"""
    # Check if user already exists
    if user_create.email in USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password strength
    is_valid, error_msg = validate_password_strength(user_create.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Create user
    hashed_password = get_password_hash(user_create.password)
    now = datetime.now()
    user_dict = {
        "email": user_create.email,
        "full_name": user_create.full_name,
        "hashed_password": hashed_password,
        "disabled": False,
        "created_at": now,
        "two_factor_enabled": False
    }
    
    USERS_DB[user_create.email] = user_dict
    
    return User(
        email=user_dict["email"],
        full_name=user_dict["full_name"],
        disabled=user_dict["disabled"],
        created_at=now,
        two_factor_enabled=False
    )

def authenticate_user(email: str, password: str, check_2fa: bool = True) -> Optional[UserInDB]:
    """
    Authenticate a user with email and password
    
    Args:
        email: User's email
        password: User's password
        check_2fa: If True, check if 2FA is enabled (for regular login)
                  If False, skip 2FA check (for 2FA login endpoint)
    """
    # Check if account is locked
    if USE_REDIS_AUTH:
        lock_info = auth_storage.is_account_locked(email)
        if lock_info:
            remaining = lock_info.get('remaining_seconds', 0)
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Account locked due to multiple failed login attempts. Try again in {remaining} seconds."
            )
    else:
        if email in FAILED_LOGIN_ATTEMPTS:
            attempt_data = FAILED_LOGIN_ATTEMPTS[email]
            
            # Check if still locked
            if 'locked_until' in attempt_data:
                if datetime.now() < attempt_data['locked_until']:
                    remaining = (attempt_data['locked_until'] - datetime.now()).seconds
                    raise HTTPException(
                        status_code=status.HTTP_423_LOCKED,
                        detail=f"Account locked due to multiple failed login attempts. Try again in {remaining} seconds."
                    )
                else:
                    # Lock expired, remove it
                    del attempt_data['locked_until']
                    attempt_data['count'] = 0
    
    user = get_user(email)
    if not user:
        # Track failed attempt (even for non-existent users to prevent enumeration)
        _track_failed_login(email)
        return None
    
    if not verify_password(password, user.hashed_password):
        # Track failed attempt
        _track_failed_login(email)
        if SECURITY_EVENTS_ENABLED:
            # Get current attempt count
            if USE_REDIS_AUTH:
                attempt_count = auth_storage.get_failed_login_count(email) if hasattr(auth_storage, 'get_failed_login_count') else 1
            else:
                attempt_count = FAILED_LOGIN_ATTEMPTS.get(email, {}).get('count', 1)
            log_failed_login(email, "unknown", attempt_count)
        return None
    
    # Successful login - clear failed attempts
    if USE_REDIS_AUTH:
        auth_storage.clear_failed_logins(email)
    else:
        if email in FAILED_LOGIN_ATTEMPTS:
            del FAILED_LOGIN_ATTEMPTS[email]
    
    # Log successful login
    if SECURITY_EVENTS_ENABLED:
        log_successful_login(email, "unknown", "unknown")
    
    return user


def _track_failed_login(email: str):
    """Track failed login attempts and lock account if needed"""
    if USE_REDIS_AUTH:
        # Use Redis storage
        result = auth_storage.track_failed_login(email, lockout_threshold=5, lockout_duration=3600)
        
        if result.get('locked_until'):
            # Send lockout notification
            if SECURITY_EVENTS_ENABLED:
                notify_account_locked(email, "unknown", result['count'])
            
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account locked due to multiple failed login attempts. Please try again in 1 hour."
            )
        
        if result['count'] >= 3:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid credentials. {result['attempts_remaining']} attempts remaining before account lockout.",
                headers={"WWW-Authenticate": "Bearer"}
            )
    else:
        # In-memory fallback
        if email not in FAILED_LOGIN_ATTEMPTS:
            FAILED_LOGIN_ATTEMPTS[email] = {
                'count': 0,
                'last_attempt': datetime.now()
            }
        
        attempt_data = FAILED_LOGIN_ATTEMPTS[email]
        attempt_data['count'] += 1
        attempt_data['last_attempt'] = datetime.now()
        
        # Lock account after 5 failed attempts
        if attempt_data['count'] >= 5:
            # Lock for 1 hour
            attempt_data['locked_until'] = datetime.now() + timedelta(hours=1)
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account locked due to multiple failed login attempts. Please try again in 1 hour."
            )
        
        # If 3-4 attempts, warn user
        if attempt_data['count'] >= 3:
            remaining_attempts = 5 - attempt_data['count']
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid credentials. {remaining_attempts} attempts remaining before account lockout.",
                headers={"WWW-Authenticate": "Bearer"}
            )



# JWT token operations
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> Optional[TokenData]:
    """Verify and decode a JWT token"""
    import hashlib
    
    # Check if token is blacklisted (revoked)
    if USE_REDIS_AUTH:
        if redis_is_token_revoked(token):
            return None
    else:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        if token_hash in REVOKED_TOKENS:
            return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        token_type_in_payload: str = payload.get("type")
        
        if email is None or token_type_in_payload != token_type:
            return None
        
        return TokenData(email=email)
    except JWTError:
        return None


def revoke_token(token: str):
    """Add token to blacklist (for logout)"""
    import hashlib
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    REVOKED_TOKENS.add(token_hash)



# Dependencies for protected routes
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Dependency to get the current authenticated user
    Use this in protected endpoints: current_user: User = Depends(get_current_user)
    """
    token = credentials.credentials
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_token(token, token_type="access")
    if token_data is None or token_data.email is None:
        raise credentials_exception
    
    user = get_user(email=token_data.email)
    if user is None:
        raise credentials_exception
    
    return User(**{k: v for k, v in user.dict().items() if k != "hashed_password"})

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get the current active (non-disabled) user
    """
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


# Helper functions for endpoints
def login_user(user_login: UserLogin) -> Token:
    """
    Login a user and return access and refresh tokens
    """
    user = authenticate_user(user_login.email, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is disabled"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )

def refresh_access_token(refresh_token: str) -> Token:
    """
    Refresh an access token using a valid refresh token
    """
    token_data = verify_token(refresh_token, token_type="refresh")
    
    if token_data is None or token_data.email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user(email=token_data.email)
    if user is None or user.disabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or disabled"
        )
    
    # Create new access token
    access_token = create_access_token(data={"sub": user.email})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token  # Return the same refresh token
    )

def revoke_token(token: str):
    """
    Revoke a token (add to blacklist)
    Used for logout functionality
    """
    if USE_REDIS_AUTH:
        redis_revoke_token(token)
    else:
        import hashlib
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        REVOKED_TOKENS.add(token_hash)

# Demo user for testing (remove in production!)
def create_demo_user():
    """Create a demo user for testing"""
    try:
        demo_user = UserCreate(
            email="demo@example.com",
            password="Demo123!",
            full_name="Demo User"
        )
        create_user(demo_user)
        print("✅ Demo user created: demo@example.com / Demo123!")
    except HTTPException:
        pass  # User already exists

# Create demo user on module import (commented out - bcrypt issue)
# create_demo_user()
