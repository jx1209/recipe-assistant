"""
Intelligent Ingredient Recipe Matcher
Advanced system for matching user ingredients to recipes with online integration
"""

import os
import json
import logging
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import re

try:
    from .recipe_database import AdvancedRecipeDatabase
    from .utils import (
        calculate_ingredient_similarity,
        parse_ingredient_list,
        print_header,
        print_separator,
        get_yes_no_input
    )
except ImportError:
    from recipe_database import AdvancedRecipeDatabase
    from utils import (
        calculate_ingredient_similarity,
        parse_ingredient_list,
        print_header,
        print_separator,
        get_yes_no_input
    )

logger = logging.getLogger(__name__)

@dataclass
class IngredientMatch:
    """Data class for ingredient matching results"""
    recipe_id: str
    recipe_name: str
    match_percentage: float
    matching_ingredients: List[str]
    missing_ingredients: List[str]
    recipe_data: Dict[str, Any]
    source: str = "local"  # "local" or "online"
    confidence_score: float = 0.0

@dataclass
class RecipeSuggestion:
    """Data class for recipe suggestions"""
    matches: List[IngredientMatch]
    total_found: int
    search_time: float
    used_online_apis: List[str]
    suggestions: List[str]  # Suggestions for missing ingredients

class SmartIngredientMatcher:
    """Advanced ingredient matching with online recipe integration"""
    
    def __init__(self, database: Optional[AdvancedRecipeDatabase] = None):
        """Initialize the ingredient matcher"""
        self.database = database or AdvancedRecipeDatabase()
        
        # Load ingredient knowledge base
        self.ingredient_synonyms = self._load_ingredient_synonyms()
        self.ingredient_categories = self._load_ingredient_categories()
        self.common_substitutions = self._load_substitutions()
        
        # Matching parameters
        self.min_match_threshold = 0.3
        self.excellent_match_threshold = 0.8
        self.good_match_threshold = 0.6
        
        # Online API preferences
        self.preferred_apis = ["spoonacular", "edamam", "themealdb"]
        self.max_online_results = 5
        
        logger.info("Smart Ingredient Matcher initialized")
    
    def _load_ingredient_synonyms(self) -> Dict[str, List[str]]:
        """Load ingredient synonyms for better matching"""
        return {
            "tomato": ["tomatoes", "roma tomato", "cherry tomato", "plum tomato"],
            "onion": ["onions", "yellow onion", "white onion", "sweet onion"],
            "garlic": ["garlic cloves", "garlic bulb", "minced garlic"],
            "chicken": ["chicken breast", "chicken thighs", "chicken drumsticks"],
            "beef": ["ground beef", "beef chuck", "beef sirloin", "steak"],
            "pasta": ["spaghetti", "penne", "macaroni", "fettuccine", "linguine"],
            "cheese": ["cheddar", "mozzarella", "parmesan", "swiss cheese"],
            "milk": ["whole milk", "2% milk", "skim milk", "low-fat milk"],
            "oil": ["olive oil", "vegetable oil", "canola oil", "coconut oil"],
            "flour": ["all-purpose flour", "wheat flour", "self-rising flour"],
            "sugar": ["white sugar", "brown sugar", "granulated sugar"],
            "herbs": ["fresh herbs", "dried herbs", "basil", "oregano", "thyme"],
            "vegetables": ["mixed vegetables", "fresh vegetables", "frozen vegetables"]
        }
    
    def _load_ingredient_categories(self) -> Dict[str, List[str]]:
        """Load ingredient categories for smart suggestions"""
        return {
            "proteins": ["chicken", "beef", "pork", "fish", "salmon", "tuna", "eggs", "tofu", "beans"],
            "vegetables": ["tomato", "onion", "carrot", "celery", "pepper", "broccoli", "spinach"],
            "grains": ["rice", "pasta", "bread", "quinoa", "oats", "barley"],
            "dairy": ["milk", "cheese", "butter", "yogurt", "cream"],
            "herbs_spices": ["basil", "oregano", "thyme", "salt", "pepper", "garlic", "ginger"],
            "oils_fats": ["olive oil", "butter", "coconut oil", "vegetable oil"],
            "pantry": ["flour", "sugar", "baking powder", "vanilla", "soy sauce"]
        }
    
    def _load_substitutions(self) -> Dict[str, List[str]]:
        """Load common ingredient substitutions"""
        return {
            "butter": ["margarine", "oil", "coconut oil"],
            "milk": ["almond milk", "soy milk", "coconut milk"],
            "eggs": ["flax eggs", "applesauce", "banana"],
            "flour": ["almond flour", "coconut flour", "oat flour"],
            "sugar": ["honey", "maple syrup", "stevia"],
            "heavy cream": ["milk + butter", "coconut cream"],
            "sour cream": ["yogurt", "coconut cream"],
            "breadcrumbs": ["crushed crackers", "panko", "oats"]
        }
    
    def analyze_ingredients(self, user_ingredients: List[str]) -> Dict[str, Any]:
        """Analyze user ingredients and provide insights"""
        cleaned_ingredients = [self._clean_ingredient(ing) for ing in user_ingredients]
        
        analysis = {
            "original_ingredients": user_ingredients,
            "cleaned_ingredients": cleaned_ingredients,
            "categories": {},
            "missing_categories": [],
            "substitution_suggestions": {},
            "pantry_items": [],
            "fresh_items": []
        }
        
        # Categorize ingredients
        for ingredient in cleaned_ingredients:
            for category, items in self.ingredient_categories.items():
                if any(self._ingredient_similarity(ingredient, item) > 0.7 for item in items):
                    if category not in analysis["categories"]:
                        analysis["categories"][category] = []
                    analysis["categories"][category].append(ingredient)
        
        # Find missing essential categories
        essential_categories = ["proteins", "vegetables", "grains"]
        for category in essential_categories:
            if category not in analysis["categories"]:
                analysis["missing_categories"].append(category)
        
        # Suggest substitutions for common items
        for ingredient in cleaned_ingredients:
            if ingredient in self.common_substitutions:
                analysis["substitution_suggestions"][ingredient] = self.common_substitutions[ingredient]
        
        # Classify as pantry vs fresh
        pantry_keywords = ["flour", "sugar", "salt", "pepper", "oil", "vinegar", "sauce"]
        for ingredient in cleaned_ingredients:
            is_pantry = any(keyword in ingredient.lower() for keyword in pantry_keywords)
            if is_pantry:
                analysis["pantry_items"].append(ingredient)
            else:
                analysis["fresh_items"].append(ingredient)
        
        return analysis
    
    def _clean_ingredient(self, ingredient: str) -> str:
        """Clean and normalize ingredient names"""
        # Remove measurements and quantities
        cleaned = re.sub(r'\d+(?:\.\d+)?(?:\s*(?:cups?|tbsp|tsp|lbs?|oz|grams?|kg))?', '', ingredient)
        
        # Remove common descriptors
        descriptors = ["fresh", "dried", "frozen", "canned", "chopped", "diced", "minced", "sliced"]
        for desc in descriptors:
            cleaned = re.sub(rf'\b{desc}\b', '', cleaned, flags=re.IGNORECASE)
        
        # Clean up spaces and punctuation
        cleaned = re.sub(r'[^\w\s]', '', cleaned)
        cleaned = ' '.join(cleaned.split()).strip().lower()
        
        return cleaned
    
    def _ingredient_similarity(self, ingredient1: str, ingredient2: str) -> float:
        """Calculate similarity between ingredients using enhanced matching"""
        # Direct match
        if ingredient1.lower() == ingredient2.lower():
            return 1.0
        
        # Check synonyms
        for base_ingredient, synonyms in self.ingredient_synonyms.items():
            if (ingredient1.lower() in synonyms and ingredient2.lower() == base_ingredient) or \
               (ingredient2.lower() in synonyms and ingredient1.lower() == base_ingredient):
                return 0.95
        
        # Use existing similarity function
        return calculate_ingredient_similarity(ingredient1, ingredient2)
    
    def find_matching_recipes(self, 
                            user_ingredients: List[str],
                            include_online: bool = True,
                            min_match_percentage: float = 30.0,
                            max_results: int = 10) -> RecipeSuggestion:
        """Find recipes matching user ingredients from local and online sources"""
        
        start_time = datetime.now()
        all_matches = []
        used_apis = []
        
        # Clean user ingredients
        cleaned_ingredients = [self._clean_ingredient(ing) for ing in user_ingredients]
        
        # Search local database first
        local_matches = self._search_local_recipes(cleaned_ingredients, min_match_percentage)
        all_matches.extend(local_matches)
        
        # Search online APIs if enabled
        if include_online and len(all_matches) < max_results:
            online_matches, apis_used = self._search_online_recipes(
                cleaned_ingredients, 
                max_results - len(all_matches)
            )
            all_matches.extend(online_matches)
            used_apis.extend(apis_used)
        
        # Sort by match percentage and confidence
        all_matches.sort(key=lambda x: (x.match_percentage, x.confidence_score), reverse=True)
        
        # Limit results
        final_matches = all_matches[:max_results]
        
        # Generate suggestions for missing ingredients
        suggestions = self._generate_ingredient_suggestions(cleaned_ingredients, final_matches)
        
        search_time = (datetime.now() - start_time).total_seconds()
        
        return RecipeSuggestion(
            matches=final_matches,
            total_found=len(all_matches),
            search_time=search_time,
            used_online_apis=used_apis,
            suggestions=suggestions
        )
    
    def _search_local_recipes(self, ingredients: List[str], min_match: float) -> List[IngredientMatch]:
        """Search local recipe database"""
        matches = []
        local_recipes = self.database.get_all_recipes()
        
        for recipe_id, recipe_data in local_recipes.items():
            match_result = self._calculate_recipe_match(ingredients, recipe_data)
            
            if match_result['match_percentage'] >= min_match:
                confidence = self._calculate_confidence_score(match_result, "local")
                
                match = IngredientMatch(
                    recipe_id=recipe_id,
                    recipe_name=recipe_data['name'],
                    match_percentage=match_result['match_percentage'],
                    matching_ingredients=match_result['matching_ingredients'],
                    missing_ingredients=match_result['missing_ingredients'],
                    recipe_data=recipe_data,
                    source="local",
                    confidence_score=confidence
                )
                matches.append(match)
        
        return matches
    
    def _search_online_recipes(self, ingredients: List[str], max_results: int) -> Tuple[List[IngredientMatch], List[str]]:
        """Search online recipe APIs"""
        matches = []
        used_apis = []
        
        for api in self.preferred_apis:
            if len(matches) >= max_results:
                break
            
            try:
                online_recipes = self.database.fetch_recipes_online(
                    ingredients=ingredients,
                    api_source=api,
                    max_results=min(max_results - len(matches), self.max_online_results)
                )
                
                if online_recipes:
                    used_apis.append(api)
                    
                    for recipe_data in online_recipes:
                        match_result = self._calculate_recipe_match(ingredients, recipe_data)
                        confidence = self._calculate_confidence_score(match_result, "online", api)
                        
                        match = IngredientMatch(
                            recipe_id=f"online_{api}_{len(matches)}",
                            recipe_name=recipe_data['name'],
                            match_percentage=match_result['match_percentage'],
                            matching_ingredients=match_result['matching_ingredients'],
                            missing_ingredients=match_result['missing_ingredients'],
                            recipe_data=recipe_data,
                            source=f"online_{api}",
                            confidence_score=confidence
                        )
                        matches.append(match)
            
            except Exception as e:
                logger.warning(f"Failed to search {api}: {e}")
        
        return matches, used_apis
    
    def _calculate_recipe_match(self, user_ingredients: List[str], recipe_data: Dict) -> Dict:
        """Calculate how well recipe matches user ingredients"""
        recipe_ingredients = recipe_data.get('ingredients', [])
        
        matching_ingredients = []
        missing_ingredients = []
        total_similarity_score = 0
        
        for recipe_ingredient in recipe_ingredients:
            cleaned_recipe_ingredient = self._clean_ingredient(recipe_ingredient)
            best_match_score = 0
            matched = False
            
            for user_ingredient in user_ingredients:
                similarity = self._ingredient_similarity(cleaned_recipe_ingredient, user_ingredient)
                
                if similarity > best_match_score:
                    best_match_score = similarity
                
                if similarity >= 0.7:
                    matched = True
            
            total_similarity_score += best_match_score
            
            if matched:
                matching_ingredients.append(recipe_ingredient)
            else:
                missing_ingredients.append(recipe_ingredient)
        
        # Calculate match percentage
        if len(recipe_ingredients) > 0:
            match_percentage = (total_similarity_score / len(recipe_ingredients)) * 100
        else:
            match_percentage = 0
        
        return {
            'match_percentage': match_percentage,
            'matching_ingredients': matching_ingredients,
            'missing_ingredients': missing_ingredients,
            'total_similarity': total_similarity_score
        }
    
