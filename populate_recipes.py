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

# Stock food photos (Unsplash — allowed for display; see next.config.js remotePatterns)
_IMG = "https://images.unsplash.com"

# Sample recipes
sample_recipes = [
    {
        "title": "Classic Spaghetti Carbonara",
        "image_url": f"{_IMG}/photo-1621996346565-e3dbc646d9a9?auto=format&fit=crop&w=1200&q=80",
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
        "image_url": f"{_IMG}/photo-1603133872878-684f208fb84b?auto=format&fit=crop&w=1200&q=80",
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
        "image_url": f"{_IMG}/photo-1541519220094-4f3f0c26a2d4?auto=format&fit=crop&w=1200&q=80",
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
        "image_url": f"{_IMG}/photo-1558961363-fa8fdf82db35?auto=format&fit=crop&w=1200&q=80",
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
        "image_url": f"{_IMG}/photo-1540189549336-e6e99c3679fe?auto=format&fit=crop&w=1200&q=80",
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
        "title": "Birria Tacos (From Scratch)",
        "source_url": "https://tastesbetterfromscratch.com/birria-tacos/",
        "source_name": "Tastes Better From Scratch",
        "image_url": (
            "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Birria_tacos.jpg/"
            "1280px-Birria_tacos.jpg"
        ),
        "description": "Shredded beef and melty cheese in crispy, sauce-dipped quesabirria tacos with consommé for dipping. "
        "Corn tortillas are store-bought—no homemade tortillas. Based on the recipe by Lauren Allen at Tastes Better From Scratch. "
        "Hero photo: birria tacos (Teddy's Red Tacos, Venice, CA) — T.Tseng, CC BY 2.0 via Wikimedia Commons.",
        "ingredients": [
            {"name": "beef chuck roast (fat trimmed)", "quantity": 3, "unit": "lb"},
            {"name": "bone-in beef short ribs", "quantity": 4, "unit": "whole"},
            {"name": "dried guajillo chiles", "quantity": 8, "unit": "whole"},
            {"name": "dried pasilla chiles", "quantity": 3, "unit": "whole"},
            {"name": "dried arbol chiles (adjust for heat)", "quantity": 2, "unit": "whole"},
            {"name": "Roma tomatoes, quartered", "quantity": 5, "unit": "whole"},
            {"name": "white onion, roughly chopped", "quantity": 1, "unit": "large"},
            {"name": "garlic cloves (about 1 head)", "quantity": 12, "unit": "cloves"},
            {"name": "whole black peppercorns", "quantity": 1, "unit": "tbsp"},
            {"name": "whole cumin seeds", "quantity": 1, "unit": "tbsp"},
            {"name": "dried Mexican oregano", "quantity": 1, "unit": "tbsp"},
            {"name": "dried thyme", "quantity": 1, "unit": "tbsp"},
            {"name": "whole coriander seed", "quantity": 0.5, "unit": "tsp"},
            {"name": "whole cloves", "quantity": 4, "unit": "whole"},
            {"name": "fresh ginger, minced", "quantity": 1, "unit": "tsp"},
            {"name": "Mexican cinnamon stick (or pinch ground cinnamon)", "quantity": 1, "unit": "inch piece"},
            {"name": "apple cider vinegar", "quantity": 2, "unit": "tbsp"},
            {"name": "bay leaves", "quantity": 3, "unit": "whole"},
            {"name": "kosher salt (for sauce)", "quantity": 1, "unit": "tbsp"},
            {"name": "water (for simmering and rinsing blender)", "quantity": 8, "unit": "cups"},
            {"name": "store-bought corn tortillas (white or yellow)", "quantity": 15, "unit": "whole"},
            {"name": "shredded Oaxaca cheese (or mozzarella / Monterey Jack)", "quantity": 2.5, "unit": "cups"},
            {"name": "white onion, diced (for tacos)", "quantity": 0.5, "unit": "whole"},
            {"name": "fresh cilantro, chopped", "quantity": 1, "unit": "bunch"},
            {"name": "limes, cut into wedges", "quantity": 2, "unit": "whole"},
        ],
        "instructions": [
            "Trim excess fat from the chuck roast and cut into a few large pieces; season lightly with salt.",
            "Rinse dried chiles. Wearing gloves, cut open and remove stems and seeds. For extra heat, leave arbol chiles whole; for milder tacos, seed them or remove some arbol.",
            "Birria base: In a large stockpot (at least 5.5 qt), cook tomatoes and chopped onion over medium heat for a few minutes, stirring. Add whole garlic cloves, all prepared chiles, and the dry spices (peppercorns, cumin, oregano, thyme, coriander, cloves, ginger, cinnamon) except the bay leaves. Cook about 5 minutes, stirring often.",
            "Add vinegar and 4 cups water. Bring to a low boil, reduce heat, and simmer uncovered for 15 minutes.",
            "Blend the mixture until as smooth as possible. Pour through a fine-mesh strainer back into the pot. Add 4 cups water to the blender, swirl to rinse remaining sauce from the sides, and pour into the pot (this rinses the blender into the broth).",
            "Stir in 1 tablespoon kosher salt. Bring to a boil. Add short ribs, chuck pieces, and bay leaves. Cover, reduce to a simmer, and cook about 2½ hours until the beef is tender.",
            "Remove meat to a plate. Shred beef; discard bones and soft bay leaves. Keep the consommé warm for dipping.",
            "Assemble tacos: Heat a large griddle or skillet over medium heat with a thin film of oil. Dip a corn tortilla in the birria sauce, lay it on the hot surface, then quickly add shredded meat, cheese, diced onion, and cilantro. Fold the tortilla in half and cook until crispy and browned on both sides.",
            "Serve quesabirria tacos with extra onion and cilantro, lime wedges, and small cups of warm consommé for dipping.",
        ],
        "prep_time": 20,
        "cook_time": 170,
        "servings": 16,
        "difficulty": "Hard",
        "cuisine": "mexican",
        "meal_type": "dinner",
        "tags": ["mexican", "birria", "beef", "slow-cooked", "weekend-project"],
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
        total_time = recipe['prep_time'] + recipe['cook_time']
        cursor.execute("""
            INSERT INTO recipes (
                created_by, title, description, source_url, source_name,
                ingredients_json, instructions_json,
                image_url, prep_time_minutes, cook_time_minutes, total_time_minutes,
                servings, difficulty, cuisine
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            recipe['title'],
            recipe['description'],
            recipe.get('source_url'),
            recipe.get('source_name'),
            json.dumps(recipe['ingredients']),
            json.dumps(recipe['instructions']),
            recipe.get('image_url'),
            recipe['prep_time'],
            recipe['cook_time'],
            total_time,
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

