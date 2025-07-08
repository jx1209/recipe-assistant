"""
Professional Meal Planning System
Comprehensive meal planning with nutrition tracking and smart recommendations
"""

import asyncio
import json
import sqlite3
import random
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple, Set, Union, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import statistics
from collections import defaultdict, Counter
import re
import hashlib

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
    
class MealPlanGenerator:
    """Intelligent meal plan generator"""
    
    def __init__(self, recipe_db: RecipeDatabase, nutrition_calculator=None):
        self.recipe_db = recipe_db
        self.nutrition_calculator = nutrition_calculator
    
    def generate_weekly_plan(self, user_profile: UserProfile, 
                           start_date: date = None,
                           preferences: Dict[str, Any] = None) -> WeeklyMealPlan:
        """Generate a complete weekly meal plan"""
        
        if start_date is None:
            start_date = date.today()
        
        preferences = preferences or {}
        
        # Calculate daily calorie target
        daily_calories = user_profile.calculate_tdee()
        
        # Distribute calories across meals
        meal_calorie_distribution = {
            MealType.BREAKFAST: 0.25,
            MealType.LUNCH: 0.35,
            MealType.DINNER: 0.35,
            MealType.SNACK: 0.05
        }
        
        weekly_plan = WeeklyMealPlan(
            start_date=start_date,
            user_profile=user_profile
        )
        
        # Generate plan for each day
        for day_offset in range(7):
            current_date = start_date + timedelta(days=day_offset)
            day_plan = self._generate_day_plan(
                current_date, 
                user_profile, 
                daily_calories,
                meal_calorie_distribution,
                preferences
            )
            weekly_plan.add_day(day_plan)
        
        # Generate shopping list
        weekly_plan.shopping_list = self._generate_shopping_list(weekly_plan)
        weekly_plan.total_cost = self._calculate_total_cost(weekly_plan)
        
        return weekly_plan
    
    def _generate_day_plan(self, plan_date: date, user_profile: UserProfile,
                          daily_calories: float, calorie_distribution: Dict[MealType, float],
                          preferences: Dict[str, Any]) -> DayMealPlan:
        """Generate meal plan for a single day"""
        
        day_plan = DayMealPlan(date=plan_date)
        
        # Generate each meal
        for meal_type, calorie_ratio in calorie_distribution.items():
            target_calories = daily_calories * calorie_ratio
            
            if meal_type == MealType.SNACK:
                # Generate multiple snacks if needed
                snack_recipes = self._select_recipes_for_meal(
                    meal_type, user_profile, target_calories, preferences
                )
                for recipe in snack_recipes[:2]:  # Max 2 snacks
                    meal = Meal(
                        recipe=recipe,
                        meal_type=meal_type,
                        date=plan_date,
                        servings=self._calculate_optimal_servings(recipe, target_calories / 2)
                    )
                    day_plan.snacks.append(meal)
            else:
                recipes = self._select_recipes_for_meal(
                    meal_type, user_profile, target_calories, preferences
                )
                
                if recipes:
                    recipe = recipes[0]  # Take the best match
                    servings = self._calculate_optimal_servings(recipe, target_calories)
                    
                    meal = Meal(
                        recipe=recipe,
                        meal_type=meal_type,
                        date=plan_date,
                        servings=servings
                    )
                    
                    if meal_type == MealType.BREAKFAST:
                        day_plan.breakfast = meal
                    elif meal_type == MealType.LUNCH:
                        day_plan.lunch = meal
                    elif meal_type == MealType.DINNER:
                        day_plan.dinner = meal
        
        return day_plan
    
    def _select_recipes_for_meal(self, meal_type: MealType, user_profile: UserProfile,
                               target_calories: float, preferences: Dict[str, Any]) -> List[Recipe]:
        """Select appropriate recipes for a meal"""
        
        # Get all recipes for this meal type
        candidates = self.recipe_db.get_recipes_by_meal_type(meal_type)
        
        # Filter by user constraints
        filtered_recipes = []
        
        for recipe in candidates:
            # Check dietary restrictions
            if not self._recipe_meets_dietary_preferences(recipe, user_profile):
                continue
            
            # Check allergies
            if self._recipe_contains_allergens(recipe, user_profile.allergies):
                continue
            
            # Check dislikes
            if self._recipe_contains_dislikes(recipe, user_profile.dislikes):
                continue
            
            # Check cooking skill and time
            if recipe.difficulty.value == 'advanced' and user_profile.cooking_skill == CookingSkill.BEGINNER:
                continue
            
            if recipe.total_time > user_profile.max_prep_time:
                continue
            
            # Check budget
            if recipe.cost_per_serving > user_profile.budget_per_day / 3:  # Rough estimate
                continue
            
            filtered_recipes.append(recipe)
        
        # Score and rank recipes
        scored_recipes = []
        for recipe in filtered_recipes:
            score = self._score_recipe_for_meal(recipe, target_calories, user_profile, preferences)
            scored_recipes.append((score, recipe))
        
        # Sort by score (highest first)
        scored_recipes.sort(key=lambda x: x[0], reverse=True)
        
        return [recipe for score, recipe in scored_recipes[:5]]  # Return top 5
    
    def _recipe_meets_dietary_preferences(self, recipe: Recipe, user_profile: UserProfile) -> bool:
        """Check if recipe meets dietary preferences"""
        ingredients_text = ' '.join(recipe.ingredients).lower()
        
        for preference in user_profile.dietary_preferences:
            if preference == DietaryPreference.VEGETARIAN:
                meat_keywords = ['chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'turkey', 'lamb']
                if any(meat in ingredients_text for meat in meat_keywords):
                    return False
            
            elif preference == DietaryPreference.VEGAN:
                animal_keywords = ['chicken', 'beef', 'pork', 'fish', 'milk', 'cheese', 'yogurt', 'eggs', 'butter', 'honey']
                if any(animal in ingredients_text for animal in animal_keywords):
                    return False
            
            elif preference == DietaryPreference.GLUTEN_FREE:
                gluten_keywords = ['flour', 'bread', 'pasta', 'wheat', 'barley', 'rye']
                if any(gluten in ingredients_text for gluten in gluten_keywords):
                    return False
            
            elif preference == DietaryPreference.DAIRY_FREE:
                dairy_keywords = ['milk', 'cheese', 'yogurt', 'butter', 'cream']
                if any(dairy in ingredients_text for dairy in dairy_keywords):
                    return False
            
            elif preference == DietaryPreference.KETO:
                if recipe.nutrition_per_serving:
                    carb_ratio = (recipe.nutrition_per_serving.get('carbs_g', 0) * 4) / max(recipe.nutrition_per_serving.get('calories', 1), 1)
                    if carb_ratio > 0.05:  # More than 5% carbs
                        return False
        
        return True
    
    def _recipe_contains_allergens(self, recipe: Recipe, allergies: List[str]) -> bool:
        """Check if recipe contains allergens"""
        ingredients_text = ' '.join(recipe.ingredients).lower()
        return any(allergen.lower() in ingredients_text for allergen in allergies)
    
    def _recipe_contains_dislikes(self, recipe: Recipe, dislikes: List[str]) -> bool:
        """Check if recipe contains disliked ingredients"""
        ingredients_text = ' '.join(recipe.ingredients).lower()
        return any(dislike.lower() in ingredients_text for dislike in dislikes)
    
    def _score_recipe_for_meal(self, recipe: Recipe, target_calories: float,
                             user_profile: UserProfile, preferences: Dict[str, Any]) -> float:
        """Score a recipe for how well it fits the meal requirements"""
        score = 0.0
        
        if not recipe.nutrition_per_serving:
            return 0.0
        
        nutrition = recipe.nutrition_per_serving
        
        # Calorie matching (0-30 points)
        calorie_diff = abs(nutrition.get('calories', 0) - target_calories)
        calorie_score = max(0, 30 - (calorie_diff / target_calories * 100))
        score += calorie_score
        
        # Protein content (0-20 points)
        protein_ratio = nutrition.get('protein_g', 0) * 4 / max(nutrition.get('calories', 1), 1)
        if protein_ratio >= 0.25:  # 25% or more protein
            score += 20
        elif protein_ratio >= 0.20:
            score += 15
        elif protein_ratio >= 0.15:
            score += 10
        
        # Fiber content (0-15 points)
        fiber_per_cal = nutrition.get('fiber_g', 0) / max(nutrition.get('calories', 1), 1) * 100
        if fiber_per_cal >= 2.0:
            score += 15
        elif fiber_per_cal >= 1.5:
            score += 10
        elif fiber_per_cal >= 1.0:
            score += 5
        
        # Cooking time preference (0-15 points)
        if recipe.total_time <= 15:
            score += 15
        elif recipe.total_time <= 30:
            score += 10
        elif recipe.total_time <= 45:
            score += 5
        
        # Cost efficiency (0-10 points)
        if recipe.cost_per_serving <= 5.0:
            score += 10
        elif recipe.cost_per_serving <= 8.0:
            score += 7
        elif recipe.cost_per_serving <= 12.0:
            score += 4
        
        # Skill level match (0-10 points)
        if recipe.difficulty == user_profile.cooking_skill:
            score += 10
        elif recipe.difficulty.value in ['beginner', 'intermediate'] and user_profile.cooking_skill != CookingSkill.BEGINNER:
            score += 7
        
        return score
    
    def _calculate_optimal_servings(self, recipe: Recipe, target_calories: float) -> float:
        """Calculate optimal serving size to match target calories"""
        if not recipe.nutrition_per_serving or recipe.nutrition_per_serving.get('calories', 0) == 0:
            return 1.0
        
        recipe_calories = recipe.nutrition_per_serving['calories']
        optimal_servings = target_calories / recipe_calories
        
        # Round to reasonable serving sizes
        if optimal_servings < 0.5:
            return 0.5
        elif optimal_servings > 3.0:
            return 3.0
        else:
            return round(optimal_servings * 4) / 4  # Round to quarter servings
    def _generate_shopping_list(self, weekly_plan: WeeklyMealPlan) -> Dict[str, float]:
        """Generate shopping list with ingredient quantities"""
        shopping_list = defaultdict(float)
        
        for day_plan in weekly_plan.days.values():
            for meal in day_plan.get_all_meals():
                for ingredient in meal.recipe.ingredients:
                    # Parse ingredient to get base ingredient name and quantity
                    amount, unit, ingredient_name = self._parse_ingredient(ingredient)
                    
                    # Scale by serving size
                    scaled_amount = amount * meal.servings
                    
                    # Group similar ingredients
                    base_ingredient = self._normalize_ingredient_name(ingredient_name)
                    shopping_list[f"{base_ingredient} ({unit})"] += scaled_amount
        
        # Convert to regular dict and round quantities
        return {
            ingredient: round(quantity, 2) 
            for ingredient, quantity in shopping_list.items()
            if quantity > 0
        }
    
    def _parse_ingredient(self, ingredient_text: str) -> Tuple[float, str, str]:
        """Parse ingredient text to extract amount, unit, and name"""
        # Simple parsing - in practice, you'd use the nutrition calculator's parser
        patterns = [
            r'^(\d+(?:\.\d+)?(?:/\d+)?)\s*(\w+)?\s+(.+)$',
            r'^(\d+/\d+)\s*(\w+)?\s+(.+)$',
        ]
        
        for pattern in patterns:
            match = re.match(pattern, ingredient_text.strip(), re.IGNORECASE)
            if match:
                amount_str, unit, ingredient = match.groups()
                
                # Handle fractions
                if '/' in amount_str:
                    parts = amount_str.split('/')
                    amount = float(parts[0]) / float(parts[1])
                else:
                    amount = float(amount_str)
                
                return amount, unit or 'unit', ingredient.strip()
        
        return 1.0, 'unit', ingredient_text.strip()
    
    def _normalize_ingredient_name(self, ingredient_name: str) -> str:
        """Normalize ingredient names for grouping"""
        # Remove common descriptors
        ingredient_name = ingredient_name.lower()
        
        # Remove common modifiers
        modifiers = ['fresh', 'frozen', 'canned', 'dried', 'chopped', 'diced', 'sliced', 'minced']
        for modifier in modifiers:
            ingredient_name = ingredient_name.replace(modifier, '').strip()
        
        # Remove commas and extra descriptors
        ingredient_name = ingredient_name.split(',')[0].strip()
        
        return ingredient_name.title()
    
    def _calculate_total_cost(self, weekly_plan: WeeklyMealPlan) -> float:
        """Calculate total cost for the weekly meal plan"""
        total_cost = 0.0
        
        for day_plan in weekly_plan.days.values():
            for meal in day_plan.get_all_meals():
                meal_cost = meal.recipe.cost_per_serving * meal.servings
                total_cost += meal_cost
        
        return round(total_cost, 2)

class NutritionCalculator:
    """Calculate and validate nutritional information"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.cache = {}
    
    async def get_nutrition_data(self, ingredient: str, amount: str) -> Dict[str, float]:
        """Get nutrition data for an ingredient"""
        cache_key = f"{ingredient}_{amount}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Mock nutrition data for demo - in production, integrate with USDA API or similar
        nutrition_data = self._get_mock_nutrition_data(ingredient, amount)
        self.cache[cache_key] = nutrition_data
        
        return nutrition_data
    
    def _get_mock_nutrition_data(self, ingredient: str, amount: str) -> Dict[str, float]:
        """Mock nutrition data - replace with real API integration"""
        # Basic nutrition estimates per 100g
        nutrition_db = {
            'chicken breast': {'calories': 165, 'protein_g': 31, 'carbs_g': 0, 'fat_g': 3.6, 'fiber_g': 0},
            'salmon': {'calories': 208, 'protein_g': 25, 'carbs_g': 0, 'fat_g': 12, 'fiber_g': 0},
            'quinoa': {'calories': 120, 'protein_g': 4.4, 'carbs_g': 22, 'fat_g': 1.9, 'fiber_g': 2.8},
            'broccoli': {'calories': 34, 'protein_g': 2.8, 'carbs_g': 7, 'fat_g': 0.4, 'fiber_g': 2.6},
            'banana': {'calories': 89, 'protein_g': 1.1, 'carbs_g': 23, 'fat_g': 0.3, 'fiber_g': 2.6},
            'oats': {'calories': 389, 'protein_g': 17, 'carbs_g': 66, 'fat_g': 7, 'fiber_g': 11},
            'greek yogurt': {'calories': 100, 'protein_g': 10, 'carbs_g': 6, 'fat_g': 4, 'fiber_g': 0},
        }
        
        # Simple amount parsing (in production, use proper parsing)
        amount_multiplier = 1.0
        if 'cup' in amount:
            amount_multiplier = 1.5
        elif 'tbsp' in amount:
            amount_multiplier = 0.15
        elif any(char.isdigit() for char in amount):
            # Extract first number
            import re
            numbers = re.findall(r'\d+', amount)
            if numbers:
                amount_multiplier = int(numbers[0]) / 100
        
        base_nutrition = nutrition_db.get(ingredient.lower(), {
            'calories': 50, 'protein_g': 2, 'carbs_g': 8, 'fat_g': 1, 'fiber_g': 1
        })
        
        return {k: v * amount_multiplier for k, v in base_nutrition.items()}
    
    def calculate_recipe_nutrition(self, recipe: Recipe) -> Dict[str, float]:
        """Calculate total nutrition for a recipe"""
        total_nutrition = defaultdict(float)
        
        for ingredient in recipe.ingredients:
            # Parse ingredient
            amount, unit, ingredient_name = self._parse_ingredient_simple(ingredient)
            nutrition = asyncio.run(self.get_nutrition_data(ingredient_name, f"{amount} {unit}"))
            
            for nutrient, value in nutrition.items():
                total_nutrition[nutrient] += value
        
        # Divide by servings to get per-serving nutrition
        per_serving = {}
        for nutrient, value in total_nutrition.items():
            per_serving[nutrient] = value / recipe.servings
        
        return per_serving
    
    def _parse_ingredient_simple(self, ingredient: str) -> Tuple[float, str, str]:
        """Simple ingredient parsing"""
        import re
        
        # Match patterns like "1 cup", "2 tbsp", "200g"
        pattern = r'^(\d+(?:\.\d+)?(?:/\d+)?)\s*(\w+)?\s+(.+)$'
        match = re.match(pattern, ingredient.strip())
        
        if match:
            amount_str, unit, name = match.groups()
            
            if '/' in amount_str:
                parts = amount_str.split('/')
                amount = float(parts[0]) / float(parts[1])
            else:
                amount = float(amount_str)
            
            return amount, unit or 'unit', name.strip()
        
        return 1.0, 'unit', ingredient.strip()

class MealPlanOptimizer:
    """Optimize meal plans for various criteria"""
    
    def __init__(self, meal_planner: MealPlanGenerator):
        self.meal_planner = meal_planner
    
    def optimize_for_nutrition(self, weekly_plan: WeeklyMealPlan) -> WeeklyMealPlan:
        """Optimize meal plan to better meet nutritional goals"""
        nutrition_summary = weekly_plan.get_weekly_nutrition_summary()
        adherence = nutrition_summary.get('goal_adherence', {})
        
        # Find nutrients that are significantly under/over target
        improvements_needed = []
        
        for nutrient, adherence_percent in adherence.items():
            if adherence_percent < 80:  # Under target
                improvements_needed.append((nutrient, 'increase'))
            elif adherence_percent > 120:  # Over target
                improvements_needed.append((nutrient, 'decrease'))
        
        # TODO: Implement recipe swapping logic based on improvements needed
        # This would involve finding alternative recipes that better meet the nutritional gaps
        
        return weekly_plan
    
    def optimize_for_cost(self, weekly_plan: WeeklyMealPlan, target_budget: float) -> WeeklyMealPlan:
        """Optimize meal plan to meet budget constraints"""
        if weekly_plan.total_cost <= target_budget:
            return weekly_plan
        
        # TODO: Implement cost optimization
        # - Replace expensive recipes with cheaper alternatives
        # - Adjust serving sizes
        # - Suggest bulk cooking options
        
        return weekly_plan
    
    def optimize_for_time(self, weekly_plan: WeeklyMealPlan, max_daily_prep_time: int) -> WeeklyMealPlan:
        """Optimize meal plan for time constraints"""
        # TODO: Implement time optimization
        # - Replace time-consuming recipes with quicker alternatives
        # - Suggest meal prep strategies
        # - Group similar cooking techniques
        
        return weekly_plan

# Main interface class
class SmartMealPlanner:
    """Main interface for the meal planning system"""
    
    def __init__(self, nutrition_calculator: Optional[NutritionCalculator] = None):
        self.recipe_db = RecipeDatabase()
        self.nutrition_calculator = nutrition_calculator or NutritionCalculator()
        self.meal_planner = MealPlanGenerator(self.recipe_db, self.nutrition_calculator)
        self.optimizer = MealPlanOptimizer(self.meal_planner)
        self.persistence = MealPlanPersistence()
        self.meal_prep = MealPrepSuggestions()
    
    def create_user_profile(self, **kwargs) -> UserProfile:
        """Create a user profile for personalized meal planning"""
        return UserProfile(**kwargs)
    
    def generate_meal_plan(self, user_profile: UserProfile, 
                          start_date: date = None,
                          optimize_for: str = None,
                          **preferences) -> WeeklyMealPlan:
        """Generate and optionally optimize a meal plan"""
        
        # Generate base meal plan
        weekly_plan = self.meal_planner.generate_weekly_plan(
            user_profile, start_date, preferences
        )
        
        # Apply optimization if requested
        if optimize_for == 'nutrition':
            weekly_plan = self.optimizer.optimize_for_nutrition(weekly_plan)
        elif optimize_for == 'cost':
            target_budget = preferences.get('target_budget', user_profile.budget_per_day * 7)
            weekly_plan = self.optimizer.optimize_for_cost(weekly_plan, target_budget)
        elif optimize_for == 'time':
            max_time = preferences.get('max_daily_prep_time', user_profile.max_prep_time)
            weekly_plan = self.optimizer.optimize_for_time(weekly_plan, max_time)
        
        return weekly_plan
    
    def export_meal_plan(self, weekly_plan: WeeklyMealPlan, format_type: str = 'json') -> str:
        """Export meal plan in various formats"""
        if format_type == 'json':
            return json.dumps(asdict(weekly_plan), indent=2, default=str)
        elif format_type == 'shopping_list':
            return self._format_shopping_list(weekly_plan.shopping_list)
        elif format_type == 'daily_schedule':
            return self._format_daily_schedule(weekly_plan)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def _format_shopping_list(self, shopping_list: Dict[str, float]) -> str:
        """Format shopping list as readable text"""
        output = "🛒 SHOPPING LIST\n" + "="*50 + "\n\n"
        
        # Group by category (basic grouping)
        categories = {
            'Proteins': [],
            'Vegetables': [],
            'Fruits': [],
            'Grains & Starches': [],
            'Dairy': [],
            'Pantry Items': []
        }
        
        for item, quantity in shopping_list.items():
            # Simple categorization
            item_lower = item.lower()
            if any(protein in item_lower for protein in ['chicken', 'beef', 'fish', 'salmon', 'eggs']):
                categories['Proteins'].append(f"  • {quantity} {item}")
            elif any(veg in item_lower for veg in ['tomato', 'onion', 'broccoli', 'spinach', 'carrot']):
                categories['Vegetables'].append(f"  • {quantity} {item}")
            elif any(fruit in item_lower for fruit in ['banana', 'apple', 'berries', 'lemon']):
                categories['Fruits'].append(f"  • {quantity} {item}")
            elif any(grain in item_lower for grain in ['rice', 'quinoa', 'oats', 'bread']):
                categories['Grains & Starches'].append(f"  • {quantity} {item}")
            elif any(dairy in item_lower for dairy in ['milk', 'cheese', 'yogurt']):
                categories['Dairy'].append(f"  • {quantity} {item}")
            else:
                categories['Pantry Items'].append(f"  • {quantity} {item}")
        
        for category, items in categories.items():
            if items:
                output += f"{category}:\n"
                output += "\n".join(items) + "\n\n"
        
        return output
    
    def _format_daily_schedule(self, weekly_plan: WeeklyMealPlan) -> str:
        """Format daily meal schedule"""
        output = f"📅 WEEKLY MEAL PLAN\n"
        output += f"Week of {weekly_plan.start_date.strftime('%B %d, %Y')}\n"
        output += "="*50 + "\n\n"
        
        for current_date in sorted(weekly_plan.days.keys()):
            day_plan = weekly_plan.days[current_date]
            output += f"{current_date.strftime('%A, %B %d')}\n"
            output += "-" * 30 + "\n"
            
            if day_plan.breakfast:
                output += f"🌅 Breakfast: {day_plan.breakfast.recipe.name}\n"
                output += f"   Prep time: {day_plan.breakfast.recipe.total_time} min\n"
            
            if day_plan.lunch:
                output += f"🌞 Lunch: {day_plan.lunch.recipe.name}\n"
                output += f"   Prep time: {day_plan.lunch.recipe.total_time} min\n"
            
            if day_plan.dinner:
                output += f"🌙 Dinner: {day_plan.dinner.recipe.name}\n"
                output += f"   Prep time: {day_plan.dinner.recipe.total_time} min\n"
            
            if day_plan.snacks:
                output += f"🍎 Snacks: {', '.join([snack.recipe.name for snack in day_plan.snacks])}\n"
            
            output += "\n"
        
        # Add summary
        nutrition_summary = weekly_plan.get_weekly_nutrition_summary()
        avg_nutrition = nutrition_summary.get('average_daily', {})
        
        output += "📊 WEEKLY NUTRITION SUMMARY\n"
        output += "="*30 + "\n"
        output += f"Average daily calories: {avg_nutrition.get('calories', 0):.0f}\n"
        output += f"Average daily protein: {avg_nutrition.get('protein_g', 0):.1f}g\n"
        output += f"Total weekly cost: ${weekly_plan.total_cost:.2f}\n"
        
        return output
    
class MealPrepSuggestions:
    """Generate meal prep and cooking efficiency suggestions"""
    
    def __init__(self):
        self.batch_cooking_ingredients = {
            'grains': ['rice', 'quinoa', 'pasta', 'oats'],
            'proteins': ['chicken', 'beef', 'beans', 'lentils'],
            'vegetables': ['broccoli', 'carrots', 'bell peppers']
        }
    
    def generate_prep_plan(self, weekly_plan: WeeklyMealPlan) -> Dict[str, Any]:
        """Generate meal prep suggestions"""
        prep_plan = {
            'batch_cooking': self._identify_batch_cooking_opportunities(weekly_plan),
            'prep_schedule': self._create_prep_schedule(weekly_plan),
            'storage_tips': self._generate_storage_tips(weekly_plan),
            'time_savings': self._calculate_time_savings(weekly_plan)
        }
        
        return prep_plan
    
    def _identify_batch_cooking_opportunities(self, weekly_plan: WeeklyMealPlan) -> List[Dict[str, Any]]:
        """Identify ingredients that can be batch cooked"""
        ingredient_frequency = defaultdict(list)
        
        # Count ingredient usage across the week
        for day_plan in weekly_plan.days.values():
            for meal in day_plan.get_all_meals():
                for ingredient in meal.recipe.ingredients:
                    # Extract base ingredient name
                    base_ingredient = self._extract_base_ingredient(ingredient)
                    ingredient_frequency[base_ingredient].append({
                        'meal': meal.recipe.name,
                        'date': day_plan.date,
                        'amount': ingredient
                    })
        
        # Find ingredients used multiple times
        batch_opportunities = []
        for ingredient, uses in ingredient_frequency.items():
            if len(uses) >= 2:  # Used in 2 or more meals
                total_amount = self._estimate_total_amount(uses)
                batch_opportunities.append({
                    'ingredient': ingredient,
                    'frequency': len(uses),
                    'total_amount': total_amount,
                    'uses': uses,
                    'suggested_batch_size': self._suggest_batch_size(ingredient, total_amount)
                })
        
        return sorted(batch_opportunities, key=lambda x: x['frequency'], reverse=True)
    
    
    def _generate_storage_tips(self, weekly_plan: WeeklyMealPlan) -> List[str]:
        """Generate food storage tips"""
        tips = [
            "Store cooked grains in airtight containers for up to 5 days",
            "Pre-cut vegetables can be stored for 3-4 days in the refrigerator",
            "Cooked proteins should be consumed within 3-4 days",
            "Freeze portions in individual containers for easy reheating",
            "Label containers with contents and date prepared"
        ]
        
        # Add specific tips based on ingredients
        all_ingredients = set()
        for day_plan in weekly_plan.days.values():
            for meal in day_plan.get_all_meals():
                for ingredient in meal.recipe.ingredients:
                    all_ingredients.add(self._extract_base_ingredient(ingredient))
        
        if 'salad' in ' '.join(all_ingredients).lower():
            tips.append("Store salad dressings separately to prevent wilting")
        
        if any('herb' in ing.lower() for ing in all_ingredients):
            tips.append("Store fresh herbs wrapped in damp paper towels")
        
        return tips
    
    def _calculate_time_savings(self, weekly_plan: WeeklyMealPlan) -> Dict[str, int]:
        """Calculate potential time savings from meal prep"""
        total_cooking_time = 0
        potential_savings = 0
        
        for day_plan in weekly_plan.days.values():
            for meal in day_plan.get_all_meals():
                total_cooking_time += meal.recipe.total_time

                if meal.recipe.total_time > 20:
                    potential_savings += min(15, meal.recipe.total_time * 0.3)
        
        return {
            'total_weekly_cooking_time': total_cooking_time,
            'potential_savings': int(potential_savings),
            'efficiency_improvement': f"{potential_savings/total_cooking_time*100:.1f}%"
        }
    
    def _extract_base_ingredient(self, ingredient_text: str) -> str:
        """Extract base ingredient name"""
        ingredient = ingredient_text.lower()

        measurements = ['cup', 'tbsp', 'tsp', 'oz', 'lb', 'g', 'kg', 'ml', 'l']
        for measure in measurements:
            ingredient = ingredient.replace(measure, '')
        
        import re
        ingredient = re.sub(r'\d+', '', ingredient)
        ingredient = re.sub(r'[\/\-,].*', '', ingredient)  # Remove everything after / - ,
        
        return ingredient.strip()
    
    def _estimate_total_amount(self, uses: List[Dict]) -> str:
        """Estimate total amount needed for batch cooking"""
        amounts = []
        for use in uses:
            amount_text = use['amount']
            import re
            numbers = re.findall(r'\d+(?:\.\d+)?', amount_text)
            if numbers:
                amounts.append(float(numbers[0]))
        
        if amounts:
            total = sum(amounts)
            return f"~{total:.1f} units"
        
        return "Multiple servings"
    
    def _suggest_batch_size(self, ingredient: str, total_amount: str) -> str:
        """Suggest optimal batch cooking size"""
        base_suggestions = {
            'rice': "Cook 2-3 cups dry rice",
            'quinoa': "Cook 1.5-2 cups dry quinoa",
            'chicken': "Cook 2-3 lbs at once",
            'vegetables': "Prep 4-5 cups mixed vegetables"
        }
        
        for key, suggestion in base_suggestions.items():
            if key in ingredient.lower():
                return suggestion
        
        return f"Prepare {total_amount}"    
class MealPlanPersistence:
    """Handle saving and loading meal plans"""
    
    def __init__(self, db_path: str = "meal_plans.db"):
        self.db_path = db_path
        self._setup_database()
    
    def _setup_database(self):
        """Initialize meal plan storage database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    profile_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS weekly_meal_plans (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    start_date DATE NOT NULL,
                    plan_data TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_profiles (id)
                );
                
                CREATE TABLE IF NOT EXISTS meal_plan_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_id TEXT NOT NULL,
                    recipe_id TEXT NOT NULL,
                    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (plan_id) REFERENCES weekly_meal_plans (id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_meal_plans_user_date ON weekly_meal_plans(user_id, start_date);
                CREATE INDEX IF NOT EXISTS idx_feedback_plan ON meal_plan_feedback(plan_id);
            """)
    
    def save_user_profile(self, user_profile: UserProfile) -> str:
        """Save user profile and return profile ID"""
        profile_id = hashlib.md5(f"{user_profile.name}_{datetime.now()}".encode()).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO user_profiles (id, name, profile_data, updated_at)
                VALUES (?, ?, ?, ?)
            """, (
                profile_id,
                user_profile.name,
                json.dumps(asdict(user_profile), default=str),
                datetime.now()
            ))
        
        return profile_id
    
    def load_user_profile(self, profile_id: str) -> Optional[UserProfile]:
        """Load user profile by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT profile_data FROM user_profiles WHERE id = ?
            """, (profile_id,))
            
            row = cursor.fetchone()
            if row:
                profile_data = json.loads(row[0])
                # Convert back to UserProfile object
                return self._dict_to_user_profile(profile_data)
        
        return None
    
    def save_meal_plan(self, meal_plan: WeeklyMealPlan, user_id: str) -> str:
        """Save weekly meal plan and return plan ID"""
        plan_id = hashlib.md5(f"{user_id}_{meal_plan.start_date}_{datetime.now()}".encode()).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO weekly_meal_plans (id, user_id, start_date, plan_data)
                VALUES (?, ?, ?, ?)
            """, (
                plan_id,
                user_id,
                meal_plan.start_date,
                json.dumps(asdict(meal_plan), default=str)
            ))
        
        return plan_id
    
    def load_meal_plan(self, plan_id: str) -> Optional[WeeklyMealPlan]:
        """Load meal plan by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT plan_data FROM weekly_meal_plans WHERE id = ?
            """, (plan_id,))
            
            row = cursor.fetchone()
            if row:
                plan_data = json.loads(row[0])
                return self._dict_to_meal_plan(plan_data)
        
        return None
    
    def get_user_meal_plans(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent meal plans for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, start_date, status, created_at 
                FROM weekly_meal_plans 
                WHERE user_id = ? 
                ORDER BY start_date DESC 
                LIMIT ?
            """, (user_id, limit))
            
            return [
                {
                    'id': row[0],
                    'start_date': row[1],
                    'status': row[2],
                    'created_at': row[3]
                }
                for row in cursor.fetchall()
            ]
    
    def save_meal_feedback(self, plan_id: str, recipe_id: str, rating: int, notes: str = ""):
        """Save user feedback on a meal"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO meal_plan_feedback (plan_id, recipe_id, rating, notes)
                VALUES (?, ?, ?, ?)
            """, (plan_id, recipe_id, rating, notes))
    
    def get_recipe_ratings(self, recipe_id: str) -> Dict[str, float]:
        """Get rating statistics for a recipe"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT rating FROM meal_plan_feedback WHERE recipe_id = ?
            """, (recipe_id,))
            
            ratings = [row[0] for row in cursor.fetchall()]
            
            if not ratings:
                return {'average': 0.0, 'count': 0}
            
            return {
                'average': statistics.mean(ratings),
                'count': len(ratings),
                'distribution': dict(Counter(ratings))
            }
    
    def _dict_to_user_profile(self, data: Dict) -> UserProfile:
        """Convert dictionary back to UserProfile object"""
        # Handle enum conversions
        if 'dietary_preferences' in data:
            data['dietary_preferences'] = [
                DietaryPreference(pref) for pref in data['dietary_preferences']
            ]
        
        if 'cooking_skill' in data:
            data['cooking_skill'] = CookingSkill(data['cooking_skill'])
        
        if 'nutritional_goals' in data:
            data['nutritional_goals'] = NutritionalGoals(**data['nutritional_goals'])
        
        return UserProfile(**data)
    
    def _dict_to_meal_plan(self, data: Dict) -> WeeklyMealPlan:
        """Convert dictionary back to WeeklyMealPlan object"""
        # This would need proper reconstruction of all nested objects
        # For now, returning a simplified version
        meal_plan = WeeklyMealPlan(
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            user_profile=self._dict_to_user_profile(data['user_profile'])
        )
        
        
        return meal_plan

