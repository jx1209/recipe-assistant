"""
Recipe Search Engine
Searches across titles, ingredients, and tags with keyword matching.
"""

from typing import List, Dict


class SearchEngine:
    def __init__(self, recipe_db: List[Dict]):
        self.recipes = recipe_db  # list of full recipe dicts

    def search(self, query: str, fields: List[str] = ["title", "ingredients", "tags"]) -> List[Dict]:
        results = []
        query = query.lower()

        for recipe in self.recipes:
            for field in fields:
                content = recipe.get(field, "")
                if isinstance(content, list):
                    content = " ".join(content)
                if query in content.lower():
                    results.append(recipe)
                    break  # avoid duplicates
        return results

    def fuzzy_search(self, query: str, threshold: float = 0.6) -> List[Dict]:
        from difflib import SequenceMatcher

        results = []
        for recipe in self.recipes:
            title = recipe.get("title", "").lower()
            ratio = SequenceMatcher(None, query.lower(), title).ratio()
            if ratio >= threshold:
                results.append(recipe)
        return results
