"""
shopping list related pydantic models
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List
from datetime import datetime


class ShoppingItem(BaseModel):
    """model for a shopping list item"""
    ingredient: str = Field(..., min_length=1, max_length=200)
    quantity: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=50)
    checked: bool = False
    notes: Optional[str] = Field(None, max_length=200)
    
    @field_validator('ingredient')
    @classmethod
    def ingredient_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('ingredient name cannot be empty')
        return v.strip().lower()


class ShoppingListCreate(BaseModel):
    """model for creating a shopping list"""
    name: str = Field(..., min_length=1, max_length=100)
    recipe_ids: List[int] = Field(default_factory=list)
    meal_plan_id: Optional[int] = None
    custom_items: List[ShoppingItem] = Field(default_factory=list)
    exclude_pantry: bool = True
    group_by_category: bool = True
    
    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('name cannot be empty')
        return v.strip()
    
    @model_validator(mode='after')
    def must_have_source(self):
        #at least one of recipe_ids, meal_plan_id, or custom_items must be provided
        if not self.recipe_ids and not self.meal_plan_id and not self.custom_items:
            raise ValueError('must provide recipe_ids, meal_plan_id, or custom_items')
        return self


class ShoppingListUpdate(BaseModel):
    """model for updating a shopping list"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    items: List[ShoppingItem]


class ShoppingListResponse(BaseModel):
    """model for shopping list response"""
    id: int
    user_id: int
    name: str
    items: List[ShoppingItem]
    meal_plan_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    #computed fields
    total_items: int = 0
    checked_items: int = 0
    categories: List[str] = Field(default_factory=list)
    
    model_config = {"from_attributes": True}


class ShoppingListSummary(BaseModel):
    """model for shopping list summary/card"""
    id: int
    name: str
    total_items: int
    checked_items: int
    created_at: datetime
    
    model_config = {"from_attributes": True}

