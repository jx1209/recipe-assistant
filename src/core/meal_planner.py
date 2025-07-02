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
    
@dataclass
class DayMealPlan:
    """All meals planned for a single day"""
    date: date
    breakfast: Optional[Meal] = None
    lunch: Optional[Meal] = None
    dinner: Optional[Meal] = None
    snacks: List[Meal] = field(default_factory=list)
    
    def get_all_meals(self) -> List[Meal]:
        """Get all meals for the day"""
        meals = []
        if self.breakfast: meals.append(self.breakfast)
        if self.lunch: meals.append(self.lunch)
        if self.dinner: meals.append(self.dinner)
        meals.extend(self.snacks)
        return meals
    
    def get_daily_nutrition(self) -> Dict[str, float]:
        """Calculate total nutrition for the day"""
        total_nutrition = defaultdict(float)
        
        for meal in self.get_all_meals():
            nutrition = meal.adjusted_nutrition
            for nutrient, value in nutrition.items():
                total_nutrition[nutrient] += value
        
        return dict(total_nutrition)

@dataclass
class WeeklyMealPlan:
    """Weekly meal plan"""
    start_date: date
    user_profile: UserProfile
    days: Dict[date, DayMealPlan] = field(default_factory=dict)
    shopping_list: Dict[str, float] = field(default_factory=dict)
    total_cost: float = 0.0
    
    def add_day(self, day_plan: DayMealPlan):
        """Add a day's meal plan"""
        self.days[day_plan.date] = day_plan
    
    def get_weekly_nutrition_summary(self) -> Dict[str, Any]:
        """Get nutrition summary for the week"""
        daily_totals = []
        
        for day_plan in self.days.values():
            daily_nutrition = day_plan.get_daily_nutrition()
            daily_totals.append(daily_nutrition)
        
        if not daily_totals:
            return {}
        
        # Calculate averages
        avg_nutrition = {}
        all_nutrients = set()
        for daily in daily_totals:
            all_nutrients.update(daily.keys())
        
        for nutrient in all_nutrients:
            values = [daily.get(nutrient, 0) for daily in daily_totals]
            avg_nutrition[nutrient] = sum(values) / len(values)
        
        return {
            'average_daily': avg_nutrition,
            'total_days': len(daily_totals),
            'goal_adherence': self._calculate_goal_adherence(avg_nutrition)
        }
    
    def _calculate_goal_adherence(self, avg_nutrition: Dict[str, float]) -> Dict[str, float]:
        """Calculate how well the plan meets nutritional goals"""
        goals = self.user_profile.nutritional_goals
        adherence = {}
        
        goal_mapping = {
            'calories': goals.calories,
            'protein_g': goals.protein_g,
            'carbs_g': goals.carbs_g,
            'fat_g': goals.fat_g,
            'fiber_g': goals.fiber_g,
            'sodium_mg': goals.sodium_mg
        }
        
        for nutrient, goal_value in goal_mapping.items():
            actual_value = avg_nutrition.get(nutrient, 0)
            if goal_value > 0:
                adherence[nutrient] = min(100, (actual_value / goal_value) * 100)
            else:
                adherence[nutrient] = 100
        
        return adherence

