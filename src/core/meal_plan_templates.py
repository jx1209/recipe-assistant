"""
template-based meal plan generator
provides pre-designed meal plans as fallback when AI is unavailable
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import random


class MealPlanTemplates:
    """generates meal plans from predefined templates"""
    
    def __init__(self):
        self.templates = self._build_templates()
    
    def _build_templates(self) -> Dict[str, Dict]:
        """build library of meal plan templates"""
        return {
            "balanced_weekly": {
                "name": "Balanced Weekly Plan",
                "description": "Well-rounded meals with variety of proteins and vegetables",
                "duration_days": 7,
                "dietary_restrictions": [],
                "meals": {
                    "day_1": {
                        "breakfast": {"name": "Scrambled Eggs with Toast", "prep_time": 10, "tags": ["quick", "protein"]},
                        "lunch": {"name": "Grilled Chicken Salad", "prep_time": 15, "tags": ["healthy", "protein"]},
                        "dinner": {"name": "Spaghetti with Marinara", "prep_time": 30, "tags": ["italian", "pasta"]},
                    },
                    "day_2": {
                        "breakfast": {"name": "Oatmeal with Berries", "prep_time": 10, "tags": ["healthy", "fiber"]},
                        "lunch": {"name": "Turkey Sandwich with Side Salad", "prep_time": 10, "tags": ["quick", "protein"]},
                        "dinner": {"name": "Baked Salmon with Roasted Vegetables", "prep_time": 35, "tags": ["healthy", "fish"]},
                    },
                    "day_3": {
                        "breakfast": {"name": "Greek Yogurt Parfait", "prep_time": 5, "tags": ["quick", "healthy"]},
                        "lunch": {"name": "Vegetable Stir-Fry with Rice", "prep_time": 25, "tags": ["vegetarian", "asian"]},
                        "dinner": {"name": "Beef Tacos with Fixings", "prep_time": 30, "tags": ["mexican", "family-friendly"]},
                    },
                    "day_4": {
                        "breakfast": {"name": "Whole Grain Toast with Avocado", "prep_time": 10, "tags": ["quick", "healthy"]},
                        "lunch": {"name": "Chicken Caesar Wrap", "prep_time": 15, "tags": ["quick", "protein"]},
                        "dinner": {"name": "Vegetable Lasagna", "prep_time": 60, "tags": ["italian", "vegetarian"]},
                    },
                    "day_5": {
                        "breakfast": {"name": "Smoothie Bowl", "prep_time": 10, "tags": ["quick", "healthy"]},
                        "lunch": {"name": "Quinoa Buddha Bowl", "prep_time": 20, "tags": ["healthy", "vegetarian"]},
                        "dinner": {"name": "Grilled Chicken with Sweet Potato", "prep_time": 40, "tags": ["healthy", "protein"]},
                    },
                    "day_6": {
                        "breakfast": {"name": "Pancakes with Fruit", "prep_time": 20, "tags": ["weekend", "family-friendly"]},
                        "lunch": {"name": "Tomato Soup with Grilled Cheese", "prep_time": 25, "tags": ["comfort", "vegetarian"]},
                        "dinner": {"name": "Shrimp Pasta with Garlic Sauce", "prep_time": 30, "tags": ["seafood", "italian"]},
                    },
                    "day_7": {
                        "breakfast": {"name": "Veggie Omelet", "prep_time": 15, "tags": ["protein", "healthy"]},
                        "lunch": {"name": "Mediterranean Chicken Plate", "prep_time": 30, "tags": ["healthy", "mediterranean"]},
                        "dinner": {"name": "Homemade Pizza Night", "prep_time": 45, "tags": ["fun", "family-friendly"]},
                    },
                }
            },
            
            "vegetarian_weekly": {
                "name": "Vegetarian Weekly Plan",
                "description": "Plant-based meals with complete proteins",
                "duration_days": 7,
                "dietary_restrictions": ["vegetarian"],
                "meals": {
                    "day_1": {
                        "breakfast": {"name": "Veggie Scramble with Toast", "prep_time": 15, "tags": ["vegetarian", "protein"]},
                        "lunch": {"name": "Caprese Salad with Balsamic", "prep_time": 10, "tags": ["vegetarian", "quick"]},
                        "dinner": {"name": "Vegetable Curry with Rice", "prep_time": 40, "tags": ["vegetarian", "indian"]},
                    },
                    "day_2": {
                        "breakfast": {"name": "Avocado Toast with Poached Egg", "prep_time": 10, "tags": ["vegetarian", "healthy"]},
                        "lunch": {"name": "Black Bean Burrito Bowl", "prep_time": 20, "tags": ["vegetarian", "mexican"]},
                        "dinner": {"name": "Eggplant Parmesan", "prep_time": 50, "tags": ["vegetarian", "italian"]},
                    },
                    "day_3": {
                        "breakfast": {"name": "Protein Smoothie", "prep_time": 5, "tags": ["vegetarian", "quick"]},
                        "lunch": {"name": "Falafel Wrap with Tahini", "prep_time": 15, "tags": ["vegetarian", "mediterranean"]},
                        "dinner": {"name": "Mushroom Risotto", "prep_time": 45, "tags": ["vegetarian", "italian"]},
                    },
                    "day_4": {
                        "breakfast": {"name": "Chia Seed Pudding", "prep_time": 5, "tags": ["vegetarian", "healthy"]},
                        "lunch": {"name": "Greek Salad with Pita", "prep_time": 15, "tags": ["vegetarian", "mediterranean"]},
                        "dinner": {"name": "Lentil Shepherd's Pie", "prep_time": 60, "tags": ["vegetarian", "comfort"]},
                    },
                    "day_5": {
                        "breakfast": {"name": "French Toast", "prep_time": 15, "tags": ["vegetarian", "sweet"]},
                        "lunch": {"name": "Chickpea Salad Sandwich", "prep_time": 10, "tags": ["vegetarian", "quick"]},
                        "dinner": {"name": "Vegetable Pad Thai", "prep_time": 30, "tags": ["vegetarian", "asian"]},
                    },
                    "day_6": {
                        "breakfast": {"name": "Banana Oat Pancakes", "prep_time": 20, "tags": ["vegetarian", "healthy"]},
                        "lunch": {"name": "Minestrone Soup", "prep_time": 35, "tags": ["vegetarian", "italian"]},
                        "dinner": {"name": "Stuffed Bell Peppers", "prep_time": 50, "tags": ["vegetarian", "healthy"]},
                    },
                    "day_7": {
                        "breakfast": {"name": "Veggie Frittata", "prep_time": 25, "tags": ["vegetarian", "protein"]},
                        "lunch": {"name": "Hummus Veggie Wrap", "prep_time": 10, "tags": ["vegetarian", "quick"]},
                        "dinner": {"name": "Margherita Pizza", "prep_time": 30, "tags": ["vegetarian", "italian"]},
                    },
                }
            },
            
            "quick_meals": {
                "name": "Quick & Easy Weekly Plan",
                "description": "All meals under 30 minutes for busy schedules",
                "duration_days": 7,
                "dietary_restrictions": [],
                "meals": {
                    "day_1": {
                        "breakfast": {"name": "Cereal with Fruit", "prep_time": 5, "tags": ["quick", "easy"]},
                        "lunch": {"name": "Deli Sandwich", "prep_time": 10, "tags": ["quick", "easy"]},
                        "dinner": {"name": "Pan-Seared Chicken with Salad", "prep_time": 25, "tags": ["quick", "protein"]},
                    },
                    "day_2": {
                        "breakfast": {"name": "Instant Oatmeal", "prep_time": 5, "tags": ["quick", "easy"]},
                        "lunch": {"name": "Canned Soup with Crackers", "prep_time": 10, "tags": ["quick", "easy"]},
                        "dinner": {"name": "Pasta with Jar Sauce", "prep_time": 20, "tags": ["quick", "italian"]},
                    },
                    "day_3": {
                        "breakfast": {"name": "Toast with Peanut Butter", "prep_time": 5, "tags": ["quick", "easy"]},
                        "lunch": {"name": "Quesadilla", "prep_time": 15, "tags": ["quick", "mexican"]},
                        "dinner": {"name": "Stir-Fry with Pre-cut Veggies", "prep_time": 20, "tags": ["quick", "asian"]},
                    },
                    "day_4": {
                        "breakfast": {"name": "Yogurt and Granola", "prep_time": 5, "tags": ["quick", "healthy"]},
                        "lunch": {"name": "Frozen Pizza", "prep_time": 15, "tags": ["quick", "easy"]},
                        "dinner": {"name": "Tacos with Pre-cooked Meat", "prep_time": 20, "tags": ["quick", "mexican"]},
                    },
                    "day_5": {
                        "breakfast": {"name": "Bagel with Cream Cheese", "prep_time": 5, "tags": ["quick", "easy"]},
                        "lunch": {"name": "Instant Ramen (Enhanced)", "prep_time": 10, "tags": ["quick", "asian"]},
                        "dinner": {"name": "Sheet Pan Sausages and Veggies", "prep_time": 30, "tags": ["quick", "easy"]},
                    },
                    "day_6": {
                        "breakfast": {"name": "Frozen Waffles", "prep_time": 5, "tags": ["quick", "easy"]},
                        "lunch": {"name": "Grilled Cheese", "prep_time": 10, "tags": ["quick", "comfort"]},
                        "dinner": {"name": "Rotisserie Chicken with Sides", "prep_time": 15, "tags": ["quick", "easy"]},
                    },
                    "day_7": {
                        "breakfast": {"name": "Smoothie", "prep_time": 5, "tags": ["quick", "healthy"]},
                        "lunch": {"name": "Leftovers Buffet", "prep_time": 10, "tags": ["quick", "easy"]},
                        "dinner": {"name": "Takeout Night", "prep_time": 0, "tags": ["easy", "fun"]},
                    },
                }
            },
            
            "family_friendly": {
                "name": "Family-Friendly Weekly Plan",
                "description": "Kid-approved meals the whole family will enjoy",
                "duration_days": 7,
                "dietary_restrictions": [],
                "meals": {
                    "day_1": {
                        "breakfast": {"name": "Scrambled Eggs and Bacon", "prep_time": 15, "tags": ["family-friendly", "protein"]},
                        "lunch": {"name": "Mac and Cheese", "prep_time": 20, "tags": ["family-friendly", "comfort"]},
                        "dinner": {"name": "Spaghetti and Meatballs", "prep_time": 40, "tags": ["family-friendly", "italian"]},
                    },
                    "day_2": {
                        "breakfast": {"name": "Pancakes with Syrup", "prep_time": 20, "tags": ["family-friendly", "sweet"]},
                        "lunch": {"name": "Chicken Nuggets with Fries", "prep_time": 25, "tags": ["family-friendly", "quick"]},
                        "dinner": {"name": "Hamburgers and Fries", "prep_time": 30, "tags": ["family-friendly", "american"]},
                    },
                    "day_3": {
                        "breakfast": {"name": "Cereal and Fruit", "prep_time": 5, "tags": ["family-friendly", "quick"]},
                        "lunch": {"name": "PB&J Sandwiches", "prep_time": 5, "tags": ["family-friendly", "quick"]},
                        "dinner": {"name": "Taco Tuesday", "prep_time": 30, "tags": ["family-friendly", "mexican"]},
                    },
                    "day_4": {
                        "breakfast": {"name": "Waffles with Berries", "prep_time": 15, "tags": ["family-friendly", "sweet"]},
                        "lunch": {"name": "Grilled Cheese with Tomato Soup", "prep_time": 20, "tags": ["family-friendly", "comfort"]},
                        "dinner": {"name": "Baked Chicken Tenders", "prep_time": 35, "tags": ["family-friendly", "healthy"]},
                    },
                    "day_5": {
                        "breakfast": {"name": "French Toast Sticks", "prep_time": 15, "tags": ["family-friendly", "fun"]},
                        "lunch": {"name": "Hot Dogs", "prep_time": 10, "tags": ["family-friendly", "quick"]},
                        "dinner": {"name": "Homemade Pizza", "prep_time": 45, "tags": ["family-friendly", "fun"]},
                    },
                    "day_6": {
                        "breakfast": {"name": "Breakfast Burritos", "prep_time": 20, "tags": ["family-friendly", "protein"]},
                        "lunch": {"name": "Corn Dogs", "prep_time": 15, "tags": ["family-friendly", "quick"]},
                        "dinner": {"name": "BBQ Ribs with Corn", "prep_time": 90, "tags": ["family-friendly", "american"]},
                    },
                    "day_7": {
                        "breakfast": {"name": "Donuts and Milk", "prep_time": 5, "tags": ["family-friendly", "treat"]},
                        "lunch": {"name": "Leftover Pizza", "prep_time": 5, "tags": ["family-friendly", "easy"]},
                        "dinner": {"name": "Build-Your-Own Burger Bar", "prep_time": 35, "tags": ["family-friendly", "fun"]},
                    },
                }
            },
            
            "budget_friendly": {
                "name": "Budget-Friendly Weekly Plan",
                "description": "Delicious meals using affordable ingredients",
                "duration_days": 7,
                "dietary_restrictions": [],
                "meals": {
                    "day_1": {
                        "breakfast": {"name": "Oatmeal", "prep_time": 10, "tags": ["budget", "healthy"]},
                        "lunch": {"name": "Rice and Beans", "prep_time": 25, "tags": ["budget", "protein"]},
                        "dinner": {"name": "Spaghetti with Tomato Sauce", "prep_time": 30, "tags": ["budget", "italian"]},
                    },
                    "day_2": {
                        "breakfast": {"name": "Scrambled Eggs", "prep_time": 10, "tags": ["budget", "protein"]},
                        "lunch": {"name": "Bean Burritos", "prep_time": 15, "tags": ["budget", "mexican"]},
                        "dinner": {"name": "Chicken Thighs with Potatoes", "prep_time": 50, "tags": ["budget", "protein"]},
                    },
                    "day_3": {
                        "breakfast": {"name": "Toast with Jam", "prep_time": 5, "tags": ["budget", "quick"]},
                        "lunch": {"name": "Peanut Butter Sandwich", "prep_time": 5, "tags": ["budget", "quick"]},
                        "dinner": {"name": "Fried Rice with Vegetables", "prep_time": 25, "tags": ["budget", "asian"]},
                    },
                    "day_4": {
                        "breakfast": {"name": "Banana and Peanut Butter", "prep_time": 5, "tags": ["budget", "quick"]},
                        "lunch": {"name": "Lentil Soup", "prep_time": 35, "tags": ["budget", "healthy"]},
                        "dinner": {"name": "Baked Potato Bar", "prep_time": 60, "tags": ["budget", "easy"]},
                    },
                    "day_5": {
                        "breakfast": {"name": "Cereal", "prep_time": 5, "tags": ["budget", "quick"]},
                        "lunch": {"name": "Egg Salad Sandwich", "prep_time": 15, "tags": ["budget", "protein"]},
                        "dinner": {"name": "Chili with Cornbread", "prep_time": 45, "tags": ["budget", "comfort"]},
                    },
                    "day_6": {
                        "breakfast": {"name": "Pancakes from Mix", "prep_time": 15, "tags": ["budget", "easy"]},
                        "lunch": {"name": "Tuna Sandwich", "prep_time": 10, "tags": ["budget", "protein"]},
                        "dinner": {"name": "Chicken Soup from Scratch", "prep_time": 60, "tags": ["budget", "comfort"]},
                    },
                    "day_7": {
                        "breakfast": {"name": "Eggs and Toast", "prep_time": 10, "tags": ["budget", "protein"]},
                        "lunch": {"name": "Leftover Soup", "prep_time": 10, "tags": ["budget", "easy"]},
                        "dinner": {"name": "Pasta with Butter and Parmesan", "prep_time": 20, "tags": ["budget", "italian"]},
                    },
                }
            }
        }
    
    def get_meal_plan(
        self,
        template_name: str = "balanced_weekly",
        days: Optional[int] = None,
        dietary_restrictions: Optional[List[str]] = None
    ) -> Dict:
        """
        get a meal plan from template
        
        args:
            template_name: name of template to use
            days: number of days (will cycle template if longer)
            dietary_restrictions: filter by dietary needs
        
        returns:
            meal plan dictionary with all meals
        """
        # Find matching template
        template = self.templates.get(template_name)
        
        if not template:
            # Try to find best match based on dietary restrictions
            template = self._find_best_template(dietary_restrictions)
        
        if not template:
            template = self.templates["balanced_weekly"]  # Default fallback
        
        # Adjust for requested days
        if days and days != template["duration_days"]:
            template = self._adjust_duration(template, days)
        
        return {
            "name": template["name"],
            "description": template["description"],
            "duration_days": template["duration_days"],
            "dietary_restrictions": template["dietary_restrictions"],
            "meals": template["meals"],
            "created_at": datetime.now().isoformat(),
            "source": "template"
        }
    
    def _find_best_template(self, dietary_restrictions: Optional[List[str]]) -> Optional[Dict]:
        """find best matching template for dietary restrictions"""
        if not dietary_restrictions:
            return self.templates["balanced_weekly"]
        
        restrictions_lower = [r.lower() for r in dietary_restrictions]
        
        if "vegetarian" in restrictions_lower or "vegan" in restrictions_lower:
            return self.templates["vegetarian_weekly"]
        
        return self.templates["balanced_weekly"]
    
    def _adjust_duration(self, template: Dict, target_days: int) -> Dict:
        """adjust template duration by cycling or truncating meals"""
        current_days = template["duration_days"]
        
        if target_days <= current_days:
            # Truncate
            new_meals = {}
            for i in range(1, target_days + 1):
                new_meals[f"day_{i}"] = template["meals"][f"day_{i}"]
            
            adjusted = template.copy()
            adjusted["meals"] = new_meals
            adjusted["duration_days"] = target_days
            return adjusted
        else:
            # Cycle through template
            new_meals = {}
            for i in range(1, target_days + 1):
                day_index = ((i - 1) % current_days) + 1
                new_meals[f"day_{i}"] = template["meals"][f"day_{day_index}"]
            
            adjusted = template.copy()
            adjusted["meals"] = new_meals
            adjusted["duration_days"] = target_days
            return adjusted
    
    def list_templates(self) -> List[Dict]:
        """list all available templates"""
        return [
            {
                "id": key,
                "name": template["name"],
                "description": template["description"],
                "duration_days": template["duration_days"],
                "dietary_restrictions": template["dietary_restrictions"]
            }
            for key, template in self.templates.items()
        ]
    
    def generate_shopping_list(self, meal_plan: Dict) -> List[Dict]:
        """generate shopping list from meal plan (basic version)"""
        # This is a simple version - in reality, you'd want to extract actual ingredients
        categories = {
            "Produce": ["vegetables", "fruits", "herbs"],
            "Proteins": ["chicken", "beef", "fish", "eggs", "beans", "tofu"],
            "Dairy": ["milk", "cheese", "yogurt", "butter"],
            "Pantry": ["pasta", "rice", "flour", "oil", "spices"],
            "Bakery": ["bread", "tortillas", "bagels"],
        }
        
        return [
            {
                "category": "Produce",
                "items": ["Mixed vegetables", "Fresh fruits", "Salad greens"]
            },
            {
                "category": "Proteins",
                "items": ["Chicken breasts", "Ground beef", "Eggs (dozen)"]
            },
            {
                "category": "Dairy",
                "items": ["Milk", "Cheese", "Butter"]
            },
            {
                "category": "Pantry",
                "items": ["Pasta", "Rice", "Olive oil", "Various spices"]
            },
            {
                "category": "Bakery",
                "items": ["Bread", "Tortillas"]
            }
        ]

