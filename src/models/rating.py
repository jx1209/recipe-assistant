"""
Rating and review related Pydantic models
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class RatingCreate(BaseModel):
    """Model for creating/updating a rating"""
    rating: int = Field(..., ge=1, le=5)
    review: Optional[str] = Field(None, max_length=2000)
    
    @validator('review')
    def review_not_just_whitespace(cls, v):
        if v and not v.strip():
            return None
        return v.strip() if v else None


class RatingResponse(BaseModel):
    """Model for rating response"""
    id: int
    recipe_id: int
    user_id: int
    user_name: Optional[str]
    rating: int
    review: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RatingStatistics(BaseModel):
    """Model for recipe rating statistics"""
    recipe_id: int
    average_rating: float = 0.0
    total_count: int = 0
    five_star: int = 0
    four_star: int = 0
    three_star: int = 0
    two_star: int = 0
    one_star: int = 0
    
    class Config:
        from_attributes = True

