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
from functools import lru_cache
import re


try:
    from .recipe_database import AdvancedRecipeDatabase
    from .utils.util_funcs import (
        calculate_ingredient_similarity,
        parse_ingredient_list,
        print_header,
        print_separator,
        get_yes_no_input
    )
except ImportError:
    from recipe_database import AdvancedRecipeDatabase
    from src.utils.util_funcs import (
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
        cleaned_ingredients = [SmartIngredientMatcher._clean_ingredient(ing) for ing in user_ingredients]
        
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
    
    @staticmethod
    @lru_cache(maxsize=500)
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
        from difflib import SequenceMatcher
        if ingredient1.lower() == ingredient2.lower():
                return 1.0

        for base, synonyms in self.ingredient_synonyms.items():
            if (ingredient1.lower() in synonyms and ingredient2.lower() == base) or \
            (ingredient2.lower() in synonyms and ingredient1.lower() == base):
                return 0.95

        # Use fuzzy similarity
        return SequenceMatcher(None, ingredient1.lower(), ingredient2.lower()).ratio()        
    
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
        cleaned_ingredients = [SmartIngredientMatcher._clean_ingredient(ing) for ing in user_ingredients]
        
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
        skipped = 0
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
            else:
                skipped += 1
        
        logger.info(f"Local search: {len(matches)} matches found, {skipped} skipped below threshold ({min_match})")
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
        pantry_items = ['salt', 'sugar', 'oil', 'water', 'pepper']
        
        recipe_ingredients = recipe_data.get('ingredients', [])
        
        matching_ingredients = []
        missing_ingredients = []
        total_similarity_score = 0
        
        for recipe_ingredient in recipe_ingredients:
            cleaned_recipe_ingredient = SmartIngredientMatcher._clean_ingredient(recipe_ingredient)
            best_match_score = 0
            matched = False
            
            for user_ingredient in user_ingredients:
                similarity = self._ingredient_similarity(cleaned_recipe_ingredient, user_ingredient)
                
                if similarity > best_match_score:
                    best_match_score = similarity
                
                if similarity >= 0.7:
                    matched = True

        # Down-weight common pantry items
        if any(p in cleaned_recipe_ingredient for p in pantry_items):
            best_match_score *= 0.5

        total_similarity_score += best_match_score
            
        if matched:
                matching_ingredients.append(recipe_ingredient)
        else:
                missing_ingredients.append(recipe_ingredient)
        
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
    
    def _calculate_confidence_score(self, match_result: Dict, source: str, api: str = None) -> float:
        """Calculate confidence score for the match"""
        base_score = match_result['match_percentage'] / 100
        
        # Bonus for local recipes (more trusted)
        if source == "local":
            base_score += 0.1
        
        # API-specific bonuses
        api_bonuses = {
            "spoonacular": 0.05,  # Generally high quality
            "edamam": 0.03,       # Good nutrition data
            "themealdb": 0.02     # Free but less detailed
        }
        
        if api in api_bonuses:
            base_score += api_bonuses[api]
        
        # Bonus for fewer missing ingredients
        missing_count = len(match_result['missing_ingredients'])
        if missing_count == 0:
            base_score += 0.2
        elif missing_count <= 2:
            base_score += 0.1
        
        return min(base_score, 1.0)
    
    def _generate_ingredient_suggestions(self, 
                                       user_ingredients: List[str], 
                                       matches: List[IngredientMatch]) -> List[str]:
        """Generate suggestions for additional ingredients"""
        suggestions = []
        missing_ingredient_counts = {}
        
        # Count frequently missing ingredients across matches
        for match in matches:
            for missing_ing in match.missing_ingredients:
                cleaned_missing = SmartIngredientMatcher._clean_ingredient(missing_ing)
                missing_ingredient_counts[cleaned_missing] = missing_ingredient_counts.get(cleaned_missing, 0) + 1
        
        # Sort by frequency and suggest top missing ingredients
        sorted_missing = sorted(missing_ingredient_counts.items(), key=lambda x: x[1], reverse=True)
        
        for ingredient, count in sorted_missing[:5]:
            if count >= 2:  # Suggest if missing in at least 2 recipes
                suggestions.append(f"Consider adding '{ingredient}' - needed in {count} recipes")
        
        # Suggest complementary ingredients based on categories
        analysis = self.analyze_ingredients(user_ingredients)
        for missing_category in analysis['missing_categories']:
            category_items = self.ingredient_categories[missing_category]
            suggestions.append(f"Add a {missing_category}: try {', '.join(category_items[:3])}")
        
        return suggestions[:3]  # Limit to top 3 suggestions
    
    def save_favorite_recipe(self, match: IngredientMatch) -> bool:
        """Save an online recipe to local database"""
        if match.source.startswith("online"):
            try:
                recipe_id = self.database.save_online_recipe(match.recipe_data)
                if recipe_id:
                    logger.info(f"Saved favorite recipe: {recipe_id}")
                    return True
            except Exception as e:
                logger.error(f"Failed to save recipe: {e}")
        return False
    
    def get_recipe_suggestions_interactive(self) -> RecipeSuggestion:
        """Interactive ingredient input and recipe suggestion"""
        print_header("Smart Recipe Finder")
        print("Enter your available ingredients to find matching recipes!")
        print("I'll search both local recipes and online sources for the best matches.\n")
        
        # Get ingredients from user
        ingredients = self._get_ingredients_interactive()
        
        if not ingredients:
            print("No ingredients provided. Please try again.")
            return RecipeSuggestion([], 0, 0.0, [], [])
        
        print(f"\nAnalyzing your ingredients: {', '.join(ingredients)}")
        
        # Analyze ingredients
        analysis = self.analyze_ingredients(ingredients)
        self._display_ingredient_analysis(analysis)
        
        # Ask about online search
        include_online = get_yes_no_input("\nWould you like to search online recipe sources?")
        
        print("\nSearching for matching recipes...")
        
        # Find matches
        suggestion = self.find_matching_recipes(
            ingredients, 
            include_online=include_online,
            max_results=10
        )
        
        # Display results
        self._display_recipe_suggestions(suggestion)
        
        return suggestion
    
    def _get_ingredients_interactive(self) -> List[str]:
        """Get ingredients from user with helpful prompts"""
        print("Enter your ingredients separated by commas.")
        print("Example: chicken breast, rice, onions, garlic, soy sauce")
        print("Or type 'help' for more guidance\n")
        
        while True:
            user_input = input("Your ingredients: ").strip()
            
            if user_input.lower() == 'help':
                self._show_ingredient_help()
                continue
            elif not user_input:
                print("Please enter at least one ingredient.")
                continue
            
            ingredients = parse_ingredient_list(user_input)
            
            if ingredients:
                # Ask for confirmation
                print(f"\nI found these ingredients: {', '.join(ingredients)}")
                if get_yes_no_input("Is this correct?"):
                    return ingredients
                else:
                    print("Please enter your ingredients again:")
            else:
                print("Please enter valid ingredients separated by commas.")
    
    def _show_ingredient_help(self):
        """Show helpful guidance for ingredient input"""
        print("\nIngredient Input Guide:")
        print("- Use simple names: 'chicken' instead of '2 lbs chicken breast'")
        print("- Separate with commas: 'tomatoes, onions, garlic'")
        print("- Don't worry about exact quantities")
        print("- Include seasonings and sauces you have")
        print("\nExample categories to consider:")
        for category, items in list(self.ingredient_categories.items())[:4]:
            print(f"- {category.title()}: {', '.join(items[:4])}")
        print()
    
    def _display_ingredient_analysis(self, analysis: Dict):
        """Display ingredient analysis to user"""
        print("\n" + "="*50)
        print("INGREDIENT ANALYSIS")
        print("="*50)
        
        if analysis['categories']:
            print("Your ingredients by category:")
            for category, items in analysis['categories'].items():
                print(f"  {category.title()}: {', '.join(items)}")
        
        if analysis['missing_categories']:
            print(f"\nMissing categories: {', '.join(analysis['missing_categories'])}")
            print("Consider adding items from these categories for more recipe options.")
        
        if analysis['substitution_suggestions']:
            print("\nPossible substitutions:")
            for ingredient, subs in list(analysis['substitution_suggestions'].items())[:3]:
                print(f"  {ingredient} → {', '.join(subs[:2])}")
        
        print("="*50)
    
    def _display_recipe_suggestions(self, suggestion: RecipeSuggestion):
        """Display recipe suggestions to user"""
        print_separator()
        print(f"RECIPE SUGGESTIONS ({suggestion.total_found} found in {suggestion.search_time:.2f}s)")
        print_separator()
        
        if not suggestion.matches:
            print("No matching recipes found.")
            print("Try adding more common ingredients or check your spelling.")
            return
        
        # Group by match quality
        excellent_matches = [m for m in suggestion.matches if m.match_percentage >= 80]
        good_matches = [m for m in suggestion.matches if 60 <= m.match_percentage < 80]
        okay_matches = [m for m in suggestion.matches if m.match_percentage < 60]
        
        # Display excellent matches
        if excellent_matches:
            print("🌟 EXCELLENT MATCHES (80%+ ingredients):")
            for i, match in enumerate(excellent_matches[:3], 1):
                self._display_match_summary(match, i)
        
        # Display good matches
        if good_matches:
            print("\n✅ GOOD MATCHES (60-79% ingredients):")
            for i, match in enumerate(good_matches[:3], len(excellent_matches) + 1):
                self._display_match_summary(match, i)
        
        # Display okay matches
        if okay_matches and len(excellent_matches + good_matches) < 3:
            print("\n📝 POSSIBLE MATCHES (under 60% ingredients):")
            for i, match in enumerate(okay_matches[:2], len(excellent_matches + good_matches) + 1):
                self._display_match_summary(match, i)
        
        # Show suggestions
        if suggestion.suggestions:
            print("\n💡 SUGGESTIONS TO IMPROVE MATCHES:")
            for suggestion_text in suggestion.suggestions:
                print(f"  • {suggestion_text}")
        
        # Show online sources used
        if suggestion.used_online_apis:
            print(f"\n🌐 Searched online sources: {', '.join(suggestion.used_online_apis)}")
        
        print_separator()
    
    def _display_match_summary(self, match: IngredientMatch, index: int):
        """Display a single recipe match summary with enhanced formatting"""
        recipe_data = match.recipe_data
        
        # Header with recipe name and match percentage
        match_emoji = "🌟" if match.match_percentage >= 80 else "✅" if match.match_percentage >= 60 else "📝"
        print(f"\n{match_emoji} {index}. {match.recipe_name}")
        
        # Match percentage with confidence indicator
        confidence_indicator = "🔥" if match.confidence_score > 0.8 else "👍" if match.confidence_score > 0.6 else ""
        print(f"   📊 Match: {match.match_percentage:.0f}% {confidence_indicator}")
        
        # Basic recipe info in a clean row
        info_parts = []
        
        # Cook time
        cook_time = recipe_data.get('cook_time', 'Unknown')
        info_parts.append(f"⏱️ {cook_time}")
        
        # Difficulty with color coding
        difficulty = recipe_data.get('difficulty', 'Unknown')
        difficulty_emoji = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}.get(difficulty, "⚪")
        info_parts.append(f"{difficulty_emoji} {difficulty}")
        
        # Servings
        servings = recipe_data.get('servings', 'Unknown')
        if servings != 'Unknown':
            info_parts.append(f"👥 {servings} servings")
        
        # Source with appropriate icon
        source_icon = "🏠" if match.source == "local" else "🌐"
        source_display = match.source.replace("online_", "").title() if match.source.startswith("online_") else "Local"
        info_parts.append(f"{source_icon} {source_display}")
        
        print(f"   {' | '.join(info_parts)}")
        
        # Additional info row (cuisine, rating, etc.)
        extra_info = []
        
        cuisine = recipe_data.get('cuisine', '')
        if cuisine and cuisine.strip():
            extra_info.append(f"🍽️ {cuisine}")
        
        rating = recipe_data.get('rating', 0)
        if rating and rating > 0:
            stars = "⭐" * min(int(rating), 5)
            extra_info.append(f"{stars} ({rating:.1f})")
        
        tags = recipe_data.get('tags', [])
        if tags and len(tags) > 0:
            # Show first 2 tags
            tag_display = ', '.join(tags[:2])
            if len(tags) > 2:
                tag_display += f" (+{len(tags)-2} more)"
            extra_info.append(f"🏷️ {tag_display}")
        
        if extra_info:
            print(f"   {' | '.join(extra_info)}")
        
        # Ingredients status
        total_ingredients = len(recipe_data.get('ingredients', []))
        matching_count = len(match.matching_ingredients)
        missing_count = len(match.missing_ingredients)
        
        print(f"   🥘 Ingredients: {matching_count}/{total_ingredients} available")
        
        # Show matching ingredients (if not too many)
        if matching_count > 0 and matching_count <= 5:
            matching_display = ', '.join(match.matching_ingredients[:5])
            print(f"   ✅ Have: {matching_display}")
        elif matching_count > 5:
            matching_display = ', '.join(match.matching_ingredients[:3])
            print(f"   ✅ Have: {matching_display} (+{matching_count-3} more)")
        
        # Show missing ingredients
        if missing_count > 0:
            if missing_count <= 4:
                missing_display = ', '.join(match.missing_ingredients)
                print(f"   🛒 Need: {missing_display}")
            else:
                missing_display = ', '.join(match.missing_ingredients[:3])
                print(f"   🛒 Need: {missing_display} (+{missing_count-3} more)")
        
        # Recipe description (if available and not too long)
        description = recipe_data.get('description', '')
        if description and len(description.strip()) > 0:
            # Clean HTML tags and truncate
            import re
            clean_desc = re.sub(r'<[^>]+>', '', description)
            if len(clean_desc) > 100:
                clean_desc = clean_desc[:97] + "..."
            print(f"   💭 {clean_desc}")
        
        # Nutrition highlight (if available)
        nutrition = recipe_data.get('nutrition', {})
        if nutrition and isinstance(nutrition, dict):
            nutrition_parts = []
            for key in ['calories', 'protein', 'carbs']:
                if key in nutrition:
                    nutrition_parts.append(f"{key}: {nutrition[key]}")
            
            if nutrition_parts:
                nutrition_display = ' | '.join(nutrition_parts[:3])
                print(f"   🥗 Nutrition: {nutrition_display}")
        
        # Special indicators
        indicators = []
        
        # Dietary restrictions
        dietary = recipe_data.get('dietary_restrictions', [])
        if dietary:
            dietary_icons = {
                'vegetarian': '🌱',
                'vegan': '🌿', 
                'gluten-free': '🚫🌾',
                'dairy-free': '🚫🥛'
            }
            for restriction in dietary[:3]:
                icon = dietary_icons.get(restriction.lower(), '🏷️')
                indicators.append(f"{icon} {restriction}")
        
        # Quick/easy indicators
        cook_time_str = recipe_data.get('cook_time', '').lower()
        if any(word in cook_time_str for word in ['15', '20', 'quick', 'fast']):
            indicators.append("⚡ Quick")
        
        if indicators:
            print(f"   🎯 {' | '.join(indicators)}")
        
        # Add subtle separator for readability
        print("   " + "─" * 50)

