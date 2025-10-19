"""
Pydantic models for Recipe Assistant API
"""

from .user import UserCreate, UserLogin, UserProfile, UserUpdate, UserPreferences
from .recipe import (
    RecipeCreate, RecipeUpdate, RecipeResponse, RecipeSearch, 
    RecipeIngredient, RecipeInstruction, RecipeNutrition
)
from .meal_plan import MealPlanCreate, MealPlanUpdate, MealPlanResponse, DayMeal
from .shopping_list import ShoppingListCreate, ShoppingListUpdate, ShoppingListResponse, ShoppingItem
from .rating import RatingCreate, RatingResponse
from .pantry import PantryItemCreate, PantryItemUpdate, PantryItemResponse
from .nutrition import NutritionInfo, NutritionGoals, NutritionAnalysis

__all__ = [
    # User models
    'UserCreate', 'UserLogin', 'UserProfile', 'UserUpdate', 'UserPreferences',
    # Recipe models
    'RecipeCreate', 'RecipeUpdate', 'RecipeResponse', 'RecipeSearch',
    'RecipeIngredient', 'RecipeInstruction', 'RecipeNutrition',
    # Meal plan models
    'MealPlanCreate', 'MealPlanUpdate', 'MealPlanResponse', 'DayMeal',
    # Shopping list models
    'ShoppingListCreate', 'ShoppingListUpdate', 'ShoppingListResponse', 'ShoppingItem',
    # Rating models
    'RatingCreate', 'RatingResponse',
    # Pantry models
    'PantryItemCreate', 'PantryItemUpdate', 'PantryItemResponse',
    # Nutrition models
    'NutritionInfo', 'NutritionGoals', 'NutritionAnalysis',
]

