"""
meal plan related pydantic models
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime


class DayMeal(BaseModel):
    """model for a single meal in a day"""
    meal_type: str = Field(..., pattern="^(breakfast|lunch|dinner|snack)$")
    recipe_id: int
    servings: float = Field(default=1.0, ge=0.25, le=10.0)
    notes: Optional[str] = Field(None, max_length=500)


class DayPlan(BaseModel):
    """model for a day's meal plan"""
    date: date
    breakfast: Optional[DayMeal] = None
    lunch: Optional[DayMeal] = None
    dinner: Optional[DayMeal] = None
    snacks: List[DayMeal] = Field(default_factory=list)
    notes: Optional[str] = Field(None, max_length=500)


class MealPlanCreate(BaseModel):
    """model for creating a meal plan"""
    name: str = Field(..., min_length=1, max_length=100)
    start_date: date
    end_date: date
    days: List[DayPlan] = Field(..., min_length=1)
    notes: Optional[str] = Field(None, max_length=1000)
    
    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('name cannot be empty')
        return v.strip()
    
    @model_validator(mode='after')
    def end_after_start(self):
        if self.end_date < self.start_date:
            raise ValueError('end_date must be after start_date')
        return self


class MealPlanUpdate(BaseModel):
    """model for updating a meal plan"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    days: Optional[List[DayPlan]] = None
    notes: Optional[str] = Field(None, max_length=1000)


class MealPlanResponse(BaseModel):
    """model for meal plan response"""
    id: int
    user_id: int
    name: str
    start_date: date
    end_date: date
    days: List[DayPlan]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    #computed fields
    total_recipes: int = 0
    total_days: int = 0
    nutrition_summary: Optional[Dict[str, Any]] = None
    
    model_config = {"from_attributes": True}


class MealPlanGenerateRequest(BaseModel):
    """model for ai-powered meal plan generation"""
    start_date: date
    days: int = Field(default=7, ge=1, le=30)
    meals_per_day: List[str] = Field(
        default=["breakfast", "lunch", "dinner"],
        min_length=1
    )
    dietary_restrictions: List[str] = Field(default_factory=list)
    exclude_ingredients: List[str] = Field(default_factory=list)
    preferred_cuisines: List[str] = Field(default_factory=list)
    target_calories_per_day: Optional[int] = Field(None, ge=800, le=5000)
    optimize_for: Optional[str] = Field(
        default="balanced",
        pattern="^(balanced|protein|low_carb|budget|time)$"
    )
    include_snacks: bool = False
    minimize_waste: bool = True
    
    @field_validator('meals_per_day')
    @classmethod
    def valid_meal_types(cls, v):
        valid_types = {'breakfast', 'lunch', 'dinner', 'snack'}
        for meal in v:
            if meal not in valid_types:
                raise ValueError(f'invalid meal type: {meal}')
        return v
    
    @field_validator('dietary_restrictions', 'exclude_ingredients', 'preferred_cuisines')
    @classmethod
    def lowercase_lists(cls, v):
        return [item.lower().strip() for item in v if item.strip()] if v else []


class MealPlanSummary(BaseModel):
    """model for meal plan summary/card"""
    id: int
    name: str
    start_date: date
    end_date: date
    total_days: int
    total_recipes: int
    created_at: datetime
    
    model_config = {"from_attributes": True}