def main():
    """Interactive ingredient matcher main function"""
    try:
        matcher = SmartIngredientMatcher()
        suggestion = matcher.get_recipe_suggestions_interactive()
        
        if suggestion.matches:
            print("\nWould you like to see detailed instructions for any recipe?")
            choice = input("Enter recipe number (or 'quit'): ").strip()
            
            try:
                recipe_num = int(choice) - 1
                if 0 <= recipe_num < len(suggestion.matches):
                    match = suggestion.matches[recipe_num]
                    
                    print_header(f"RECIPE: {match.recipe_name}")
                    recipe_data = match.recipe_data
                    
                    print(f"Servings: {recipe_data.get('servings', 'Unknown')}")
                    print(f"Cook Time: {recipe_data.get('cook_time', 'Unknown')}")
                    print(f"Difficulty: {recipe_data.get('difficulty', 'Unknown')}")
                    
                    print_separator()
                    print("INGREDIENTS:")
                    for ingredient in recipe_data.get('ingredients', []):
                        status = "✅" if ingredient in match.matching_ingredients else "🛒"
                        print(f"  {status} {ingredient}")
                    
                    print_separator()
                    print("INSTRUCTIONS:")
                    for i, instruction in enumerate(recipe_data.get('instructions', []), 1):
                        print(f"  {i}. {instruction}")
                    
                    # Offer to save online recipes
                    if match.source.startswith("online"):
                        if get_yes_no_input(f"\nSave '{match.recipe_name}' to your recipe collection?"):
                            if matcher.save_favorite_recipe(match):
                                print("Recipe saved successfully!")
                            else:
                                print("Failed to save recipe.")
                    
                    print_separator()
            
            except (ValueError, IndexError):
                print("Invalid recipe number.")

    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"Error in ingredient matcher: {e}")

if __name__ == "__main__":
    main()