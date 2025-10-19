"""
Pantry related Pydantic models
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date, datetime


class PantryItemCreate(BaseModel):
    """Model for creating a pantry item"""
    ingredient_name: str = Field(..., min_length=1, max_length=200)
    quantity: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=50)
    expiration_date: Optional[date] = None
    
    @validator('ingredient_name')
    def ingredient_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Ingredient name cannot be empty')
        return v.strip().lower()


class PantryItemUpdate(BaseModel):
    """Model for updating a pantry item"""
    quantity: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=50)
    expiration_date: Optional[date] = None


class PantryItemResponse(BaseModel):
    """Model for pantry item response"""
    id: int
    user_id: int
    ingredient_name: str
    quantity: Optional[float]
    unit: Optional[str]
    category: Optional[str]
    expiration_date: Optional[date]
    added_at: datetime
    updated_at: datetime
    
    # Computed fields
    is_expiring_soon: bool = False  # Within 7 days
    is_expired: bool = False
    
    class Config:
        from_attributes = True


class PantryCheck(BaseModel):
    """Model for checking ingredient availability"""
    required_ingredients: list[str]
    available_ingredients: list[str] = Field(default_factory=list)
    missing_ingredients: list[str] = Field(default_factory=list)
    match_percentage: float = 0.0

