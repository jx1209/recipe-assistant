"""
Authentication Handler
Manages JWT tokens, password hashing, and user authentication
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings from environment or defaults
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Security scheme
security = HTTPBearer()


class AuthHandler:
    """Authentication handler for user management"""
    
    def __init__(self, db_manager=None):
        """Initialize auth handler"""
        self.db_manager = db_manager
        self.pwd_context = pwd_context
    
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        # Bcrypt has a 72 byte limit
        # Pre-truncate to avoid any bcrypt errors
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            # Truncate to 72 bytes
            password_bytes = password_bytes[:72]
            # Decode back, ignoring any incomplete multi-byte characters
            password = password_bytes.decode('utf-8', errors='ignore')
        
        try:
            return pwd_context.hash(password)
        except (ValueError, TypeError) as e:
            # Catch any bcrypt errors and try with a shorter password
            error_msg = str(e).lower()
            if "72" in error_msg or "too long" in error_msg or "byte" in error_msg:
                # Be very conservative - truncate to 70 bytes to be safe
                password_safe = password.encode('utf-8')[:70].decode('utf-8', errors='ignore')
                return pwd_context.hash(password_safe)
            raise
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(32),  # JWT ID for blacklisting
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(32),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError as e:
            logger.error(f"Token verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user with email and password"""
        if not self.db_manager:
            raise ValueError("Database manager not initialized")
        
        user = self.db_manager.get_user_by_email(email)
        
        if not user:
            return None
        
        if not self.verify_password(password, user['password_hash']):
            return None
        
        return user
    
    def check_token_blacklist(self, jti: str) -> bool:
        """Check if token is blacklisted"""
        if not self.db_manager:
            return False
        
        return self.db_manager.is_token_blacklisted(jti)
    
    def blacklist_token(self, token: str) -> bool:
        """Add token to blacklist"""
        if not self.db_manager:
            return False
        
        try:
            payload = self.verify_token(token)
            jti = payload.get("jti")
            user_id = payload.get("sub")
            exp = payload.get("exp")
            
            if not jti or not user_id or not exp:
                return False
            
            expires_at = datetime.fromtimestamp(exp)
            self.db_manager.blacklist_token(jti, int(user_id), expires_at)
            return True
        except Exception as e:
            logger.error(f"Error blacklisting token: {e}")
            return False


# Global auth handler instance
_auth_handler: Optional[AuthHandler] = None


def get_auth_handler() -> AuthHandler:
    """Get or create auth handler instance"""
    global _auth_handler
    if _auth_handler is None:
        from src.database import get_db
        _auth_handler = AuthHandler(db_manager=get_db())
    return _auth_handler


# Convenience functions
def get_password_hash(password: str) -> str:
    """Hash a password"""
    # Bcrypt has a 72 byte limit
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        password = password_bytes.decode('utf-8', errors='ignore')
    
    try:
        return pwd_context.hash(password)
    except (ValueError, TypeError) as e:
        error_msg = str(e).lower()
        if "72" in error_msg or "too long" in error_msg or "byte" in error_msg:
            password_safe = password.encode('utf-8')[:70].decode('utf-8', errors='ignore')
            return pwd_context.hash(password_safe)
        raise


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create access token"""
    return get_auth_handler().create_access_token(data, expires_delta)


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create refresh token"""
    return get_auth_handler().create_refresh_token(data, expires_delta)


def verify_token(token: str) -> Dict[str, Any]:
    """Verify token"""
    return get_auth_handler().verify_token(token)


# Dependency for protected routes
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Get current authenticated user from token"""
    from src.database import get_db
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = verify_token(token)
        
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        jti: str = payload.get("jti")
        
        if user_id is None or token_type != "access":
            raise credentials_exception
        
        # Check if token is blacklisted
        auth_handler = get_auth_handler()
        if auth_handler.check_token_blacklist(jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    db = get_db()
    user = db.get_user_by_id(int(user_id))
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get current active user"""
    if not current_user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[Dict[str, Any]]:
    """Get user if token is provided, None otherwise (for optional authentication)"""
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None

