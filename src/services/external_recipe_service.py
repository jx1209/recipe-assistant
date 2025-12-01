from typing import List, Optional, Dict, Any
import httpx
import logging
from src.models.recipe import RecipeCreate, RecipeIngredient, DifficultyLevel

logger = logging.getLogger(__name__)

class ExternalRecipeService:
    
    def __init__(self):
        self.themealdb_base_url = "https://www.themealdb.com/api/json/v1/1"
        
    async def search_recipes(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        recipes = []
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.themealdb_base_url}/search.php",
                    params={"s": query}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    meals = data.get("meals", [])
                    
                    if meals:
                        for meal in meals[:limit]:
                            recipe = self._convert_meal_to_recipe(meal)
                            if recipe:
                                recipes.append(recipe)
                                
        except Exception as e:
            logger.error(f"Error fetching recipes from TheMealDB: {e}")
            
        return recipes
    
    async def get_random_recipes(self, count: int = 6) -> List[Dict[str, Any]]:
        recipes = []
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                for _ in range(count):
                    response = await client.get(f"{self.themealdb_base_url}/random.php")
                    
                    if response.status_code == 200:
                        data = response.json()
                        meals = data.get("meals", [])
                        
                        if meals:
                            recipe = self._convert_meal_to_recipe(meals[0])
                            if recipe:
                                recipes.append(recipe)
                                
        except Exception as e:
            logger.error(f"Error fetching random recipes: {e}")
            
        return recipes
    
    async def search_by_category(self, category: str) -> List[Dict[str, Any]]:
        recipes = []
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.themealdb_base_url}/filter.php",
                    params={"c": category}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    meals = data.get("meals", [])
                    
                    if meals:
                        for meal in meals[:10]:
                            detail_response = await client.get(
                                f"{self.themealdb_base_url}/lookup.php",
                                params={"i": meal["idMeal"]}
                            )
                            
                            if detail_response.status_code == 200:
                                detail_data = detail_response.json()
                                detail_meals = detail_data.get("meals", [])
                                
                                if detail_meals:
                                    recipe = self._convert_meal_to_recipe(detail_meals[0])
                                    if recipe:
                                        recipes.append(recipe)
                                        
        except Exception as e:
            logger.error(f"Error fetching recipes by category: {e}")
            
        return recipes
    
    def _convert_meal_to_recipe(self, meal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            ingredients = []
            for i in range(1, 21):
                ingredient_key = f"strIngredient{i}"
                measure_key = f"strMeasure{i}"
                
                ingredient_name = meal.get(ingredient_key, "").strip()
                measure = meal.get(measure_key, "").strip()
                
                if ingredient_name:
                    ingredients.append({
                        "name": ingredient_name,
                        "quantity": measure if measure else None,
                        "unit": None
                    })
            
            instructions_text = meal.get("strInstructions", "")
            instructions = [s.strip() for s in instructions_text.split(".") if s.strip() and len(s.strip()) > 10]
            
            tags = []
            if meal.get("strCategory"):
                tags.append(meal["strCategory"].lower())
            if meal.get("strArea"):
                tags.append(meal["strArea"].lower())
            meal_tags = meal.get("strTags", "")
            if meal_tags:
                tags.extend([tag.strip().lower() for tag in meal_tags.split(",")])
            
            return {
                "id": f"ext_{meal['idMeal']}",
                "title": meal.get("strMeal", "Unknown Recipe"),
                "description": instructions_text[:200] + "..." if len(instructions_text) > 200 else instructions_text,
                "image_url": meal.get("strMealThumb"),
                "source_url": meal.get("strSource"),
                "source_name": "TheMealDB",
                "ingredients": ingredients,
                "instructions": instructions,
                "cuisine": meal.get("strArea"),
                "category": meal.get("strCategory"),
                "tags": tags,
                "servings": 4,
                "difficulty": "medium",
                "external": True,
                "prep_time": 15,
                "cook_time": 30,
                "average_rating": 4.5
            }
            
        except Exception as e:
            logger.error(f"Error converting meal to recipe: {e}")
            return None

