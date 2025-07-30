"""
Recipe Assistant - Main Application Module
A command-line recipe matching system using modular design
"""

try:
    from .recipe_database import RecipeDatabase
    from .utils.util_funcs import (
        calculate_ingredient_similarity, 
        format_recipe_summary, 
        print_separator, 
        print_header,
        get_yes_no_input,
        parse_ingredient_list
    )
except ImportError:
    # Fallback for when running directly (not as module)
    from recipe_database import RecipeDatabase
    from src.utils.util_funcs import (
        calculate_ingredient_similarity, 
        format_recipe_summary, 
        print_separator, 
        print_header,
        get_yes_no_input,
        parse_ingredient_list
    )

class RecipeAssistant:
    def __init__(self):
        """Initialize the Recipe Assistant"""
        self.database = RecipeDatabase()
        self.recipes = self.database.get_all_recipes()
    
    def find_recipes_by_ingredients(self, available_ingredients):
        """
        Find recipes that match available ingredients using improved similarity matching
        Returns list of recipes sorted by match percentage
        """
        available_ingredients = [ingredient.lower().strip() for ingredient in available_ingredients]
        recipe_matches = []
        
        for recipe_id, recipe in self.recipes.items():
            recipe_ingredients = recipe["ingredients"]
            
            matching_ingredients = []
            missing_ingredients = []
            total_similarity_score = 0
            
            for recipe_ingredient in recipe_ingredients:
                best_match_score = 0
                matched = False
                
                # Check against each available ingredient
                for available_ingredient in available_ingredients:
                    similarity = calculate_ingredient_similarity(recipe_ingredient, available_ingredient)
                    
                    if similarity > best_match_score:
                        best_match_score = similarity
                    
                    # Consider it a match if similarity is above threshold
                    if similarity >= 0.7:
                        matched = True
                
                total_similarity_score += best_match_score
                
                if matched:
                    matching_ingredients.append(recipe_ingredient)
                else:
                    missing_ingredients.append(recipe_ingredient)
            
            # Calculate match percentage based on similarity scores
            if len(recipe_ingredients) > 0:
                match_percentage = (total_similarity_score / len(recipe_ingredients)) * 100
            else:
                match_percentage = 0
            
            recipe_matches.append({
                "recipe": recipe,
                "recipe_id": recipe_id,
                "match_percentage": match_percentage,
                "matching_ingredients": matching_ingredients,
                "missing_ingredients": missing_ingredients
            })
        
        # Sort by match percentage (highest first)
        recipe_matches.sort(key=lambda x: x["match_percentage"], reverse=True)
        return recipe_matches
    
    def display_recipe_summary(self, recipe_data, index):
        """Display a brief recipe summary"""
        recipe = recipe_data["recipe"]
        summary = format_recipe_summary(recipe, recipe_data["match_percentage"])
        print(f"{index}. {summary}")
        
        if recipe_data['missing_ingredients']:
            missing_count = len(recipe_data['missing_ingredients'])
            if missing_count <= 3:
                print(f"   Missing: {', '.join(recipe_data['missing_ingredients'])}")
            else:
                first_three = ', '.join(recipe_data['missing_ingredients'][:3])
                print(f"   Missing: {first_three} (and {missing_count - 3} more)")
        print()
    
    def display_full_recipe(self, recipe_data):
        """Display complete recipe details"""
        recipe = recipe_data["recipe"]
        
        print_header(f"RECIPE: {recipe['name']}")
        
        # Basic info
        info_items = [
            f"Cook Time: {recipe['cook_time']}",
            f"Difficulty: {recipe['difficulty']}",
            f"Servings: {recipe['servings']}",
            f"Ingredient Match: {recipe_data['match_percentage']:.0f}%"
        ]
        
        if 'cuisine' in recipe:
            info_items.append(f"Cuisine: {recipe['cuisine']}")
        
        for item in info_items:
            print(item)
        
        # Tags
        if 'tags' in recipe and recipe['tags']:
            print(f"Tags: {', '.join(recipe['tags'])}")
        
        print_separator()
        
        # Ingredients
        print("INGREDIENTS:")
        for ingredient in recipe["ingredients"]:
            status = "HAVE" if ingredient in recipe_data["matching_ingredients"] else "NEED"
            print(f"  [{status}] {ingredient.title()}")
        
        print_separator()
        
        # Instructions
        print("INSTRUCTIONS:")
        for i, step in enumerate(recipe["instructions"], 1):
            print(f"  {i}. {step}")
        
        print_separator()
        print()
    
    def get_user_ingredients(self):
        """Get ingredients from user input with improved parsing"""
        print("Enter your available ingredients separated by commas.")
        print("Example: chicken, rice, vegetables, soy sauce")
        print("Or type 'help' for more examples")
        
        while True:
            user_input = input("\nYour ingredients: ").strip()
            
            if user_input.lower() == 'help':
                self.show_ingredient_examples()
                continue
            elif not user_input:
                print("Please enter at least one ingredient.")
                continue
            
            ingredients = parse_ingredient_list(user_input)
            
            if ingredients:
                return ingredients
            else:
                print("Please enter valid ingredients separated by commas.")
    
    def show_ingredient_examples(self):
        """Show example ingredient inputs"""
        print("\nIngredient Input Examples:")
        print("- Basic: eggs, milk, flour")
        print("- With quantities: 2 chicken breasts, 1 cup rice, mixed vegetables")
        print("- Specific items: ground beef, olive oil, fresh basil, canned tomatoes")
        print("- Categories work too: vegetables, meat, herbs, spices")
    
    def show_search_options(self):
        """Show additional search options"""
        print("\nAdditional Search Options:")
        print("1. Search by ingredients (default)")
        print("2. Browse by cuisine type")
        print("3. Browse by tags (breakfast, dinner, vegetarian, etc.)")
        print("4. View all recipes")
        
        choice = input("Choose an option (1-4) or press Enter for ingredient search: ").strip()
        
        if choice == '2':
            return self.browse_by_cuisine()
        elif choice == '3':
            return self.browse_by_tags()
        elif choice == '4':
            return self.view_all_recipes()
        else:
            return None  # Default to ingredient search
    
    def browse_by_cuisine(self):
        """Browse recipes by cuisine type"""
        cuisines = set()
        for recipe in self.recipes.values():
            if 'cuisine' in recipe:
                cuisines.add(recipe['cuisine'])
        
        if not cuisines:
            print("No cuisine information available.")
            return []
        
        print(f"\nAvailable cuisines: {', '.join(sorted(cuisines))}")
        cuisine_choice = input("Enter cuisine type: ").strip()
        
        matching_recipes = self.database.search_recipes_by_cuisine(cuisine_choice)
        
        if matching_recipes:
            # Convert to format expected by display functions
            matches = []
            for recipe_id, recipe in matching_recipes.items():
                matches.append({
                    "recipe": recipe,
                    "recipe_id": recipe_id,
                    "match_percentage": 100,  # Full match since they chose this cuisine
                    "matching_ingredients": recipe["ingredients"],
                    "missing_ingredients": []
                })
            return matches
        else:
            print(f"No recipes found for {cuisine_choice} cuisine.")
            return []
    
    def browse_by_tags(self):
        """Browse recipes by tags"""
        all_tags = set()
        for recipe in self.recipes.values():
            if 'tags' in recipe:
                all_tags.update(recipe['tags'])
        
        if not all_tags:
            print("No tags available.")
            return []
        
        print(f"\nAvailable tags: {', '.join(sorted(all_tags))}")
        tag_choice = input("Enter tag: ").strip()
        
        matching_recipes = self.database.search_recipes_by_tag(tag_choice)
        
        if matching_recipes:
            matches = []
            for recipe_id, recipe in matching_recipes.items():
                matches.append({
                    "recipe": recipe,
                    "recipe_id": recipe_id,
                    "match_percentage": 100,
                    "matching_ingredients": recipe["ingredients"],
                    "missing_ingredients": []
                })
            return matches
        else:
            print(f"No recipes found with tag '{tag_choice}'.")
            return []
    
    def view_all_recipes(self):
        """View all available recipes"""
        matches = []
        for recipe_id, recipe in self.recipes.items():
            matches.append({
                "recipe": recipe,
                "recipe_id": recipe_id,
                "match_percentage": 100,
                "matching_ingredients": recipe["ingredients"],
                "missing_ingredients": []
            })
        return matches
    
    def run(self):
        """Main application loop"""
        print_header("RECIPE ASSISTANT")
        print("Find recipes based on your available ingredients")
        print("Type 'quit' at any time to exit")
        print("Type 'options' to see additional search methods\n")
        
        while True:
            ingredients = self.get_user_ingredients()
            
            if not ingredients:
                print("No ingredients entered. Please try again.")
                continue
            
            if 'quit' in ingredients or 'exit' in ingredients:
                print("Exiting Recipe Assistant. Goodbye!")
                break
            
            if 'options' in ingredients:
                matches = self.show_search_options()
                if matches is None:
                    continue
            else:
                matches = self.find_recipes_by_ingredients(ingredients)
            
            if not matches:
                print("No matching recipes found. Try different ingredients.")
                continue
            
            print_header("MATCHED RECIPES")
            for index, recipe_data in enumerate(matches, start=1):
                self.display_recipe_summary(recipe_data, index)
            
            # Ask user to select a recipe to view full details
            while True:
                try:
                    choice = input("Enter recipe number to view details or 'back' to search again: ").strip()
                    if choice.lower() == 'back':
                        break
                    choice_index = int(choice) - 1
                    
                    if 0 <= choice_index < len(matches):
                        self.display_full_recipe(matches[choice_index])
                        break
                    else:
                        print(f"Invalid choice. Please enter a number between 1 and {len(matches)}.")
                except ValueError:
                    print("Please enter a valid number.")

        """Display search results and handle user interaction"""
        # Filter out recipes with very low match
        valid_matches = [match for match in matches if match["match_percentage"] >= 10]
        
        if not valid_matches:
            print("No matching recipes found.")
            print("Try different ingredients or check spelling.\n")
            return
        
        # Display recipe summaries
        print(f"Found {len(valid_matches)} matching recipes:\n")
        
        display_count = min(5, len(valid_matches))
        for i in range(display_count):
            self.display_recipe_summary(valid_matches[i], i + 1)
        
        if len(valid_matches) > display_count:
            print(f"... and {len(valid_matches) - display_count} more recipes")
            show_more = get_yes_no_input("Show all recipes?")
            if show_more:
                for i in range(display_count, len(valid_matches)):
                    self.display_recipe_summary(valid_matches[i], i + 1)
                display_count = len(valid_matches)
        
        # Get user choice for detailed view
        while True:
            choice = input(f"\nView recipe details (1-{display_count}) or 'back' for new search: ").strip().lower()
            
            if choice == 'back':
                break
            elif choice == 'quit':
                return
            
            try:
                recipe_num = int(choice) - 1
                if 0 <= recipe_num < len(valid_matches):
                    self.display_full_recipe(valid_matches[recipe_num])
                    
                    # Ask if they want to see another recipe
                    if not get_yes_no_input("View another recipe?"):
                        break
                else:
                    print(f"Please enter a number between 1 and {display_count}")
            
            except ValueError:
                print("Please enter a valid number or 'back'")

def main():
    """Main entry point for the Recipe Assistant application"""
    assistant = RecipeAssistant()
    assistant.run()

if __name__ == "__main__":
    main()
# This allows the script to be run directly or imported as a module