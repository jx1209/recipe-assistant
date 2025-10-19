"""
Recipe-related Pydantic models
"""

from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DifficultyLevel(str, Enum):
    """Recipe difficulty levels"""
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class RecipeIngredient(BaseModel):
    """Model for a recipe ingredient"""
    name: str = Field(..., min_length=1, max_length=200)
    quantity: Optional[float] = None
    unit: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=200)
    
    @validator('name')
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Ingredient name cannot be empty')
        return v.strip()


class RecipeInstruction(BaseModel):
    """Model for a recipe instruction step"""
    step_number: int = Field(..., ge=1)
    instruction: str = Field(..., min_length=1, max_length=1000)
    
    @validator('instruction')
    def instruction_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Instruction cannot be empty')
        return v.strip()


class RecipeNutrition(BaseModel):
    """Model for recipe nutrition information"""
    calories: Optional[float] = Field(None, ge=0)
    protein_g: Optional[float] = Field(None, ge=0)
    carbs_g: Optional[float] = Field(None, ge=0)
    fat_g: Optional[float] = Field(None, ge=0)
    fiber_g: Optional[float] = Field(None, ge=0)
    sugar_g: Optional[float] = Field(None, ge=0)
    sodium_mg: Optional[float] = Field(None, ge=0)
    cholesterol_mg: Optional[float] = Field(None, ge=0)
    
    # Vitamins and minerals
    vitamin_c_mg: Optional[float] = Field(None, ge=0)
    calcium_mg: Optional[float] = Field(None, ge=0)
    iron_mg: Optional[float] = Field(None, ge=0)
    potassium_mg: Optional[float] = Field(None, ge=0)


class RecipeCreate(BaseModel):
    """Model for creating a new recipe"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    source_url: Optional[HttpUrl] = None
    source_name: Optional[str] = Field(None, max_length=100)
    ingredients: List[RecipeIngredient] = Field(..., min_items=1)
    instructions: List[str] = Field(..., min_items=1)
    image_url: Optional[HttpUrl] = None
    prep_time_minutes: Optional[int] = Field(None, ge=0, le=1440)
    cook_time_minutes: Optional[int] = Field(None, ge=0, le=1440)
    servings: int = Field(default=4, ge=1, le=100)
    difficulty: Optional[DifficultyLevel] = None
    cuisine: Optional[str] = Field(None, max_length=50)
    tags: List[str] = Field(default_factory=list)
    nutrition: Optional[RecipeNutrition] = None
    
    @validator('title')
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    @validator('instructions')
    def instructions_not_empty(cls, v):
        if not v:
            raise ValueError('At least one instruction is required')
        return [instr.strip() for instr in v if instr.strip()]
    
    @validator('tags')
    def lowercase_tags(cls, v):
        return [tag.lower().strip() for tag in v if tag.strip()] if v else []


class RecipeUpdate(BaseModel):
    """Model for updating a recipe"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    source_url: Optional[HttpUrl] = None
    source_name: Optional[str] = Field(None, max_length=100)
    ingredients: Optional[List[RecipeIngredient]] = None
    instructions: Optional[List[str]] = None
    image_url: Optional[HttpUrl] = None
    prep_time_minutes: Optional[int] = Field(None, ge=0, le=1440)
    cook_time_minutes: Optional[int] = Field(None, ge=0, le=1440)
    servings: Optional[int] = Field(None, ge=1, le=100)
    difficulty: Optional[DifficultyLevel] = None
    cuisine: Optional[str] = Field(None, max_length=50)
    tags: Optional[List[str]] = None
    nutrition: Optional[RecipeNutrition] = None


class RecipeResponse(BaseModel):
    """Model for recipe response"""
    id: int
    title: str
    description: Optional[str]
    source_url: Optional[str]
    source_name: Optional[str]
    ingredients: List[RecipeIngredient]
    instructions: List[str]
    image_url: Optional[str]
    prep_time_minutes: Optional[int]
    cook_time_minutes: Optional[int]
    total_time_minutes: Optional[int]
    servings: int
    difficulty: Optional[str]
    cuisine: Optional[str]
    tags: List[str] = Field(default_factory=list)
    nutrition: Optional[RecipeNutrition]
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    view_count: int = 0
    
    # Additional computed fields
    is_favorite: bool = False
    average_rating: Optional[float] = None
    rating_count: int = 0
    user_rating: Optional[int] = None
    
    class Config:
        from_attributes = True


class RecipeSearch(BaseModel):
    """Model for recipe search parameters"""
    query: Optional[str] = Field(None, max_length=200)
    cuisine: Optional[str] = Field(None, max_length=50)
    difficulty: Optional[DifficultyLevel] = None
    max_time: Optional[int] = Field(None, ge=0, le=1440)
    tags: Optional[List[str]] = None
    ingredients: Optional[List[str]] = None  # Search by ingredients
    exclude_ingredients: Optional[List[str]] = None
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    sort_by: Optional[str] = Field(default="created_at")  # created_at, rating, time, title
    
    @validator('tags', 'ingredients', 'exclude_ingredients')
    def lowercase_lists(cls, v):
        return [item.lower().strip() for item in v if item.strip()] if v else []


class RecipeImportUrl(BaseModel):
    """Model for importing recipe from URL"""
    url: HttpUrl


class RecipeImportText(BaseModel):
    """Model for importing recipe from text"""
    text: str = Field(..., min_length=10)
    title: Optional[str] = Field(None, max_length=200)


class RecipeSummary(BaseModel):
    """Model for recipe summary/card"""
    id: int
    title: str
    description: Optional[str]
    image_url: Optional[str]
    total_time_minutes: Optional[int]
    difficulty: Optional[str]
    cuisine: Optional[str]
    servings: int
    average_rating: Optional[float]
    rating_count: int
    is_favorite: bool = False
    
    class Config:
        from_attributes = True

