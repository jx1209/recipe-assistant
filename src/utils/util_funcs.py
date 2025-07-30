"""
Utility Functions
Helper functions used throughout the Recipe Assistant application
"""

import re
import time
from typing import List, Dict, Any

def clean_ingredient_name(ingredient: str) -> str:
    """
    Clean and standardize ingredient names
    Remove extra spaces, convert to lowercase, handle plurals
    """
    if not ingredient:
        return ""
    
    cleaned = ingredient.lower().strip()

    measurement_words = ['cup', 'cups', 'tbsp', 'tsp', 'lb', 'lbs', 'oz', 'pound', 'pounds']
    for word in measurement_words:
        cleaned = re.sub(rf'\b{word}\b', '', cleaned)
    
    # remove common prefixes and suffixes
    cleaned = re.sub(r'[\d\-\(\)\/]', '', cleaned)
    
    # clean up extra spaces
    cleaned = ' '.join(cleaned.split())
    
    return cleaned

def calculate_ingredient_similarity(ingredient1: str, ingredient2: str) -> float:
    """
    Calculate similarity between two ingredients
    Returns a score between 0 and 1
    """
    ing1 = clean_ingredient_name(ingredient1)
    ing2 = clean_ingredient_name(ingredient2)
    
    if ing1 == ing2:
        return 1.0
    
    # check if one contains the other
    if ing1 in ing2 or ing2 in ing1:
        return 0.8
    
    # common ingredient substitutions
    substitutions = {
        'chicken breast': 'chicken',
        'ground beef': 'beef',
        'olive oil': 'oil',
        'vegetable oil': 'oil',
        'fresh herbs': 'herbs',
        'mixed vegetables': 'vegetables',
        'chicken broth': 'broth',
        'vegetable broth': 'broth'
    }
    
    for key, value in substitutions.items():
        if (ing1 == key and ing2 == value) or (ing1 == value and ing2 == key):
            return 0.9
    
    words1 = set(ing1.split())
    words2 = set(ing2.split())
    
    if words1 and words2:
        overlap = len(words1.intersection(words2))
        total_words = len(words1.union(words2))
        return overlap / total_words if total_words > 0 else 0.0
    
    return 0.0

def format_cooking_time(minutes: int) -> str:
    """
    Format cooking time in a human-readable way
    """
    if minutes < 60:
        return f"{minutes} minutes"
    elif minutes == 60:
        return "1 hour"
    else:
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes == 0:
            return f"{hours} hours"
        else:
            return f"{hours} hours {remaining_minutes} minutes"

def validate_recipe_data(recipe_data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate recipe data structure
    Returns (is_valid, list_of_errors)
    """
    errors = []
    required_fields = ['name', 'ingredients', 'instructions', 'cook_time', 'difficulty', 'servings']
    
    # check and validate required/ spec fields
    for field in required_fields:
        if field not in recipe_data:
            errors.append(f"Missing required field: {field}")
    
    if 'ingredients' in recipe_data:
        if not isinstance(recipe_data['ingredients'], list) or len(recipe_data['ingredients']) == 0:
            errors.append("Ingredients must be a non-empty list")
    
    if 'instructions' in recipe_data:
        if not isinstance(recipe_data['instructions'], list) or len(recipe_data['instructions']) == 0:
            errors.append("Instructions must be a non-empty list")
    
    if 'servings' in recipe_data:
        try:
            servings = int(recipe_data['servings'])
            if servings <= 0:
                errors.append("Servings must be a positive number")
        except (ValueError, TypeError):
            errors.append("Servings must be a valid number")
    
    if 'difficulty' in recipe_data:
        valid_difficulties = ['Easy', 'Medium', 'Hard']
        if recipe_data['difficulty'] not in valid_difficulties:
            errors.append(f"Difficulty must be one of: {', '.join(valid_difficulties)}")
    
    return len(errors) == 0, errors

def parse_ingredient_list(ingredient_string: str) -> List[str]:
    """
    Parse a comma-separated string of ingredients into a clean list
    """
    if not ingredient_string:
        return []
    
    # split by commas and clean each ingredient
    ingredients = []
    for ingredient in ingredient_string.split(','):
        cleaned = ingredient.strip()
        if cleaned:
            ingredients.append(cleaned)
    
    return ingredients

def get_recipe_id_from_name(recipe_name: str) -> str:
    """
    Generate a recipe ID from the recipe name
    """
    if not recipe_name:
        return f"recipe_{int(time.time())}"
    
    # Convert to lowercase, replace spaces with underscores, remove special chars
    recipe_id = recipe_name.lower()
    recipe_id = re.sub(r'[^a-z0-9\s]', '', recipe_id)
    recipe_id = re.sub(r'\s+', '_', recipe_id)
    recipe_id = recipe_id.strip('_')
    
    return recipe_id if recipe_id else f"recipe_{int(time.time())}"

def format_recipe_summary(recipe_data: Dict[str, Any], match_percentage: float = None) -> str:
    """
    Format a recipe into a summary string
    """
    name = recipe_data.get('name', 'Unknown Recipe')
    cook_time = recipe_data.get('cook_time', 'Unknown')
    difficulty = recipe_data.get('difficulty', 'Unknown')
    servings = recipe_data.get('servings', 'Unknown')
    
    summary = f"{name} | Time: {cook_time} | Difficulty: {difficulty} | Serves: {servings}"
    
    if match_percentage is not None:
        summary = f"Match: {match_percentage:.0f}% | " + summary
    
    return summary

def print_separator(char='-', length=50):
    """Print a separator line"""
    print(char * length)

def print_header(text: str, char='='):
    """Print a formatted header"""
    print(f"\n{char * len(text)}")
    print(text.upper())
    print(char * len(text))

def get_yes_no_input(prompt: str) -> bool:
    """
    Get a yes/no response from user
    Returns True for yes, False for no
    """
    while True:
        response = input(f"{prompt} (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no")

def truncate_text(text: str, max_length: int) -> str:
    """Truncate text to maximum length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."