"""
Ingredient Substitution Engine
Suggests intelligent substitutions based on dietary needs, pantry, or availability.
"""

from typing import List, Dict, Optional


class SubstitutionEngine:
    def __init__(self):
        self.substitution_rules: Dict[str, List[str]] = {
            "egg": ["1 tbsp flaxseed + 3 tbsp water", "1/4 cup applesauce", "1/2 mashed banana"],
            "milk": ["almond milk", "soy milk", "oat milk", "water + 1 tbsp butter"],
            "buttermilk": ["1 tbsp vinegar + 1 cup milk", "1 tbsp lemon juice + 1 cup milk"],
            "butter": ["coconut oil", "olive oil", "applesauce (for baking)"],
            "sugar": ["honey", "maple syrup", "agave nectar"],
            "flour": ["almond flour", "oat flour", "coconut flour"],
            "yogurt": ["sour cream", "coconut yogurt", "mashed banana"],
            "cream": ["evaporated milk", "greek yogurt", "blended tofu"],
            "soy sauce": ["tamari", "coconut aminos", "Worcestershire sauce"],
            "meat": ["tofu", "tempeh", "seitan", "mushrooms"],
            "cheese": ["nutritional yeast", "vegan cheese", "tofu ricotta"],
        }

    def suggest(self, ingredient: str, dietary_flags: Optional[List[str]] = None, pantry: Optional[List[str]] = None) -> List[str]:
        """
        Suggest substitutions for an ingredient, optionally filtered by dietary needs and pantry inventory.
        """
        ingredient = ingredient.lower()
        substitutions = self.substitution_rules.get(ingredient, [])
        filtered = []

        for sub in substitutions:
            if dietary_flags:
                if "vegan" in dietary_flags and any(animal in sub for animal in ["milk", "butter", "cream", "egg", "honey", "cheese"]):
                    continue
            if pantry:
                # Favor substitutions that exist in pantry
                if any(p in sub.lower() for p in pantry):
                    filtered.insert(0, sub)  # priority suggestion
                    continue
            filtered.append(sub)

        return filtered if filtered else substitutions

    def add_custom_rule(self, ingredient: str, alternatives: List[str]) -> None:
        """
        Add or overwrite a custom substitution rule.
        """
        self.substitution_rules[ingredient.lower()] = alternatives

    def get_supported_ingredients(self) -> List[str]:
        return list(self.substitution_rules.keys())

    def get_all_rules(self) -> Dict[str, List[str]]:
        return self.substitution_rules