class MealPlanOptimizer:
    """Optimize meal plans for various criteria"""
    
    def __init__(self, meal_planner: 'MealPlanGenerator'):
        self.meal_planner = meal_planner
    
    def optimize_for_nutrition(self, weekly_plan: WeeklyMealPlan) -> WeeklyMealPlan:
        """Optimize meal plan to better meet nutritional goals"""
        nutrition_summary = weekly_plan.get_weekly_nutrition_summary()
        adherence = nutrition_summary.get('goal_adherence', {})
        
        # Find nutrients that need adjustment
        improvements_needed = []
        
        for nutrient, adherence_percent in adherence.items():
            if adherence_percent < 80:  # Under target
                improvements_needed.append((nutrient, 'increase'))
            elif adherence_percent > 120:  # Over target
                improvements_needed.append((nutrient, 'decrease'))
        
        if not improvements_needed:
            return weekly_plan
        
        # Try to swap recipes to improve nutrition
        optimized_plan = self._create_plan_copy(weekly_plan)
        
        for day_date, day_plan in optimized_plan.days.items():
            for meal_type in [MealType.BREAKFAST, MealType.LUNCH, MealType.DINNER]:
                current_meal = self._get_meal_by_type(day_plan, meal_type)
                
                if current_meal:
                    # Find better alternatives
                    alternatives = self._find_nutritional_alternatives(
                        current_meal, improvements_needed, weekly_plan.user_profile
                    )
                    
                    if alternatives:
                        best_alternative = alternatives[0]
                        # Replace the meal
                        self._replace_meal_in_day(day_plan, meal_type, best_alternative)
        
        return optimized_plan
    
    def optimize_for_cost(self, weekly_plan: WeeklyMealPlan, target_budget: float) -> WeeklyMealPlan:
        """Optimize meal plan to meet budget constraints"""
        if weekly_plan.total_cost <= target_budget:
            return weekly_plan
        
        optimized_plan = self._create_plan_copy(weekly_plan)
        cost_reduction_needed = weekly_plan.total_cost - target_budget
        
        # Sort meals by cost per serving (highest first)
        all_meals = []
        for day_date, day_plan in optimized_plan.days.items():
            for meal in day_plan.get_all_meals():
                all_meals.append((meal, day_date, day_plan))
        
        all_meals.sort(key=lambda x: x[0].recipe.cost_per_serving, reverse=True)
        
        # Replace expensive meals with cheaper alternatives
        cost_saved = 0.0
        for meal, day_date, day_plan in all_meals:
            if cost_saved >= cost_reduction_needed:
                break
            
            cheaper_alternatives = self._find_cost_alternatives(
                meal, weekly_plan.user_profile
            )
            
            if cheaper_alternatives:
                alternative = cheaper_alternatives[0]
                cost_difference = meal.recipe.cost_per_serving - alternative.recipe.cost_per_serving
                
                if cost_difference > 0:
                    # Replace the meal
                    self._replace_meal_in_day(day_plan, meal.meal_type, alternative)
                    cost_saved += cost_difference * meal.servings
        
        # Recalculate total cost
        optimized_plan.total_cost = self.meal_planner._calculate_total_cost(optimized_plan)
        
        return optimized_plan
    
    def optimize_for_time(self, weekly_plan: WeeklyMealPlan, max_daily_prep_time: int) -> WeeklyMealPlan:
        """Optimize meal plan for time constraints"""
        optimized_plan = self._create_plan_copy(weekly_plan)
        
        for day_date, day_plan in optimized_plan.days.items():
            total_daily_time = sum(meal.recipe.total_time for meal in day_plan.get_all_meals())
            
            if total_daily_time <= max_daily_prep_time:
                continue
            
            # Find time-efficient alternatives
            all_meals = day_plan.get_all_meals()
            all_meals.sort(key=lambda x: x.recipe.total_time, reverse=True)
            
            for meal in all_meals:
                if total_daily_time <= max_daily_prep_time:
                    break
                
                quicker_alternatives = self._find_time_alternatives(
                    meal, weekly_plan.user_profile
                )
                
                if quicker_alternatives:
                    alternative = quicker_alternatives[0]
                    time_saved = meal.recipe.total_time - alternative.recipe.total_time
                    
                    if time_saved > 0:
                        self._replace_meal_in_day(day_plan, meal.meal_type, alternative)
                        total_daily_time -= time_saved
        
        return optimized_plan
    
    def _create_plan_copy(self, weekly_plan: WeeklyMealPlan) -> WeeklyMealPlan:
        """Create a deep copy of the meal plan"""
        # In practice, implement proper deep copying
        # For now, return the same plan (would need proper implementation)
        return weekly_plan
    
    def _get_meal_by_type(self, day_plan: DayMealPlan, meal_type: MealType) -> Optional[Meal]:
        """Get meal of specific type from day plan"""
        if meal_type == MealType.BREAKFAST:
            return day_plan.breakfast
        elif meal_type == MealType.LUNCH:
            return day_plan.lunch
        elif meal_type == MealType.DINNER:
            return day_plan.dinner
        return None
    
    def _replace_meal_in_day(self, day_plan: DayMealPlan, meal_type: MealType, new_meal: Meal):
        """Replace a meal in the day plan"""
        if meal_type == MealType.BREAKFAST:
            day_plan.breakfast = new_meal
        elif meal_type == MealType.LUNCH:
            day_plan.lunch = new_meal
        elif meal_type == MealType.DINNER:
            day_plan.dinner = new_meal
    
    def _find_nutritional_alternatives(self, current_meal: Meal, 
                                     improvements: List[Tuple[str, str]], 
                                     user_profile: UserProfile) -> List[Meal]:
        """Find recipe alternatives that improve nutrition"""
        candidates = self.meal_planner.recipe_db.get_recipes_by_meal_type(current_meal.meal_type)
        
        scored_alternatives = []
        for recipe in candidates:
            if recipe.id == current_meal.recipe.id:
                continue
            
            score = self._score_nutritional_improvement(recipe, improvements)
            if score > 0:
                alternative_meal = Meal(
                    recipe=recipe,
                    meal_type=current_meal.meal_type,
                    date=current_meal.date,
                    servings=current_meal.servings
                )
                scored_alternatives.append((score, alternative_meal))
        
        scored_alternatives.sort(key=lambda x: x[0], reverse=True)
        return [meal for score, meal in scored_alternatives[:3]]
    
    def _find_cost_alternatives(self, current_meal: Meal, user_profile: UserProfile) -> List[Meal]:
        """Find cheaper recipe alternatives"""
        candidates = self.meal_planner.recipe_db.get_recipes_by_meal_type(current_meal.meal_type)
        
        cheaper_alternatives = []
        for recipe in candidates:
            if (recipe.id != current_meal.recipe.id and 
                recipe.cost_per_serving < current_meal.recipe.cost_per_serving):
                
                alternative_meal = Meal(
                    recipe=recipe,
                    meal_type=current_meal.meal_type,
                    date=current_meal.date,
                    servings=current_meal.servings
                )
                cheaper_alternatives.append(alternative_meal)
        
        # Sort by cost (cheapest first)
        cheaper_alternatives.sort(key=lambda x: x.recipe.cost_per_serving)
        return cheaper_alternatives[:3]
    
    def _find_time_alternatives(self, current_meal: Meal, user_profile: UserProfile) -> List[Meal]:
        """Find quicker recipe alternatives"""
        candidates = self.meal_planner.recipe_db.get_recipes_by_meal_type(current_meal.meal_type)
        
        quicker_alternatives = []
        for recipe in candidates:
            if (recipe.id != current_meal.recipe.id and 
                recipe.total_time < current_meal.recipe.total_time):
                
                alternative_meal = Meal(
                    recipe=recipe,
                    meal_type=current_meal.meal_type,
                    date=current_meal.date,
                    servings=current_meal.servings
                )
                quicker_alternatives.append(alternative_meal)
        
        # Sort by time (quickest first)
        quicker_alternatives.sort(key=lambda x: x.recipe.total_time)
        return quicker_alternatives[:3]
    
    def _score_nutritional_improvement(self, recipe: Recipe, 
                                     improvements: List[Tuple[str, str]]) -> float:
        """Score how well a recipe addresses nutritional improvements"""
        if not recipe.nutrition_per_serving:
            return 0.0
        
        score = 0.0
        nutrition = recipe.nutrition_per_serving
        
        for nutrient, direction in improvements:
            if nutrient in nutrition:
                value = nutrition[nutrient]
                
                if direction == 'increase':
                    # Higher values are better
                    if nutrient == 'protein_g' and value >= 20:
                        score += 10
                    elif nutrient == 'fiber_g' and value >= 5:
                        score += 8
                    elif nutrient == 'calories' and value >= 400:
                        score += 5
                
                elif direction == 'decrease':
                    # Lower values are better
                    if nutrient == 'sodium_mg' and value <= 500:
                        score += 8
                    elif nutrient == 'fat_g' and value <= 10:
                        score += 6
        
        return score
