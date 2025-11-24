"""
User management API routes
Handles authentication, registration, and user profile management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import logging
import json

from src.models.user import (
    UserCreate, UserLogin, UserProfile, UserUpdate, 
    UserPreferences, TokenResponse
)
from src.auth.auth_handler import (
    get_auth_handler, get_current_active_user,
    create_access_token, create_refresh_token, verify_token
)
from src.database import get_db
from src.models.pantry import PantryItemCreate, PantryItemUpdate, PantryItemResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])
user_router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """
    Register a new user
    
    - **email**: User email address (must be unique)
    - **password**: Password (min 8 chars, must include uppercase, lowercase, and digit)
    - **full_name**: Optional full name
    """
    db = get_db()
    auth_handler = get_auth_handler()
    
    # Check if user already exists
    existing_user = db.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    password_hash = auth_handler.hash_password(user_data.password)
    
    # Create user
    try:
        user_id = db.create_user(
            email=user_data.email,
            password_hash=password_hash,
            full_name=user_data.full_name
        )
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user_id)})
    refresh_token = create_refresh_token(data={"sub": str(user_id)})
    
    logger.info(f"New user registered: {user_data.email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=30 * 60  # 30 minutes
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """
    Login with email and password
    
    Returns access and refresh tokens
    """
    auth_handler = get_auth_handler()
    
    # Authenticate user
    user = auth_handler.authenticate_user(credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user['id'])})
    refresh_token = create_refresh_token(data={"sub": str(user['id'])})
    
    logger.info(f"User logged in: {credentials.email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=30 * 60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token_data: Dict[str, str]):
    """
    Refresh access token using refresh token
    
    - **refresh_token**: Valid refresh token
    """
    refresh_token = refresh_token_data.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token is required"
        )
    
    try:
        payload = verify_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Create new access token
        new_access_token = create_access_token(data={"sub": user_id})
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=refresh_token,  # Return same refresh token
            expires_in=30 * 60
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


@router.post("/logout")
async def logout(current_user: Dict = Depends(get_current_active_user)):
    """
    Logout current user (blacklist token)
    
    Requires authentication
    """
    # Note: In a stateless JWT system, logout is handled client-side
    # Here we can optionally blacklist the token
    logger.info(f"User logged out: {current_user['email']}")
    
    return {"message": "Successfully logged out"}


@user_router.get("/me", response_model=UserProfile)
async def get_current_user_profile(current_user: Dict = Depends(get_current_active_user)):
    """
    Get current user profile
    
    Requires authentication
    """
    try:
        preferences = json.loads(current_user.get('preferences_json', '{}'))
    except:
        preferences = {}
    
    return UserProfile(
        id=current_user['id'],
        email=current_user['email'],
        full_name=current_user.get('full_name'),
        created_at=current_user['created_at'],
        is_verified=current_user.get('is_verified', False),
        preferences=preferences,
        height=current_user.get('height'),
        weight=current_user.get('weight'),
        sex=current_user.get('sex'),
        body_type=current_user.get('body_type'),
        bmi=current_user.get('bmi')
    )


@user_router.put("/me", response_model=UserProfile)
async def update_current_user(
    user_update: UserUpdate,
    current_user: Dict = Depends(get_current_active_user)
):
    """
    Update current user profile
    
    Requires authentication
    """
    db = get_db()
    
    update_data = user_update.dict(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    # Check if email is being updated and if it's already in use
    if 'email' in update_data:
        existing_user = db.get_user_by_email(update_data['email'])
        if existing_user and existing_user['id'] != current_user['id']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
    
    # Update user
    success = db.update_user(current_user['id'], **update_data)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )
    
    # Get updated user
    updated_user = db.get_user_by_id(current_user['id'])
    
    try:
        preferences = json.loads(updated_user.get('preferences_json', '{}'))
    except:
        preferences = {}
    
    logger.info(f"User profile updated: {current_user['email']}")
    
    return UserProfile(
        id=updated_user['id'],
        email=updated_user['email'],
        full_name=updated_user.get('full_name'),
        created_at=updated_user['created_at'],
        is_verified=updated_user.get('is_verified', False),
        preferences=preferences,
        height=updated_user.get('height'),
        weight=updated_user.get('weight'),
        sex=updated_user.get('sex'),
        body_type=updated_user.get('body_type'),
        bmi=updated_user.get('bmi')
    )


@user_router.put("/me/preferences", response_model=UserProfile)
async def update_user_preferences(
    preferences: UserPreferences,
    current_user: Dict = Depends(get_current_active_user)
):
    """
    Update user preferences (dietary restrictions, allergies, etc.)
    
    Requires authentication
    """
    db = get_db()
    
    # Convert preferences to JSON
    preferences_json = preferences.dict()
    
    # Update user preferences
    success = db.update_user_preferences(current_user['id'], preferences_json)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences"
        )
    
    # Get updated user
    updated_user = db.get_user_by_id(current_user['id'])
    
    try:
        user_preferences = json.loads(updated_user.get('preferences_json', '{}'))
    except:
        user_preferences = {}
    
    logger.info(f"User preferences updated: {current_user['email']}")
    
    return UserProfile(
        id=updated_user['id'],
        email=updated_user['email'],
        full_name=updated_user.get('full_name'),
        created_at=updated_user['created_at'],
        is_verified=updated_user.get('is_verified', False),
        preferences=user_preferences,
        height=updated_user.get('height'),
        weight=updated_user.get('weight'),
        sex=updated_user.get('sex'),
        body_type=updated_user.get('body_type'),
        bmi=updated_user.get('bmi')
    )


@user_router.get("/me/pantry", response_model=list[PantryItemResponse])
async def get_user_pantry(current_user: Dict = Depends(get_current_active_user)):
    """
    Get all items in user's pantry
    
    Requires authentication
    """
    db = get_db()
    
    pantry_items = db.get_user_pantry(current_user['id'])
    
    return [PantryItemResponse(**item) for item in pantry_items]


@user_router.post("/me/pantry", response_model=PantryItemResponse, status_code=status.HTTP_201_CREATED)
async def add_pantry_item(
    item: PantryItemCreate,
    current_user: Dict = Depends(get_current_active_user)
):
    """
    Add item to user's pantry
    
    Requires authentication
    """
    db = get_db()
    
    item_id = db.add_pantry_item(
        user_id=current_user['id'],
        ingredient_name=item.ingredient_name,
        quantity=item.quantity,
        unit=item.unit,
        category=item.category,
        expiration_date=item.expiration_date.isoformat() if item.expiration_date else None
    )
    
    # Get the created item
    with db.get_cursor() as cursor:
        cursor.execute("SELECT * FROM user_pantry WHERE id = ?", (item_id,))
        pantry_item = dict(cursor.fetchone())
    
    logger.info(f"Pantry item added for user {current_user['email']}: {item.ingredient_name}")
    
    return PantryItemResponse(**pantry_item)


@user_router.put("/me/pantry/{item_id}", response_model=PantryItemResponse)
async def update_pantry_item(
    item_id: int,
    item_update: PantryItemUpdate,
    current_user: Dict = Depends(get_current_active_user)
):
    """
    Update pantry item
    
    Requires authentication
    """
    db = get_db()
    
    # Verify item belongs to user
    with db.get_cursor() as cursor:
        cursor.execute("SELECT user_id FROM user_pantry WHERE id = ?", (item_id,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pantry item not found"
            )
        
        if result['user_id'] != current_user['id']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this item"
            )
    
    # Update item
    update_data = item_update.dict(exclude_unset=True)
    if 'expiration_date' in update_data and update_data['expiration_date']:
        update_data['expiration_date'] = update_data['expiration_date'].isoformat()
    
    success = db.update_pantry_item(item_id, **update_data)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update pantry item"
        )
    
    # Get updated item
    with db.get_cursor() as cursor:
        cursor.execute("SELECT * FROM user_pantry WHERE id = ?", (item_id,))
        pantry_item = dict(cursor.fetchone())
    
    return PantryItemResponse(**pantry_item)


@user_router.delete("/me/pantry/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pantry_item(
    item_id: int,
    current_user: Dict = Depends(get_current_active_user)
):
    """
    Delete pantry item
    
    Requires authentication
    """
    db = get_db()
    
    # Verify item belongs to user
    with db.get_cursor() as cursor:
        cursor.execute("SELECT user_id FROM user_pantry WHERE id = ?", (item_id,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pantry item not found"
            )
        
        if result['user_id'] != current_user['id']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this item"
            )
    
    # Delete item
    success = db.delete_pantry_item(item_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete pantry item"
        )
    
    logger.info(f"Pantry item deleted for user {current_user['email']}: {item_id}")
    
    return None

