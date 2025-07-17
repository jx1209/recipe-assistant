import re
from typing import Dict, List

def interpret_user_input(raw_text: str) -> Dict:
    """
    Parses user input like:
    "I want a vegetarian meal with chickpeas and spinach"
    into structured fields for search.
    """
    raw_text = raw_text.lower()

    ingredients = re.findall(r'\b(?:with|have|using|including)?\s*([\w\s]+?)(?:,|and|$)', raw_text)
    ingredients = [i.strip() for i in ingredients if len(i.strip()) > 1]

    # Detect dietary goals
    diet_keywords = {
        "vegetarian": "vegetarian",
        "vegan": "vegan",
        "low carb": "low_carb",
        "keto": "keto",
        "gluten free": "gluten_free",
        "healthy": "balanced"
    }
    diet = None
    for keyword, tag in diet_keywords.items():
        if keyword in raw_text:
            diet = tag
            break

    goal = None
    if "breakfast" in raw_text:
        goal = "breakfast"
    elif "lunch" in raw_text:
        goal = "lunch"
    elif "dinner" in raw_text or "supper" in raw_text:
        goal = "dinner"
    elif "snack" in raw_text:
        goal = "snack"

    return {
        "ingredients": list(set(ingredients)),
        "diet": diet,
        "goal": goal
    }

# Debug CLI
if __name__ == "__main__":
    prompt = input("Describe your food idea: ")
    print(interpret_user_input(prompt))
