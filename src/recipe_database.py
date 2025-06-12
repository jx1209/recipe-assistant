"""
Recipe Database Module
Handles all recipe data and database operations
"""

import json
import os

class RecipeDatabase:
    def __init__(self, data_file=None):
        """Initialize the recipe database"""
        if data_file is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            data_file = os.path.join(project_root, 'data', 'recipes.json')
        
        self.data_file = data_file
        self.recipes = self.load_recipes()
    
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