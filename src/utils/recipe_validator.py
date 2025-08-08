"""
Recipe Validator
Checks that recipes have required fields and valid units.
"""

from typing import Dict, List

VALID_UNITS = {
    "cup", "cups", "tbsp", "tablespoon", "tsp", "teaspoon",
    "g", "gram", "grams", "kg", "kilogram", "oz", "ounce", "ml", "liter", "l", "lb", "pound"
}

class RecipeValidator:
    def __init__(self):
        self.min_ingredients = 2
        self.min_instructions = 2

    def validate(self, recipe: Dict) -> Dict:
        errors = []

        if not recipe.get("title"):
            errors.append("Missing title")

        if "ingredients" not in recipe or len(recipe["ingredients"]) < self.min_ingredients:
            errors.append("Too few ingredients")

        if "instructions" not in recipe or len(recipe["instructions"]) < self.min_instructions:
            errors.append("Too few instructions")

        invalid_units = self._check_units(recipe.get("ingredients", []))
        if invalid_units:
            errors.append(f"Invalid units found: {', '.join(invalid_units)}")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }

    def _check_units(self, ingredients: List[str]) -> List[str]:
        invalid = []
        for line in ingredients:
            tokens = line.lower().split()
            for token in tokens:
                if token in VALID_UNITS:
                    break
            else:
                invalid.append(line)
        return invalid
