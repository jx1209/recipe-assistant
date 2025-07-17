def recommend_recipes(input_data: Dict, recipe_db: RecipeDatabase) -> List[Dict]:
    """
    Given parsed input, rank recipes by relevance and nutrition.
    Future: embed ingredients, use transformer reranker, etc.
    """
    ingredients = input_data["ingredients"]
    ...
