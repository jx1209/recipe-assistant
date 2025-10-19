"""
User-related Pydantic models
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserCreate(BaseModel):
    """Model for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=100)
    
    @validator('password')
    def password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    """Model for user login"""
    email: EmailStr
    password: str


class UserProfile(BaseModel):
    """Model for user profile response"""
    id: int
    email: EmailStr
    full_name: Optional[str]
    created_at: datetime
    is_verified: bool
    preferences: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Model for updating user profile"""
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None


class UserPreferences(BaseModel):
    """Model for user preferences"""
    dietary_restrictions: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    favorite_cuisines: List[str] = Field(default_factory=list)
    disliked_ingredients: List[str] = Field(default_factory=list)
    default_servings: int = Field(default=4, ge=1, le=20)
    measurement_system: str = Field(default="metric")  # metric or imperial
    
    @validator('dietary_restrictions', 'allergies', 'favorite_cuisines', 'disliked_ingredients')
    def lowercase_lists(cls, v):
        """Convert string lists to lowercase"""
        return [item.lower().strip() for item in v] if v else []


class TokenResponse(BaseModel):
    """Model for authentication token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class DietaryRestriction(BaseModel):
    """Model for dietary restriction"""
    restriction_type: str
    added_at: datetime
    
    class Config:
        from_attributes = True

