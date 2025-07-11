"""
Recipe Database Module
Handles all recipe data and database operations
"""

import json
import os
import sqlite3
import logging
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
from contextlib import contextmanager
import shutil
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Recipe:
    """Recipe data model with type hints and validation"""
    name: str
    ingredients: List[str]
    instructions: List[str]
    cook_time: str
    difficulty: str
    servings: int
    cuisine: str = ""
    tags: List[str] = None
    nutrition: Dict[str, Any] = None
    image: str = ""
    created_at: str = ""
    updated_at: str = ""
    created_by: str = "system"
    rating: float = 0.0
    review_count: int = 0
    prep_time: str = ""
    total_time: str = ""
    description: str = ""
    source: str = ""
    dietary_restrictions: List[str] = None
    equipment: List[str] = None
    cost_estimate: str = ""
    
    def __post_init__(self):
        """Initialize default values and validate data"""
        if self.tags is None:
            self.tags = []
        if self.nutrition is None:
            self.nutrition = {}
        if self.dietary_restrictions is None:
            self.dietary_restrictions = []
        if self.equipment is None:
            self.equipment = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
        

        self._validate()
    
    def _validate(self):
        """Validate recipe data"""
        errors = []
        
        if not self.name or len(self.name.strip()) < 2:
            errors.append("Recipe name must be at least 2 characters")
        
        if not self.ingredients or len(self.ingredients) == 0:
            errors.append("Recipe must have at least one ingredient")
        
        if not self.instructions or len(self.instructions) == 0:
            errors.append("Recipe must have at least one instruction")
        
        if self.servings <= 0:
            errors.append("Servings must be greater than 0")
        
        valid_difficulties = ['Easy', 'Medium', 'Hard']
        if self.difficulty not in valid_difficulties:
            errors.append(f"Difficulty must be one of: {', '.join(valid_difficulties)}")
        
        if self.rating < 0 or self.rating > 5:
            errors.append("Rating must be between 0 and 5")
        
        if errors:
            raise ValueError(f"Recipe validation failed: {'; '.join(errors)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert recipe to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Recipe':
        """Create recipe from dictionary"""
        return cls(**data)
    
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.now().isoformat()

class DatabaseCache:
    """Simple in-memory cache for frequently accessed data"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache = {}
        self._timestamps = {}
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        with self._lock:
            if key not in self._cache:
                return None

            if time.time() - self._timestamps[key] > self.ttl_seconds:
                del self._cache[key]
                del self._timestamps[key]
                return None
            
            return self._cache[key]
    
    def set(self, key: str, value: Any):
        """Set item in cache"""
        with self._lock:

            if len(self._cache) >= self.max_size:
                oldest_key = min(self._timestamps.keys(), key=lambda k: self._timestamps[k])
                del self._cache[oldest_key]
                del self._timestamps[oldest_key]
            
            self._cache[key] = value
            self._timestamps[key] = time.time()
    
    def clear(self):
        """Clear all cache"""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
    
    def invalidate(self, pattern: str = None):
        """Invalidate cache entries matching pattern"""
        with self._lock:
            if pattern is None:
                self.clear()
                return
            
            keys_to_remove = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self._cache[key]
                del self._timestamps[key]

 ########################Note: update to adv recipe database
class AdvancedRecipeDatabase:
    def __init__(self, 
                 data_file: Optional[str] = None,
                 db_file: Optional[str] = None,
                 enable_cache: bool = True,
                 backup_enabled: bool = True):

        """Initialize the recipe database"""
        if data_file is None:
            current_dir = Path(__file__).parent
            project_root = current_dir.parent
            data_dir = project_root / 'data'
            data_dir.mkdir(exist_ok=True)
            data_file = str(data_dir / 'recipes.json')
        
        if db_file is None:
            db_file = str(Path(data_file).parent / 'recipes.db')
        
        self.data_file = data_file
        self.db_file = db_file
        self.backup_enabled = backup_enabled
        
        # Initialize cache
        self.cache = DatabaseCache() if enable_cache else None
        
        # Database lock for thread safety
        self._db_lock = threading.RLock()
        
        # Initialize databases
        self._init_sqlite_db()
        self._load_or_migrate_data()
        
        # Performance metrics
        self.query_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
        
        logger.info(f"Advanced Recipe Database initialized")
        logger.info(f"JSON file: {self.data_file}")
        logger.info(f"SQLite file: {self.db_file}")
###############################################
        #self.data_file = data_file
        #self.recipes = self.load_recipes()
    
    def load_recipes(self):
        """Load recipes from JSON file or return default recipes"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as file:
                    return json.load(file)
            else:
                print(f"Creating data file at {self.data_file}")
                default_recipes = self.get_default_recipes()

            try:
                os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
                with open(self.data_file, 'w', encoding='utf-8') as file:
                    json.dump(self.recipes, file, indent=2, ensure_ascii=False)
                return default_recipes
            
            except PermissionError:
                print("Warning: Cannot create data file due to permissions. Using in-memory recipes.")
                return default_recipes
        
        except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
            print(f"Warning: Could not load recipes from {self.data_file}: {e}")
            print("Using default recipes in memory.")
            return self.get_default_recipes()
    
    def get_default_recipes(self):
        """Return the default recipe database"""
        return {
            "pasta_marinara": {
                "name": "Pasta Marinara",
                "ingredients": ["pasta", "tomatoes", "garlic", "olive oil", "basil"],
                "instructions": [
                    "Boil water and cook pasta according to package directions",
                    "Heat olive oil in pan, add minced garlic",
                    "Add crushed tomatoes and simmer 10 minutes", 
                    "Add cooked pasta and fresh basil",
                    "Serve hot"
                ],
                "cook_time": "20 minutes",
                "difficulty": "Easy",
                "servings": 4,
                "cuisine": "Italian",
                "tags": ["vegetarian", "quick", "dinner"]
            },
            "scrambled_eggs": {
                "name": "Scrambled Eggs",
                "ingredients": ["eggs", "butter", "salt", "pepper"],
                "instructions": [
                    "Crack eggs into bowl and whisk",
                    "Heat butter in non-stick pan over low heat",
                    "Add eggs and gently stir continuously",
                    "Season with salt and pepper",
                    "Remove from heat when just set"
                ],
                "cook_time": "5 minutes", 
                "difficulty": "Easy",
                "servings": 2,
                "cuisine": "American",
                "tags": ["breakfast", "quick", "vegetarian"]
            },
            "chicken_stir_fry": {
                "name": "Chicken Stir Fry",
                "ingredients": ["chicken", "vegetables", "soy sauce", "garlic", "ginger", "oil"],
                "instructions": [
                    "Cut chicken into small pieces",
                    "Heat oil in wok or large pan",
                    "Cook chicken until golden",
                    "Add vegetables and stir fry 3-4 minutes",
                    "Add soy sauce, garlic, and ginger",
                    "Serve over rice"
                ],
                "cook_time": "15 minutes",
                "difficulty": "Medium",
                "servings": 3,
                "cuisine": "Asian",
                "tags": ["dinner", "healthy", "quick"]
            },
            "grilled_cheese": {
                "name": "Grilled Cheese Sandwich",
                "ingredients": ["bread", "cheese", "butter"],
                "instructions": [
                    "Butter one side of each bread slice",
                    "Place cheese between bread (butter sides out)",
                    "Heat pan over medium heat",
                    "Cook sandwich 2-3 minutes per side until golden",
                    "Cut diagonally and serve"
                ],
                "cook_time": "8 minutes",
                "difficulty": "Easy",
                "servings": 1,
                "cuisine": "American",
                "tags": ["lunch", "quick", "vegetarian"]
            },
            "vegetable_soup": {
                "name": "Vegetable Soup",
                "ingredients": ["vegetables", "broth", "onion", "garlic", "herbs", "salt", "pepper"],
                "instructions": [
                    "Dice onion and garlic",
                    "Saute onion and garlic in pot until soft",
                    "Add chopped vegetables and broth",
                    "Simmer for 20-25 minutes until vegetables are tender",
                    "Season with herbs, salt, and pepper",
                    "Serve hot"
                ],
                "cook_time": "30 minutes",
                "difficulty": "Easy",
                "servings": 4,
                "cuisine": "International",
                "tags": ["soup", "healthy", "vegetarian", "dinner"]
            },
            "pancakes": {
                "name": "Classic Pancakes",
                "ingredients": ["flour", "milk", "eggs", "sugar", "baking powder", "salt", "butter"],
                "instructions": [
                    "Mix dry ingredients in large bowl",
                    "Whisk milk, eggs, and melted butter in separate bowl",
                    "Combine wet and dry ingredients until just mixed",
                    "Heat griddle or pan over medium heat",
                    "Pour batter and cook until bubbles form",
                    "Flip and cook until golden brown"
                ],
                "cook_time": "15 minutes",
                "difficulty": "Easy",
                "servings": 4,
                "cuisine": "American",
                "tags": ["breakfast", "sweet", "vegetarian"]
            }
        }
    
    def get_all_recipes(self):
        """Return all recipes"""
        return self.recipes
    
    def get_recipe(self, recipe_id):
        """Get a specific recipe by ID"""
        return self.recipes.get(recipe_id)
    
    def add_recipe(self, recipe_id, recipe_data):
        """Add a new recipe to the database"""
        self.recipes[recipe_id] = recipe_data
        return self.save_recipes()
    
    def update_recipe(self, recipe_id, recipe_data):
        """Update an existing recipe"""
        if recipe_id in self.recipes:
            self.recipes[recipe_id] = recipe_data
            return self.save_recipes()
        return False
    
    def delete_recipe(self, recipe_id):
        """Delete a recipe from the database"""
        if recipe_id in self.recipes:
            del self.recipes[recipe_id]
            return self.save_recipes()
        return False
    
    def search_recipes_by_tag(self, tag):
        """Find recipes that have a specific tag"""
        matching_recipes = {}
        for recipe_id, recipe in self.recipes.items():
            if 'tags' in recipe and tag.lower() in [t.lower() for t in recipe['tags']]:
                matching_recipes[recipe_id] = recipe
        return matching_recipes
    
    def search_recipes_by_cuisine(self, cuisine):
        """Find recipes from a specific cuisine"""
        matching_recipes = {}
        for recipe_id, recipe in self.recipes.items():
            if 'cuisine' in recipe and cuisine.lower() in recipe['cuisine'].lower():
                matching_recipes[recipe_id] = recipe
        return matching_recipes
    
