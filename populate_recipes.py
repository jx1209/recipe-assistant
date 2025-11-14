#!/usr/bin/env python3
"""
Script to populate the database with sample recipes
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.database import get_db
from src.config.settings import get_settings
import json

settings = get_settings()

# Sample recipes
sample_recipes = [
    {
        "title": "Classic Spaghetti Carbonara",
        "description": "An authentic Italian pasta dish with eggs, cheese, pancetta, and black pepper",
        "ingredients": [
            {"name": "spaghetti", "amount": 400, "unit": "g"},
            {"name": "pancetta", "amount": 200, "unit": "g"},
            {"name": "eggs", "amount": 4, "unit": "whole"},
            {"name": "parmesan cheese", "amount": 100, "unit": "g"},
            {"name": "black pepper", "amount": 1, "unit": "tsp"}
        ],
        "instructions": [
            "Cook spaghetti in salted boiling water until al dente",
            "Dice pancetta and fry until crispy",
            "Beat eggs with grated parmesan and pepper",
            "Drain pasta, reserving some pasta water",
            "Mix hot pasta with pancetta, then add egg mixture off heat",
            "Toss quickly, adding pasta water if needed",
            "Serve immediately with extra parmesan"
        ],
        "prep_time": 10,
        "cook_time": 20,
        "servings": 4,
        "difficulty": "Medium",
        "cuisine": "italian",
        "meal_type": "dinner",
        "tags": ["pasta", "italian", "quick", "comfort-food"]
    },
    {
        "title": "Chicken Stir-Fry",
        "description": "Quick and healthy chicken stir-fry with vegetables",
        "ingredients": [
            {"name": "chicken breast", "amount": 500, "unit": "g"},
            {"name": "bell peppers", "amount": 2, "unit": "whole"},
            {"name": "broccoli", "amount": 1, "unit": "cup"},
            {"name": "soy sauce", "amount": 3, "unit": "tbsp"},
            {"name": "garlic", "amount": 3, "unit": "cloves"},
            {"name": "ginger", "amount": 1, "unit": "tbsp"},
            {"name": "vegetable oil", "amount": 2, "unit": "tbsp"}
        ],
        "instructions": [
            "Cut chicken into bite-sized pieces",
            "Chop vegetables into uniform sizes",
            "Heat oil in wok or large pan over high heat",
            "Stir-fry chicken until cooked through, remove",
            "Stir-fry vegetables until tender-crisp",
            "Return chicken to pan",
            "Add soy sauce, garlic, and ginger",
            "Toss everything together and serve over rice"
        ],
        "prep_time": 15,
        "cook_time": 10,
        "servings": 4,
        "difficulty": "Easy",
        "cuisine": "asian",
        "meal_type": "dinner",
        "tags": ["quick", "healthy", "asian", "chicken"]
    },
    {
        "title": "Avocado Toast",
        "description": "Simple and delicious avocado toast with a twist",
        "ingredients": [
            {"name": "bread", "amount": 2, "unit": "slices"},
            {"name": "avocado", "amount": 1, "unit": "whole"},
            {"name": "lemon juice", "amount": 1, "unit": "tsp"},
            {"name": "cherry tomatoes", "amount": 6, "unit": "whole"},
            {"name": "red pepper flakes", "amount": 0.5, "unit": "tsp"},
            {"name": "olive oil", "amount": 1, "unit": "tbsp"}
        ],
        "instructions": [
            "Toast bread until golden brown",
            "Mash avocado with lemon juice, salt, and pepper",
            "Spread avocado mixture on toast",
            "Top with halved cherry tomatoes",
            "Drizzle with olive oil",
            "Sprinkle with red pepper flakes",
            "Serve immediately"
        ],
        "prep_time": 5,
        "cook_time": 5,
        "servings": 1,
        "difficulty": "Easy",
        "cuisine": "american",
        "meal_type": "breakfast",
        "tags": ["quick", "vegetarian", "healthy", "breakfast"]
    },
    {
        "title": "Chocolate Chip Cookies",
        "description": "Classic homemade chocolate chip cookies that are crispy on the outside and chewy inside",
        "ingredients": [
            {"name": "all-purpose flour", "amount": 2.25, "unit": "cups"},
            {"name": "butter", "amount": 1, "unit": "cup"},
            {"name": "granulated sugar", "amount": 0.75, "unit": "cup"},
            {"name": "brown sugar", "amount": 0.75, "unit": "cup"},
            {"name": "eggs", "amount": 2, "unit": "whole"},
            {"name": "vanilla extract", "amount": 2, "unit": "tsp"},
            {"name": "baking soda", "amount": 1, "unit": "tsp"},
            {"name": "chocolate chips", "amount": 2, "unit": "cups"}
        ],
        "instructions": [
            "Preheat oven to 375°F (190°C)",
            "Cream together butter and both sugars until fluffy",
            "Beat in eggs and vanilla",
            "Mix flour, baking soda, and salt in separate bowl",
            "Gradually blend dry ingredients into butter mixture",
            "Stir in chocolate chips",
            "Drop rounded tablespoons onto ungreased cookie sheets",
            "Bake for 9-11 minutes until golden brown",
            "Cool on baking sheet for 2 minutes before transferring"
        ],
        "prep_time": 15,
        "cook_time": 11,
        "servings": 48,
        "difficulty": "Easy",
        "cuisine": "american",
        "meal_type": "dessert",
        "tags": ["dessert", "baking", "cookies", "sweet"]
    },
    {
        "title": "Greek Salad",
        "description": "Fresh and vibrant Mediterranean salad",
        "ingredients": [
            {"name": "cucumber", "amount": 1, "unit": "whole"},
            {"name": "tomatoes", "amount": 3, "unit": "whole"},
            {"name": "red onion", "amount": 0.5, "unit": "whole"},
            {"name": "feta cheese", "amount": 200, "unit": "g"},
            {"name": "kalamata olives", "amount": 0.5, "unit": "cup"},
            {"name": "olive oil", "amount": 3, "unit": "tbsp"},
            {"name": "lemon juice", "amount": 2, "unit": "tbsp"},
            {"name": "oregano", "amount": 1, "unit": "tsp"}
        ],
        "instructions": [
            "Chop cucumber, tomatoes into chunks",
            "Slice red onion thinly",
            "Cube feta cheese",
            "Combine vegetables in large bowl",
            "Add feta and olives",
            "Whisk together olive oil, lemon juice, and oregano",
            "Pour dressing over salad and toss gently",
            "Season with salt and pepper",
            "Serve immediately or chill"
        ],
        "prep_time": 15,
        "cook_time": 0,
        "servings": 4,
        "difficulty": "Easy",
        "cuisine": "mediterranean",
        "meal_type": "lunch",
        "tags": ["salad", "vegetarian", "healthy", "mediterranean", "quick"]
    },
    {
        "title": "Beef Tacos",
        "description": "Flavorful beef tacos with fresh toppings",
        "ingredients": [
            {"name": "ground beef", "amount": 500, "unit": "g"},
            {"name": "taco seasoning", "amount": 2, "unit": "tbsp"},
            {"name": "taco shells", "amount": 8, "unit": "whole"},
            {"name": "lettuce", "amount": 1, "unit": "cup"},
            {"name": "tomatoes", "amount": 2, "unit": "whole"},
            {"name": "cheddar cheese", "amount": 1, "unit": "cup"},
            {"name": "sour cream", "amount": 0.5, "unit": "cup"},
            {"name": "salsa", "amount": 0.5, "unit": "cup"}
        ],
        "instructions": [
            "Brown ground beef in large skillet over medium heat",
            "Drain excess fat",
            "Add taco seasoning and water according to package",
            "Simmer for 5 minutes",
            "Warm taco shells in oven",
            "Shred lettuce and dice tomatoes",
            "Fill shells with seasoned beef",
            "Top with lettuce, tomatoes, cheese, sour cream, and salsa",
            "Serve immediately"
        ],
        "prep_time": 10,
        "cook_time": 15,
        "servings": 4,
        "difficulty": "Easy",
        "cuisine": "mexican",
        "meal_type": "dinner",
        "tags": ["mexican", "quick", "comfort-food", "beef"]
    }
]

def main():
    """Populate database with sample recipes"""
    db = get_db(settings.DATABASE_URL)
    cursor = db.conn.cursor()
    
    # Check if we already have recipes
    cursor.execute("SELECT COUNT(*) as count FROM recipes WHERE is_deleted = 0")
    count = cursor.fetchone()['count']
    
    if count > 0:
        print(f"Database already has {count} recipes. Skipping population.")
        return
    
    print("Adding sample recipes to database...")
    
    # Get or create a default user (user_id = 1)
    cursor.execute("SELECT id FROM users LIMIT 1")
    user_row = cursor.fetchone()
    
    if not user_row:
        # Create a demo user
        cursor.execute("""
            INSERT INTO users (email, password_hash, full_name)
            VALUES (?, ?, ?)
        """, ('demo@example.com', 'demo_hash', 'Demo User'))
        db.conn.commit()
        user_id = cursor.lastrowid
        print(f"Created demo user (ID: {user_id})")
    else:
        user_id = user_row['id']
        print(f"Using existing user (ID: {user_id})")
    
    # Insert recipes
    for recipe in sample_recipes:
        cursor.execute("""
            INSERT INTO recipes (
                created_by, title, description, ingredients_json, instructions_json,
                prep_time_minutes, cook_time_minutes, servings, difficulty, cuisine
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            recipe['title'],
            recipe['description'],
            json.dumps(recipe['ingredients']),
            json.dumps(recipe['instructions']),
            recipe['prep_time'],
            recipe['cook_time'],
            recipe['servings'],
            recipe['difficulty'],
            recipe['cuisine']
        ))
        print(f"  ✓ Added: {recipe['title']}")
    
    db.conn.commit()
    
    # Verify
    cursor.execute("SELECT COUNT(*) as count FROM recipes WHERE is_deleted = 0")
    final_count = cursor.fetchone()['count']
    print(f"\n✓ Successfully added {final_count} recipes to database!")
    
    # Show some stats
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(DISTINCT cuisine) as cuisines
        FROM recipes WHERE is_deleted = 0
    """)
    stats = cursor.fetchone()
    print(f"  - Total recipes: {stats['total']}")
    print(f"  - Cuisines: {stats['cuisines']}")

if __name__ == "__main__":
    main()

