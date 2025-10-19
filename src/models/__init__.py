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
    #user models
    'UserCreate', 'UserLogin', 'UserProfile', 'UserUpdate', 'UserPreferences',
    #recipe models
    'RecipeCreate', 'RecipeUpdate', 'RecipeResponse', 'RecipeSearch',
    'RecipeIngredient', 'RecipeInstruction', 'RecipeNutrition',
    #meal plan models
    'MealPlanCreate', 'MealPlanUpdate', 'MealPlanResponse', 'DayMeal',
    #shopping list models
    'ShoppingListCreate', 'ShoppingListUpdate', 'ShoppingListResponse', 'ShoppingItem',
    #rating models
    'RatingCreate', 'RatingResponse',
    #pantry models
    'PantryItemCreate', 'PantryItemUpdate', 'PantryItemResponse',
    #nutrition models
    'NutritionInfo', 'NutritionGoals', 'NutritionAnalysis',
]

