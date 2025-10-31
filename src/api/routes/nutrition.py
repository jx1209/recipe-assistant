"""
nutrition analysis api endpoints
handles nutrition calculation and analysis for recipes and meal plans
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional, Dict, Any
import logging

from src.models.user import UserResponse
from src.core.nutrition_calculator import NutritionCalculator
from src.database import get_db
from src.auth.dependencies import get_current_user, get_current_user_optional
from src.config.settings import get_settings
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(tags=["nutrition"])
settings = get_settings()


class NutritionAnalysisRequest(BaseModel):
    """request model for nutrition analysis"""
    ingredients: List[str]
    servings: int = 1


class RecipeNutritionRequest(BaseModel):
    """request model for recipe nutrition analysis"""
    recipe_id: int


class MealPlanNutritionRequest(BaseModel):
    """request model for meal plan nutrition analysis"""
    meal_plan_id: int


def get_nutrition_calculator() -> NutritionCalculator:
    """dependency to get nutrition calculator"""
    return NutritionCalculator()


@router.post("/nutrition/analyze", response_model=Dict[str, Any])
async def analyze_nutrition(
    analysis_request: NutritionAnalysisRequest,
    calculator: NutritionCalculator = Depends(get_nutrition_calculator)
):
    """
    analyze nutrition for a list of ingredients
    returns comprehensive nutrition analysis including scores and indicators
    """
    try:
        recipe_data = {
            'ingredients': analysis_request.ingredients,
            'servings': analysis_request.servings
        }
        
        analysis = calculator.analyze_recipe_nutrition(recipe_data)
        
        logger.info(f"analyzed nutrition for {len(analysis_request.ingredients)} ingredients")
        return analysis
        
    except Exception as e:
        logger.error(f"error analyzing nutrition: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error analyzing nutrition"
        )


@router.get("/nutrition/recipe/{recipe_id}", response_model=Dict[str, Any])
async def get_recipe_nutrition(
    recipe_id: int,
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
    calculator: NutritionCalculator = Depends(get_nutrition_calculator)
):
    """
    get comprehensive nutrition analysis for a recipe
    includes stored nutrition data plus calculated analysis
    """
    try:
        db = get_db(settings.DATABASE_URL)
        cursor = db.conn.cursor()
        
        #get recipe
        cursor.execute("""
            SELECT ingredients_json, servings, nutrition_json
            FROM recipes
            WHERE id = ? AND is_deleted = 0
        """, (recipe_id,))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="recipe not found"
            )
        
        import json
        ingredients = json.loads(row['ingredients_json'])
        servings = row['servings']
        
        #convert ingredients to text format for calculator
        ingredient_texts = []
        for ing in ingredients:
            text = ing['name']
            if ing.get('quantity'):
                text = f"{ing['quantity']} {ing.get('unit', '')} {text}".strip()
            ingredient_texts.append(text)
        
        recipe_data = {
            'ingredients': ingredient_texts,
            'servings': servings
        }
        
        analysis = calculator.analyze_recipe_nutrition(recipe_data)
        
        logger.info(f"analyzed nutrition for recipe {recipe_id}")
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"error getting recipe nutrition: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error retrieving recipe nutrition"
        )


@router.get("/nutrition/meal-plan/{meal_plan_id}", response_model=Dict[str, Any])
async def get_meal_plan_nutrition(
    meal_plan_id: int,
    current_user: UserResponse = Depends(get_current_user),
    calculator: NutritionCalculator = Depends(get_nutrition_calculator)
):
    """
    get comprehensive nutrition analysis for an entire meal plan
    aggregates nutrition across all meals in the plan
    """
    try:
        db = get_db(settings.DATABASE_URL)
        cursor = db.conn.cursor()
        
        #get meal plan
        cursor.execute("""
            SELECT meals_json, start_date, end_date
            FROM meal_plans
            WHERE id = ? AND user_id = ?
        """, (meal_plan_id, current_user.id))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="meal plan not found"
            )
        
        import json
        from src.core.nutrition_calculator import NutritionInfo
        
        meals = json.loads(row['meals_json'])
        
        #collect all recipe ids
        recipe_ids = set()
        for day_meals in meals.values():
            for meal_type in ['breakfast', 'lunch', 'dinner']:
                if meal_type in day_meals:
                    recipe_ids.add(day_meals[meal_type]['recipe_id'])
            if 'snacks' in day_meals:
                for snack in day_meals['snacks']:
                    recipe_ids.add(snack['recipe_id'])
        
        #get all recipes and their nutrition
        total_nutrition = NutritionInfo()
        recipe_count = 0
        
        for recipe_id in recipe_ids:
            cursor.execute("""
                SELECT ingredients_json, servings
                FROM recipes
                WHERE id = ? AND is_deleted = 0
            """, (recipe_id,))
            
            recipe_row = cursor.fetchone()
            if recipe_row:
                ingredients = json.loads(recipe_row['ingredients_json'])
                servings = recipe_row['servings']
                
                #convert ingredients to text
                ingredient_texts = []
                for ing in ingredients:
                    text = ing['name']
                    if ing.get('quantity'):
                        text = f"{ing['quantity']} {ing.get('unit', '')} {text}".strip()
                    ingredient_texts.append(text)
                
                recipe_data = {
                    'ingredients': ingredient_texts,
                    'servings': servings
                }
                
                recipe_nutrition = calculator.calculate_recipe_nutrition(recipe_data)
                total_nutrition = total_nutrition + recipe_nutrition
                recipe_count += 1
        
        #calculate per-day averages
        from datetime import datetime
        start_date = datetime.fromisoformat(row['start_date']).date()
        end_date = datetime.fromisoformat(row['end_date']).date()
        num_days = (end_date - start_date).days + 1
        
        per_day_nutrition = total_nutrition.scale(1.0 / num_days) if num_days > 0 else total_nutrition
        
        return {
            'meal_plan_id': meal_plan_id,
            'total_days': num_days,
            'total_recipes': recipe_count,
            'total_nutrition': total_nutrition.__dict__,
            'per_day_nutrition': per_day_nutrition.__dict__,
            'analysis_date': datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"error analyzing meal plan nutrition: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error analyzing meal plan nutrition"
        )


@router.get("/nutrition/daily-targets", response_model=Dict[str, float])
async def get_daily_targets(
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
    calculator: NutritionCalculator = Depends(get_nutrition_calculator)
):
    """
    get recommended daily nutrition targets
    can be customized per user based on preferences (future enhancement)
    """
    from src.core.nutrition_calculator import DailyNutritionTargets
    
    targets = DailyNutritionTargets()
    
    return {
        'calories': targets.calories,
        'protein_g': targets.protein_g,
        'carbs_g': targets.carbs_g,
        'fat_g': targets.fat_g,
        'fiber_g': targets.fiber_g,
        'sodium_mg': targets.sodium_mg,
        'cholesterol_mg': targets.cholesterol_mg,
        'calcium_mg': targets.calcium_mg,
        'iron_mg': targets.iron_mg,
        'vitamin_c_mg': targets.vitamin_c_mg,
        'potassium_mg': targets.potassium_mg,
        'vitamin_a_iu': targets.vitamin_a_iu,
        'vitamin_d_iu': targets.vitamin_d_iu,
        'saturated_fat_g': targets.saturated_fat_g
    }

