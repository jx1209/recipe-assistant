"""
authentication dependencies for fastapi routes
provides current user dependency for protected endpoints
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

from src.auth.auth_handler import AuthHandler
from src.database import get_db
from src.models.user import UserResponse
from src.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)


def get_auth_handler() -> AuthHandler:
    """dependency to get auth handler"""
    return AuthHandler(settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_handler: AuthHandler = Depends(get_auth_handler)
) -> UserResponse:
    """
    dependency to get current authenticated user
    validates jwt token and returns user data
    
    raises:
        httpexception 401: if token is invalid or user not found
    """
    try:
        token = credentials.credentials
        
        #validate token
        payload = auth_handler.decode_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        #check if token is blacklisted
        if auth_handler.is_token_blacklisted(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="token has been revoked",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        #get user from database
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid token payload",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        db = get_db(settings.DATABASE_URL)
        user = db.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="user not found",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="user account is inactive",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"error validating user token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional),
    auth_handler: AuthHandler = Depends(get_auth_handler)
) -> Optional[UserResponse]:
    """
    optional authentication dependency
    returns user if authenticated, none if not
    useful for endpoints that work with or without auth
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = auth_handler.decode_token(token)
        
        if not payload or auth_handler.is_token_blacklisted(token):
            return None
        
        user_id = payload.get("user_id")
        if not user_id:
            return None
        
        db = get_db(settings.DATABASE_URL)
        user = db.get_user_by_id(user_id)
        
        if not user or not user.is_active:
            return None
        
        return user
        
    except Exception:
        return None


async def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    dependency to get current active user
    additional check for active status
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user account is inactive"
        )
    return current_user


async def get_current_verified_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    dependency to get current verified user
    requires email verification
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="email verification required"
        )
    return current_user

