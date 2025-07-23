import re
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
from fractions import Fraction

from src.core.recipe_database import RecipeDatabase  # adjust if you're using AdvancedRecipeDatabase


class ShoppingListGenerator:
    def __init__(self, database: Optional[RecipeDatabase] = None):
        self.database = database or RecipeDatabase()
        self.category_keywords = {
            "produce": ["tomato", "onion", "lettuce", "carrot", "apple", "banana", "pepper", "spinach", "potato"],
            "dairy": ["milk", "cheese", "butter", "yogurt", "cream", "eggs"],
            "meat": ["chicken", "beef", "pork", "turkey", "bacon", "ham", "sausage"],
            "grains": ["bread", "rice", "pasta", "flour", "oats", "cereal", "tortilla"],
            "spices": ["salt", "pepper", "cumin", "paprika", "oregano", "thyme", "basil", "chili"],
            "canned_goods": ["beans", "soup", "tomato paste", "corn", "peas"],
            "frozen": ["frozen vegetables", "ice cream", "frozen pizza"],
            "condiments": ["ketchup", "mustard", "soy sauce", "vinegar", "mayonnaise"],
            "baking": ["sugar", "baking powder", "yeast", "vanilla", "cocoa"],
        }

    def generate_shopping_list(
        self,
        recipe_ids: List[str],
        pantry_items: Optional[List[str]] = None,
        servings_multiplier: float = 1.0,
        combine_duplicates: bool = True
    ) -> Dict[str, List[str]]:
        pantry_items = pantry_items or []
        all_ingredients = []

        for recipe_id in recipe_ids:
            recipe = self.database.get_recipe(recipe_id)
            if not recipe:
                continue
            ingredients = recipe.get("ingredients", [])
            scaled = self._scale_ingredients(ingredients, servings_multiplier)
            all_ingredients.extend(scaled)

        if combine_duplicates:
            deduped = self._aggregate_and_deduplicate(all_ingredients, pantry_items)
        else:
            deduped = self._deduplicate_ingredients(all_ingredients, pantry_items)

        categorized = self._categorize_ingredients(deduped)
        return categorized

    def _scale_ingredients(self, ingredients: List[str], multiplier: float) -> List[str]:
        scaled = []
        for item in ingredients:
            match = re.match(r"^([\d/.]+)\s+(.*)", item)
            if match:
                quantity, rest = match.groups()
                try:
                    quantity_val = float(Fraction(quantity))
                    scaled_quantity = round(quantity_val * multiplier, 2)
                    scaled.append(f"{scaled_quantity} {rest}")
                except Exception:
                    scaled.append(item)
            else:
                scaled.append(item)
        return scaled

    def _deduplicate_ingredients(self, ingredients: List[str], pantry_items: List[str]) -> List[str]:
        cleaned = []
        seen = set()
        for item in ingredients:
            norm = self._normalize_ingredient(item)
            if any(p in norm for p in pantry_items):
                continue
            if norm not in seen:
                seen.add(norm)
                cleaned.append(item)
        return cleaned

    def _aggregate_and_deduplicate(self, ingredients: List[str], pantry_items: List[str]) -> List[str]:
        aggregated = defaultdict(float)
        units = {}
        for item in ingredients:
            norm = self._normalize_ingredient(item)
            if any(p in norm for p in pantry_items):
                continue
            qty, name, unit = self._parse_quantity_and_unit(item)
            if name:
                aggregated[name] += qty
                units[name] = unit
        return [f"{round(aggregated[name], 2)} {units[name]} {name}" if units[name] else f"{round(aggregated[name], 2)} {name}" for name in aggregated]

    def _parse_quantity_and_unit(self, item: str) -> Tuple[float, str, str]:
        match = re.match(r"^([\d/.]+)\s+(\w+)?\s*(.*)", item)
        if match:
            quantity = float(Fraction(match.group(1)))
            unit = match.group(2) if match.group(2) and not match.group(2).isdigit() else ""
            rest = match.group(3).strip() if match.group(3) else ""
            return quantity, rest, unit
        return 1.0, item, ""

    def _normalize_ingredient(self, ingredient: str) -> str:
        cleaned = re.sub(r"[^a-zA-Z\s]", "", ingredient)
        return cleaned.strip().lower()

    def _categorize_ingredients(self, ingredients: List[str]) -> Dict[str, List[str]]:
        categorized = defaultdict(list)
        for item in ingredients:
            found = False
            for category, keywords in self.category_keywords.items():
                if any(kw in item.lower() for kw in keywords):
                    categorized[category].append(item)
                    found = True
                    break
            if not found:
                categorized["other"].append(item)
        return dict(categorized)

    def print_shopping_list(self, categorized: Dict[str, List[str]]):
        print("\n🛒 Shopping List:")
        for category, items in categorized.items():
            print(f"\n📂 {category.title()}")
            for i in items:
                print(f"  - {i}")

    def to_markdown(self, categorized: Dict[str, List[str]]) -> str:
        lines = ["# 🛒 Shopping List\n"]
        for category, items in categorized.items():
            lines.append(f"## {category.title()}")
            for item in items:
                lines.append(f"- [ ] {item}")
            lines.append("")
        return "\n".join(lines)