class RecipeDatabase:
    """Database for storing and retrieving recipes"""
    
    def __init__(self, db_path: str = "recipes.db"):
        self.db_path = db_path
        self._setup_database()
        self._populate_sample_recipes()
    
    def _setup_database(self):
        """Initialize recipe database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS recipes (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    ingredients TEXT NOT NULL,
                    instructions TEXT NOT NULL,
                    servings INTEGER NOT NULL,
                    prep_time INTEGER NOT NULL,
                    cook_time INTEGER NOT NULL,
                    difficulty TEXT NOT NULL,
                    meal_types TEXT NOT NULL,
                    cuisine TEXT,
                    tags TEXT,
                    nutrition_data TEXT,
                    cost_per_serving REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS meal_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    plan_date DATE NOT NULL,
                    plan_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_recipes_meal_type ON recipes(meal_types);
                CREATE INDEX IF NOT EXISTS idx_recipes_difficulty ON recipes(difficulty);
                CREATE INDEX IF NOT EXISTS idx_meal_plans_date ON meal_plans(plan_date);
            """)
    
    def _populate_sample_recipes(self):
        """Add sample recipes to the database"""
        sample_recipes = [
            Recipe(
                id="breakfast_oatmeal",
                name="Protein-Packed Oatmeal",
                ingredients=[
                    "1 cup rolled oats",
                    "1 cup almond milk",
                    "1 banana, sliced",
                    "2 tbsp almond butter",
                    "1 tbsp honey",
                    "1 tbsp chia seeds",
                    "1/2 cup blueberries"
                ],
                instructions=[
                    "Cook oats with almond milk for 5 minutes",
                    "Stir in almond butter and honey",
                    "Top with banana, blueberries, and chia seeds"
                ],
                servings=1,
                prep_time=5,
                cook_time=5,
                difficulty=CookingSkill.BEGINNER,
                meal_types=[MealType.BREAKFAST],
                cuisine="American",
                tags=["healthy", "quick", "vegetarian"],
                nutrition_per_serving={
                    "calories": 520,
                    "protein_g": 18,
                    "carbs_g": 68,
                    "fat_g": 22,
                    "fiber_g": 14,
                    "sodium_mg": 120
                },
                cost_per_serving=3.50
            ),
            Recipe(
                id="lunch_chicken_salad",
                name="Mediterranean Chicken Salad",
                ingredients=[
                    "200g grilled chicken breast",
                    "2 cups mixed greens",
                    "1/2 cup cherry tomatoes",
                    "1/4 cup cucumber, diced",
                    "1/4 cup red onion, sliced",
                    "2 tbsp olive oil",
                    "1 tbsp lemon juice",
                    "1/4 cup feta cheese",
                    "10 olives"
                ],
                instructions=[
                    "Grill chicken breast and slice",
                    "Combine all vegetables in a bowl",
                    "Whisk olive oil and lemon juice",
                    "Top salad with chicken, feta, and olives",
                    "Drizzle with dressing"
                ],
                servings=1,
                prep_time=15,
                cook_time=10,
                difficulty=CookingSkill.INTERMEDIATE,
                meal_types=[MealType.LUNCH, MealType.DINNER],
                cuisine="Mediterranean",
                tags=["high-protein", "low-carb", "gluten-free"],
                nutrition_per_serving={
                    "calories": 485,
                    "protein_g": 42,
                    "carbs_g": 12,
                    "fat_g": 28,
                    "fiber_g": 4,
                    "sodium_mg": 680
                },
                cost_per_serving=8.25
            ),
            Recipe(
                id="dinner_salmon_quinoa",
                name="Baked Salmon with Quinoa",
                ingredients=[
                    "200g salmon fillet",
                    "1 cup quinoa",
                    "2 cups vegetable broth",
                    "1 cup broccoli florets",
                    "1 tbsp olive oil",
                    "1 lemon, sliced",
                    "2 cloves garlic, minced",
                    "Salt and pepper to taste"
                ],
                instructions=[
                    "Cook quinoa in vegetable broth",
                    "Season salmon with salt, pepper, and garlic",
                    "Bake salmon at 400°F for 12-15 minutes",
                    "Steam broccoli until tender",
                    "Serve salmon over quinoa with broccoli"
                ],
                servings=1,
                prep_time=10,
                cook_time=20,
                difficulty=CookingSkill.INTERMEDIATE,
                meal_types=[MealType.DINNER],
                cuisine="American",
                tags=["high-protein", "omega-3", "gluten-free"],
                nutrition_per_serving={
                    "calories": 625,
                    "protein_g": 45,
                    "carbs_g": 52,
                    "fat_g": 24,
                    "fiber_g": 8,
                    "sodium_mg": 320
                },
                cost_per_serving=12.50
            ),
            Recipe(
                id="snack_greek_yogurt",
                name="Greek Yogurt Parfait",
                ingredients=[
                    "1 cup Greek yogurt",
                    "1/4 cup granola",
                    "1/2 cup mixed berries",
                    "1 tbsp honey",
                    "1 tbsp chopped nuts"
                ],
                instructions=[
                    "Layer half the yogurt in a bowl",
                    "Add half the berries and granola",
                    "Repeat layers",
                    "Top with honey and nuts"
                ],
                servings=1,
                prep_time=5,
                cook_time=0,
                difficulty=CookingSkill.BEGINNER,
                meal_types=[MealType.SNACK, MealType.BREAKFAST],
                cuisine="American",
                tags=["high-protein", "quick", "vegetarian"],
                nutrition_per_serving={
                    "calories": 320,
                    "protein_g": 20,
                    "carbs_g": 35,
                    "fat_g": 12,
                    "fiber_g": 6,
                    "sodium_mg": 85
                },
                cost_per_serving=4.75
            )
        ]
        
        for recipe in sample_recipes:
            self.save_recipe(recipe)
    
    def save_recipe(self, recipe: Recipe):
        """Save a recipe to the database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO recipes 
                (id, name, ingredients, instructions, servings, prep_time, cook_time, 
                 difficulty, meal_types, cuisine, tags, nutrition_data, cost_per_serving)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                recipe.id,
                recipe.name,
                json.dumps(recipe.ingredients),
                json.dumps(recipe.instructions),
                recipe.servings,
                recipe.prep_time,
                recipe.cook_time,
                recipe.difficulty.value,
                json.dumps([mt.value for mt in recipe.meal_types]),
                recipe.cuisine,
                json.dumps(recipe.tags),
                json.dumps(recipe.nutrition_per_serving) if recipe.nutrition_per_serving else None,
                recipe.cost_per_serving
            ))
    
    def get_recipes_by_meal_type(self, meal_type: MealType) -> List[Recipe]:
        """Get recipes suitable for a specific meal type"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM recipes 
                WHERE meal_types LIKE ?
            """, (f'%{meal_type.value}%',))
            
            recipes = []
            for row in cursor.fetchall():
                recipe = self._row_to_recipe(row)
                if meal_type in recipe.meal_types:
                    recipes.append(recipe)
            
            return recipes
    
    def search_recipes(self, **criteria) -> List[Recipe]:
        """Search recipes by various criteria"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM recipes WHERE 1=1"
            params = []
            
            if 'max_prep_time' in criteria:
                query += " AND prep_time <= ?"
                params.append(criteria['max_prep_time'])
            
            if 'max_total_time' in criteria:
                query += " AND (prep_time + cook_time) <= ?"
                params.append(criteria['max_total_time'])
            
            if 'difficulty' in criteria:
                query += " AND difficulty = ?"
                params.append(criteria['difficulty'].value)
            
            if 'cuisine' in criteria:
                query += " AND cuisine = ?"
                params.append(criteria['cuisine'])
            
            if 'max_cost' in criteria:
                query += " AND cost_per_serving <= ?"
                params.append(criteria['max_cost'])
            
            cursor.execute(query, params)
            return [self._row_to_recipe(row) for row in cursor.fetchall()]
    
    def _row_to_recipe(self, row) -> Recipe:
        """Convert database row to Recipe object"""
        return Recipe(
            id=row[0],
            name=row[1],
            ingredients=json.loads(row[2]),
            instructions=json.loads(row[3]),
            servings=row[4],
            prep_time=row[5],
            cook_time=row[6],
            difficulty=CookingSkill(row[7]),
            meal_types=[MealType(mt) for mt in json.loads(row[8])],
            cuisine=row[9] or "",
            tags=json.loads(row[10]) if row[10] else [],
            nutrition_per_serving=json.loads(row[11]) if row[11] else None,
            cost_per_serving=row[12]
        )