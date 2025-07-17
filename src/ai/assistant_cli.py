# src/ai/assistant_cli.py

import sys
from src.ai.input_interpreter import interpret_user_input
from src.recipe_database import RecipeDatabase
from src.ingredient_matcher import SmartIngredientMatcher

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m src.ai.assistant_cli \"your input text here\"")
        return

    user_input = sys.argv[1]
    parsed = interpret_user_input(user_input)
    
    print(f"\n🔍 Parsed Input: {parsed}")

    matcher = SmartIngredientMatcher(database=RecipeDatabase())
    suggestion = matcher.find_matching_recipes(
        user_ingredients=parsed["ingredients"],
        include_online=True,
        max_results=5
    )

    if not suggestion.matches:
        print("\n❌ No matching recipes found.")
        return

    print(f"\n✅ Top Matches ({len(suggestion.matches)}):")
    for i, match in enumerate(suggestion.matches, 1):
        print(f"{i}. {match.recipe_name} - {match.match_percentage:.1f}% match")

if __name__ == "__main__":
    main()
