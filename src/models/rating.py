"""
rating and review related pydantic models
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class RatingCreate(BaseModel):
    """model for creating/updating a rating"""
    rating: int = Field(..., ge=1, le=5)
    review_text: Optional[str] = Field(None, max_length=2000)
    
    @field_validator('review_text')
    @classmethod
    def review_not_just_whitespace(cls, v):
        if v and not v.strip():
            return None
        return v.strip() if v else None


class RatingUpdate(BaseModel):
    """model for updating a rating"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    review_text: Optional[str] = Field(None, max_length=2000)
    
    @field_validator('review_text')
    @classmethod
    def review_not_just_whitespace(cls, v):
        if v and not v.strip():
            return None
        return v.strip() if v else None


class RatingResponse(BaseModel):
    """model for rating response"""
    id: int
    recipe_id: int
    user_id: int
    user_name: Optional[str]
    rating: int
    review_text: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class RatingSummary(BaseModel):
    """model for recipe rating summary"""
    recipe_id: int
    average_rating: float = 0.0
    total_count: int = 0
    five_star_count: int = 0
    four_star_count: int = 0
    three_star_count: int = 0
    two_star_count: int = 0
    one_star_count: int = 0
    
    model_config = {"from_attributes": True}

