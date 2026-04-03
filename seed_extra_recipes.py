#!/usr/bin/env python3
"""
Append additional demo recipes to an existing database (skips titles that already exist).

Run from project root:
  ./venv/bin/python seed_extra_recipes.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config.settings import get_settings
from src.database import get_db

settings = get_settings()
_IMG = "https://images.unsplash.com"

# Verified Unsplash URLs (images.unsplash.com in next.config.js)
EXTRA_RECIPES = [
    {
        "title": "Thai Green Curry with Vegetables",
        "description": "Aromatic coconut curry with bell pepper, Thai basil, and jasmine rice.",
        "image_url": f"{_IMG}/photo-1563379926898-05f4575a45d8?auto=format&fit=crop&w=1200&q=80",
        "ingredients": [
            {"name": "coconut milk", "quantity": 2, "unit": "cans"},
            {"name": "green curry paste", "quantity": 3, "unit": "tbsp"},
            {"name": "chicken thighs, cubed", "quantity": 600, "unit": "g"},
            {"name": "bell peppers", "quantity": 2, "unit": "whole"},
            {"name": "Thai basil", "quantity": 1, "unit": "cup"},
            {"name": "fish sauce", "quantity": 2, "unit": "tbsp"},
            {"name": "brown sugar", "quantity": 1, "unit": "tbsp"},
            {"name": "jasmine rice, cooked", "quantity": 4, "unit": "cups"},
        ],
        "instructions": [
            "Simmer coconut milk in a large pan until it splits slightly, then fry curry paste 2 minutes.",
            "Add chicken; cook until no longer pink on the outside.",
            "Pour in remaining coconut milk, fish sauce, and sugar; simmer 12 minutes.",
            "Add peppers; cook until tender. Stir in basil off heat.",
            "Serve over jasmine rice.",
        ],
        "prep_time": 15,
        "cook_time": 25,
        "servings": 4,
        "difficulty": "Medium",
        "cuisine": "thai",
        "meal_type": "dinner",
        "tags": ["asian", "coconut", "spicy", "chicken", "dinner", "gluten-free"],
    },
    {
        "title": "French Onion Soup",
        "description": "Caramelized onions in rich beef broth with a gratinéed cheese crouton.",
        "image_url": f"{_IMG}/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=1200&q=80",
        "ingredients": [
            {"name": "yellow onions, sliced", "quantity": 6, "unit": "large"},
            {"name": "butter", "quantity": 4, "unit": "tbsp"},
            {"name": "beef stock", "quantity": 8, "unit": "cups"},
            {"name": "dry white wine", "quantity": 0.5, "unit": "cup"},
            {"name": "baguette slices", "quantity": 8, "unit": "slices"},
            {"name": "Gruyère cheese, grated", "quantity": 2, "unit": "cups"},
            {"name": "thyme sprigs", "quantity": 4, "unit": "sprigs"},
            {"name": "bay leaf", "quantity": 1, "unit": "whole"},
        ],
        "instructions": [
            "Cook onions in butter over low heat 40–50 minutes until deep golden, stirring often.",
            "Add wine; reduce. Add stock, thyme, bay; simmer 20 minutes. Season.",
            "Toast baguette. Ladle soup into oven-safe bowls, top with bread and cheese.",
            "Broil until bubbly and browned.",
        ],
        "prep_time": 20,
        "cook_time": 75,
        "servings": 6,
        "difficulty": "Medium",
        "cuisine": "french",
        "meal_type": "lunch",
        "tags": ["soup", "comfort food", "slow-cooked", "lunch", "dinner"],
    },
    {
        "title": "Shakshuka",
        "description": "Eggs poached in spiced tomato–pepper sauce—perfect for brunch.",
        "image_url": f"{_IMG}/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=1200&q=80",
        "ingredients": [
            {"name": "olive oil", "quantity": 3, "unit": "tbsp"},
            {"name": "onion, diced", "quantity": 1, "unit": "whole"},
            {"name": "red bell pepper, diced", "quantity": 1, "unit": "whole"},
            {"name": "garlic, minced", "quantity": 3, "unit": "cloves"},
            {"name": "canned crushed tomatoes", "quantity": 28, "unit": "oz"},
            {"name": "paprika", "quantity": 1, "unit": "tsp"},
            {"name": "cumin", "quantity": 0.5, "unit": "tsp"},
            {"name": "eggs", "quantity": 6, "unit": "whole"},
            {"name": "feta, crumbled", "quantity": 0.5, "unit": "cup"},
            {"name": "fresh parsley", "quantity": 0.25, "unit": "cup"},
        ],
        "instructions": [
            "Sauté onion and pepper in oil until soft. Add garlic 1 minute.",
            "Stir in tomatoes and spices; simmer 10 minutes until thick.",
            "Make wells; crack in eggs. Cover and cook until whites set.",
            "Top with feta and parsley. Serve with crusty bread.",
        ],
        "prep_time": 10,
        "cook_time": 25,
        "servings": 4,
        "difficulty": "Easy",
        "cuisine": "mediterranean",
        "meal_type": "breakfast",
        "tags": ["vegetarian", "eggs", "healthy", "brunch", "quick", "gluten-free"],
    },
    {
        "title": "Margherita Pizza",
        "description": "Thin crust with San Marzano tomatoes, fresh mozzarella, and basil.",
        "image_url": f"{_IMG}/photo-1574071318508-1cdbab80d002?auto=format&fit=crop&w=1200&q=80",
        "ingredients": [
            {"name": "pizza dough ball", "quantity": 1, "unit": "lb"},
            {"name": "San Marzano tomatoes, crushed", "quantity": 1, "unit": "cup"},
            {"name": "fresh mozzarella, sliced", "quantity": 8, "unit": "oz"},
            {"name": "fresh basil leaves", "quantity": 12, "unit": "leaves"},
            {"name": "olive oil", "quantity": 2, "unit": "tbsp"},
            {"name": "garlic, minced", "quantity": 1, "unit": "clove"},
            {"name": "salt", "quantity": 1, "unit": "tsp"},
        ],
        "instructions": [
            "Preheat oven to 260°C (500°F) with a stone if you have one.",
            "Stretch dough. Mix tomatoes with garlic, salt, and oil; spread on dough.",
            "Top with mozzarella. Bake 8–10 minutes until blistered.",
            "Finish with fresh basil and a drizzle of oil.",
        ],
        "prep_time": 20,
        "cook_time": 12,
        "servings": 3,
        "difficulty": "Medium",
        "cuisine": "italian",
        "meal_type": "dinner",
        "tags": ["pizza", "vegetarian", "italian", "comfort food", "dinner"],
    },
    {
        "title": "Chickpea Buddha Bowl",
        "description": "Roasted chickpeas, grains, greens, and tahini lemon dressing.",
        "image_url": f"{_IMG}/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=1200&q=80",
        "ingredients": [
            {"name": "chickpeas, drained", "quantity": 2, "unit": "cans"},
            {"name": "olive oil", "quantity": 3, "unit": "tbsp"},
            {"name": "cumin", "quantity": 1, "unit": "tsp"},
            {"name": "cooked quinoa", "quantity": 2, "unit": "cups"},
            {"name": "mixed greens", "quantity": 4, "unit": "cups"},
            {"name": "cucumber, diced", "quantity": 1, "unit": "whole"},
            {"name": "tahini", "quantity": 3, "unit": "tbsp"},
            {"name": "lemon juice", "quantity": 2, "unit": "tbsp"},
            {"name": "maple syrup", "quantity": 1, "unit": "tsp"},
        ],
        "instructions": [
            "Toss chickpeas with oil and cumin; roast at 200°C (400°F) 25 minutes until crisp.",
            "Whisk tahini, lemon, syrup, and water for dressing.",
            "Divide quinoa, greens, cucumber, and chickpeas in bowls.",
            "Drizzle dressing and serve.",
        ],
        "prep_time": 15,
        "cook_time": 30,
        "servings": 4,
        "difficulty": "Easy",
        "cuisine": "american",
        "meal_type": "lunch",
        "tags": ["vegan", "healthy", "bowl", "meal-prep", "gluten-free", "lunch"],
    },
    {
        "title": "Beef Teriyaki Bowl",
        "description": "Thin-sliced beef glazed with homemade teriyaki over steamed rice.",
        "image_url": f"{_IMG}/photo-1603133872878-684f208fb84b?auto=format&fit=crop&w=1200&q=80",
        "ingredients": [
            {"name": "sirloin, thinly sliced", "quantity": 500, "unit": "g"},
            {"name": "soy sauce", "quantity": 0.25, "unit": "cup"},
            {"name": "mirin", "quantity": 3, "unit": "tbsp"},
            {"name": "brown sugar", "quantity": 2, "unit": "tbsp"},
            {"name": "ginger, grated", "quantity": 1, "unit": "tbsp"},
            {"name": "garlic, minced", "quantity": 2, "unit": "cloves"},
            {"name": "sesame oil", "quantity": 1, "unit": "tsp"},
            {"name": "steamed rice", "quantity": 4, "unit": "cups"},
            {"name": "green onions", "quantity": 4, "unit": "stalks"},
        ],
        "instructions": [
            "Whisk soy, mirin, sugar, ginger, and garlic for sauce.",
            "Sear beef in batches; return all to pan, add sauce, simmer until glossy.",
            "Finish with sesame oil and scallions. Serve over rice.",
        ],
        "prep_time": 15,
        "cook_time": 15,
        "servings": 4,
        "difficulty": "Easy",
        "cuisine": "asian",
        "meal_type": "dinner",
        "tags": ["beef", "asian", "quick", "rice", "dinner"],
    },
    {
        "title": "Mushroom Risotto",
        "description": "Creamy arborio rice with wild mushrooms and parmesan.",
        "image_url": f"{_IMG}/photo-1621996346565-e3dbc646d9a9?auto=format&fit=crop&w=1200&q=80",
        "ingredients": [
            {"name": "arborio rice", "quantity": 1.5, "unit": "cups"},
            {"name": "mixed mushrooms, sliced", "quantity": 400, "unit": "g"},
            {"name": "shallots, minced", "quantity": 2, "unit": "whole"},
            {"name": "dry white wine", "quantity": 0.5, "unit": "cup"},
            {"name": "vegetable stock, warm", "quantity": 6, "unit": "cups"},
            {"name": "butter", "quantity": 3, "unit": "tbsp"},
            {"name": "parmesan, grated", "quantity": 0.5, "unit": "cup"},
            {"name": "fresh thyme", "quantity": 1, "unit": "tbsp"},
        ],
        "instructions": [
            "Sauté mushrooms in butter until golden; set aside.",
            "Cook shallots, add rice, toast 2 minutes. Deglaze with wine.",
            "Add stock a ladle at a time, stirring until creamy, 18–22 minutes.",
            "Stir in mushrooms, parmesan, and thyme. Rest 2 minutes before serving.",
        ],
        "prep_time": 15,
        "cook_time": 35,
        "servings": 4,
        "difficulty": "Medium",
        "cuisine": "italian",
        "meal_type": "dinner",
        "tags": ["vegetarian", "comfort food", "rice", "mushroom", "dinner", "gluten-free"],
    },
    {
        "title": "Banana Protein Smoothie",
        "description": "Post-workout smoothie with peanut butter and oat milk.",
        "image_url": f"{_IMG}/photo-1599487488170-d11ec9c172f0?auto=format&fit=crop&w=1200&q=80",
        "ingredients": [
            {"name": "frozen banana", "quantity": 2, "unit": "whole"},
            {"name": "oat milk", "quantity": 1.5, "unit": "cups"},
            {"name": "peanut butter", "quantity": 2, "unit": "tbsp"},
            {"name": "vanilla protein powder", "quantity": 1, "unit": "scoop"},
            {"name": "chia seeds", "quantity": 1, "unit": "tbsp"},
            {"name": "ice", "quantity": 0.5, "unit": "cup"},
        ],
        "instructions": [
            "Add all ingredients to a high-speed blender.",
            "Blend until smooth, 45–60 seconds.",
            "Pour into glasses and serve immediately.",
        ],
        "prep_time": 5,
        "cook_time": 0,
        "servings": 2,
        "difficulty": "Easy",
        "cuisine": "american",
        "meal_type": "snack",
        "tags": ["quick", "healthy", "vegetarian", "breakfast", "snack", "gluten-free"],
    },
    {
        "title": "Fish Tacos with Cabbage Slaw",
        "description": "Crispy white fish, lime crema, and crunchy slaw in warm tortillas.",
        "image_url": f"{_IMG}/photo-1565299585323-38d6b0865b47?auto=format&fit=crop&w=1200&q=80",
        "ingredients": [
            {"name": "white fish fillets", "quantity": 600, "unit": "g"},
            {"name": "corn tortillas", "quantity": 12, "unit": "whole"},
            {"name": "cabbage, shredded", "quantity": 3, "unit": "cups"},
            {"name": "lime juice", "quantity": 3, "unit": "tbsp"},
            {"name": "mayonnaise", "quantity": 0.25, "unit": "cup"},
            {"name": "chili powder", "quantity": 1, "unit": "tsp"},
            {"name": "cilantro", "quantity": 0.5, "unit": "cup"},
            {"name": "vegetable oil", "quantity": 3, "unit": "tbsp"},
        ],
        "instructions": [
            "Season fish; pan-fry or bake until flaky.",
            "Toss cabbage with half the lime juice and a pinch of salt.",
            "Mix mayo, remaining lime, and chili for crema.",
            "Warm tortillas. Fill with fish, slaw, crema, and cilantro.",
        ],
        "prep_time": 20,
        "cook_time": 15,
        "servings": 4,
        "difficulty": "Easy",
        "cuisine": "mexican",
        "meal_type": "dinner",
        "tags": ["fish", "mexican", "quick", "dinner", "dairy-free"],
    },
    {
        "title": "Vegetable Pad Thai",
        "description": "Rice noodles in tamarind sauce with tofu, peanuts, and bean sprouts.",
        "image_url": f"{_IMG}/photo-1559314809-0d155014e29e?auto=format&fit=crop&w=1200&q=80",
        "ingredients": [
            {"name": "rice noodles, soaked", "quantity": 8, "unit": "oz"},
            {"name": "firm tofu, cubed", "quantity": 300, "unit": "g"},
            {"name": "eggs", "quantity": 2, "unit": "whole"},
            {"name": "bean sprouts", "quantity": 2, "unit": "cups"},
            {"name": "tamarind paste", "quantity": 2, "unit": "tbsp"},
            {"name": "fish sauce", "quantity": 3, "unit": "tbsp"},
            {"name": "palm sugar", "quantity": 2, "unit": "tbsp"},
            {"name": "peanuts, crushed", "quantity": 0.5, "unit": "cup"},
            {"name": "lime wedges", "quantity": 4, "unit": "whole"},
        ],
        "instructions": [
            "Stir-fry tofu until golden; push aside, scramble eggs.",
            "Add drained noodles, tamarind, fish sauce, and sugar.",
            "Toss with sprouts; top with peanuts and lime.",
        ],
        "prep_time": 25,
        "cook_time": 12,
        "servings": 4,
        "difficulty": "Medium",
        "cuisine": "thai",
        "meal_type": "dinner",
        "tags": ["noodles", "asian", "vegetarian", "peanuts", "dinner"],
    },
]


def _ingredients_json(recipe: dict) -> str:
    rows = []
    for ing in recipe["ingredients"]:
        rows.append(
            {
                "name": ing["name"],
                "quantity": ing["quantity"],
                "unit": ing.get("unit"),
            }
        )
    return json.dumps(rows)


def main() -> None:
    db = get_db(settings.DATABASE_URL)
    cur = db.conn.cursor()
    cur.execute("SELECT id FROM users LIMIT 1")
    row = cur.fetchone()
    if not row:
        print("No user found. Create a user first or run populate_recipes on empty DB.")
        sys.exit(1)
    user_id = row["id"]

    added = 0
    skipped = 0
    for recipe in EXTRA_RECIPES:
        cur.execute(
            "SELECT 1 FROM recipes WHERE LOWER(title) = LOWER(?) AND is_deleted = 0",
            (recipe["title"],),
        )
        if cur.fetchone():
            skipped += 1
            print(f"  skip (exists): {recipe['title']}")
            continue

        total_time = recipe["prep_time"] + recipe["cook_time"]
        cur.execute(
            """
            INSERT INTO recipes (
                created_by, title, description, source_url, source_name,
                ingredients_json, instructions_json,
                image_url, prep_time_minutes, cook_time_minutes, total_time_minutes,
                servings, difficulty, cuisine
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                recipe["title"],
                recipe["description"],
                recipe.get("source_url"),
                recipe.get("source_name"),
                _ingredients_json(recipe),
                json.dumps(recipe["instructions"]),
                recipe.get("image_url"),
                recipe["prep_time"],
                recipe["cook_time"],
                total_time,
                recipe["servings"],
                recipe["difficulty"],
                recipe["cuisine"],
            ),
        )
        rid = cur.lastrowid
        tag_set = set(t.lower().strip() for t in recipe.get("tags", []))
        mt = recipe.get("meal_type")
        if mt:
            tag_set.add(mt.lower())
        for tag in sorted(tag_set):
            try:
                cur.execute(
                    "INSERT INTO recipe_tags (recipe_id, tag_name) VALUES (?, ?)",
                    (rid, tag),
                )
            except Exception:
                pass
        added += 1
        print(f"  + {recipe['title']}")

    db.conn.commit()
    print(f"\nDone. Added {added} recipes, skipped {skipped} duplicates.")
    cur.execute("SELECT COUNT(*) AS c FROM recipes WHERE is_deleted = 0")
    total_row = cur.fetchone()
    print(f"Total recipes in database: {total_row['c'] if total_row else 0}")


if __name__ == "__main__":
    main()
