"""
Professional Meal Planning System
Comprehensive meal planning with nutrition tracking and smart recommendations
"""

import json
import sqlite3
import random
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple, Set, Union, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from collections import defaultdict, Counter
import re

logger = logging.getLogger(__name__)

class MealType(Enum):
    """Types of meals"""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"

class DietaryPreference(Enum):
    """Dietary preferences and restrictions"""
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    PESCATARIAN = "pescatarian"
    KETO = "keto"
    PALEO = "paleo"
    MEDITERRANEAN = "mediterranean"
    LOW_CARB = "low_carb"
    LOW_FAT = "low_fat"
    HIGH_PROTEIN = "high_protein"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"
    NUT_FREE = "nut_free"

class CookingSkill(Enum):
    """Cooking skill levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

@dataclass
class NutritionalGoals:
    """Daily nutritional goals for meal planning"""
    calories: float = 2000.0
    protein_g: float = 150.0
    carbs_g: float = 250.0
    fat_g: float = 65.0
    fiber_g: float = 25.0
    sodium_mg: float = 2300.0
    sugar_g: float = 50.0
    
    # Micronutrients
    vitamin_c_mg: float = 90.0
    calcium_mg: float = 1000.0
    iron_mg: float = 18.0
    potassium_mg: float = 3500.0

@dataclass
class UserProfile:
    """User profile for personalized meal planning"""
    name: str
    age: int
    gender: str  # 'male' or 'female'
    height_cm: float
    weight_kg: float
    activity_level: str  # 'sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extremely_active'
    dietary_preferences: List[DietaryPreference] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)
    dislikes: List[str] = field(default_factory=list)
    cooking_skill: CookingSkill = CookingSkill.INTERMEDIATE
    max_prep_time: int = 60  # minutes
    budget_per_day: float = 25.0  # dollars
    nutritional_goals: NutritionalGoals = field(default_factory=NutritionalGoals)

    def calculate_bmr(self) -> float:
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation"""
        if self.gender.lower() == 'male':
            bmr = 10 * self.weight_kg + 6.25 * self.height_cm - 5 * self.age + 5
        else:
            bmr = 10 * self.weight_kg + 6.25 * self.height_cm - 5 * self.age - 161
        return bmr
    
    def calculate_tdee(self) -> float:
        """Calculate Total Daily Energy Expenditure"""
        bmr = self.calculate_bmr()
        activity_multipliers = {
            'sedentary': 1.2,
            'lightly_active': 1.375,
            'moderately_active': 1.55,
            'very_active': 1.725,
            'extremely_active': 1.9
        }
        return bmr * activity_multipliers.get(self.activity_level, 1.55)
    
@dataclass
class Recipe:
    """Recipe data structure"""
    id: str
    name: str
    ingredients: List[str]
    instructions: List[str]
    servings: int
    prep_time: int  # minutes
    cook_time: int  # minutes
    difficulty: CookingSkill
    meal_types: List[MealType]
    cuisine: str = ""
    tags: List[str] = field(default_factory=list)
    nutrition_per_serving: Optional[Dict] = None
    cost_per_serving: float = 0.0
    
    @property
    def total_time(self) -> int:
        return self.prep_time + self.cook_time

@dataclass
class Meal:
    """Individual meal in a meal plan"""
    recipe: Recipe
    meal_type: MealType
    date: date
    servings: float = 1.0
    notes: str = ""
    
    @property
    def adjusted_nutrition(self) -> Dict:
        """Get nutrition adjusted for serving size"""
        if not self.recipe.nutrition_per_serving:
            return {}
        
        return {
            key: value * self.servings 
            for key, value in self.recipe.nutrition_per_serving.items()
        }