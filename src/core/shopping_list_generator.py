import json
import csv
import os
import re
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from pathlib import Path

class ShoppingListGenerator:
    def __init__(
        self,
        pantry_items: Optional[List[str]] = None,
        enable_substitutions: bool = True,
        export_dir: str = "data/shopping_lists"
    ):
        self.pantry_items = set(map(str.lower, pantry_items or []))
        self.enable_substitutions = enable_substitutions
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

        self.substitution_map = {
            "milk": ["almond milk", "soy milk", "oat milk"],
            "butter": ["margarine", "coconut oil"],
            "flour": ["almond flour", "coconut flour"],
            "sugar": ["honey", "stevia"],
            "eggs": ["chia eggs", "applesauce", "banana"]
        }

        self.category_map = {
            "vegetables": ["tomato", "onion", "lettuce", "spinach", "pepper"],
            "fruits": ["apple", "banana", "lemon", "orange"],
            "dairy": ["milk", "cheese", "butter", "cream"],
            "proteins": ["chicken", "beef", "tofu", "eggs"],
            "grains": ["rice", "flour", "pasta", "bread"],
            "spices": ["salt", "pepper", "basil", "oregano"],
            "oils": ["olive oil", "vegetable oil"],
            "others": []
        }

    def generate(
        self, recipes: List[Dict], exclude_pantry: bool = True
    ) -> Dict[str, List[Dict]]:
        all_ingredients = []
        for recipe in recipes:
            all_ingredients += recipe.get("ingredients", [])

        parsed_ingredients = self._parse_ingredients(all_ingredients)

        if exclude_pantry:
            parsed_ingredients = [
                ing for ing in parsed_ingredients
                if ing["name"].lower() not in self.pantry_items
            ]

        deduped = self._deduplicate(parsed_ingredients)
        categorized = self._categorize(deduped)

        if self.enable_substitutions:
            self._suggest_substitutions(categorized)

        return categorized

    def export(
        self,
        categorized_list: Dict[str, List[Dict]],
        filename_base: str = "shopping_list"
    ):
        json_path = self.export_dir / f"{filename_base}.json"
        txt_path = self.export_dir / f"{filename_base}.txt"
        csv_path = self.export_dir / f"{filename_base}.csv"

        # JSON
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(categorized_list, f, indent=2)

        # Plaintext
        with open(txt_path, "w", encoding="utf-8") as f:
            for category, items in categorized_list.items():
                f.write(f"## {category.upper()}\n")
                for item in items:
                    line = f"- {item['name']}"
                    if item.get("quantity"):
                        line += f" ({item['quantity']})"
                    if item.get("substitutions"):
                        line += f" [subs: {', '.join(item['substitutions'])}]"
                    f.write(line + "\n")
                f.write("\n")

        # CSV
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Category", "Ingredient", "Quantity", "Substitutions"])
            for category, items in categorized_list.items():
                for item in items:
                    writer.writerow([
                        category,
                        item["name"],
                        item.get("quantity", ""),
                        ", ".join(item.get("substitutions", []))
                    ])

    def _parse_ingredients(self, raw_ingredients: List[str]) -> List[Dict]:
        result = []
        pattern = r"(?P<quantity>[\d/.\s]+)?\s*(?P<unit>cups?|tsp|tbsp|grams?|oz|ml|kg|lbs?)?\s*(?P<name>.+)"
        for line in raw_ingredients:
            match = re.match(pattern, line.lower())
            if match:
                name = match.group("name").strip()
                result.append({
                    "name": name,
                    "quantity": match.group("quantity") or "",
                    "unit": match.group("unit") or ""
                })
            else:
                result.append({"name": line.strip(), "quantity": "", "unit": ""})
        return result

    def _deduplicate(self, ingredients: List[Dict]) -> List[Dict]:
        grouped = defaultdict(list)
        for ing in ingredients:
            grouped[ing["name"].lower()].append(ing)

        deduped = []
        for name, group in grouped.items():
            quantities = [g["quantity"] for g in group if g["quantity"]]
            unit = group[0]["unit"]
            deduped.append({
                "name": name,
                "quantity": " + ".join(quantities) if quantities else "",
                "unit": unit
            })

        return deduped

    def _categorize(self, ingredients: List[Dict]) -> Dict[str, List[Dict]]:
        categorized = defaultdict(list)
        for ing in ingredients:
            found = False
            for category, keywords in self.category_map.items():
                if any(k in ing["name"] for k in keywords):
                    categorized[category].append(ing)
                    found = True
                    break
            if not found:
                categorized["others"].append(ing)
        return dict(categorized)

    def _suggest_substitutions(self, categorized: Dict[str, List[Dict]]):
        for items in categorized.values():
            for ing in items:
                subs = self.substitution_map.get(ing["name"].lower())
                if subs:
                    ing["substitutions"] = subs

