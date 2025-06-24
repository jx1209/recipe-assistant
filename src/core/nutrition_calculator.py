"""
Nutrition Calculator and Analysis System
Calculate and analyze nutritional information for recipes and meal plans
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class NutritionInfo:
    """Nutritional information for a recipe or meal"""
    calories: float = 0.0
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0
    fiber_g: float = 0.0
    sugar_g: float = 0.0
    sodium_mg: float = 0.0
    cholesterol_mg: float = 0.0
    vitamin_c_mg: float = 0.0
    calcium_mg: float = 0.0
    iron_mg: float = 0.0
    potassium_mg: float = 0.0
    vitamin_a_iu: float = 0.0
    vitamin_d_iu: float = 0.0
    saturated_fat_g: float = 0.0
    trans_fat_g: float = 0.0
    monounsaturated_fat_g: float = 0.0
    polyunsaturated_fat_g: float = 0.0
    
    def __add__(self, other: 'NutritionInfo') -> 'NutritionInfo':
        """Add two nutrition info objects"""
        return NutritionInfo(
            calories=self.calories + other.calories,
            protein_g=self.protein_g + other.protein_g,
            carbs_g=self.carbs_g + other.carbs_g,
            fat_g=self.fat_g + other.fat_g,
            fiber_g=self.fiber_g + other.fiber_g,
            sugar_g=self.sugar_g + other.sugar_g,
            sodium_mg=self.sodium_mg + other.sodium_mg,
            cholesterol_mg=self.cholesterol_mg + other.cholesterol_mg,
            vitamin_c_mg=self.vitamin_c_mg + other.vitamin_c_mg,
            calcium_mg=self.calcium_mg + other.calcium_mg,
            iron_mg=self.iron_mg + other.iron_mg,
            potassium_mg=self.potassium_mg + other.potassium_mg,
            vitamin_a_iu=self.vitamin_a_iu + other.vitamin_a_iu,
            vitamin_d_iu=self.vitamin_d_iu + other.vitamin_d_iu,
            saturated_fat_g=self.saturated_fat_g + other.saturated_fat_g,
            trans_fat_g=self.trans_fat_g + other.trans_fat_g,
            monounsaturated_fat_g=self.monounsaturated_fat_g + other.monounsaturated_fat_g,
            polyunsaturated_fat_g=self.polyunsaturated_fat_g + other.polyunsaturated_fat_g
        )
    
    def scale(self, factor: float) -> 'NutritionInfo':
        """Scale nutrition info by a factor"""
        return NutritionInfo(
            calories=self.calories * factor,
            protein_g=self.protein_g * factor,
            carbs_g=self.carbs_g * factor,
            fat_g=self.fat_g * factor,
            fiber_g=self.fiber_g * factor,
            sugar_g=self.sugar_g * factor,
            sodium_mg=self.sodium_mg * factor,
            cholesterol_mg=self.cholesterol_mg * factor,
            vitamin_c_mg=self.vitamin_c_mg * factor,
            calcium_mg=self.calcium_mg * factor,
            iron_mg=self.iron_mg * factor,
            potassium_mg=self.potassium_mg * factor,
            vitamin_a_iu=self.vitamin_a_iu * factor,
            vitamin_d_iu=self.vitamin_d_iu * factor,
            saturated_fat_g=self.saturated_fat_g * factor,
            trans_fat_g=self.trans_fat_g * factor,
            monounsaturated_fat_g=self.monounsaturated_fat_g * factor,
            polyunsaturated_fat_g=self.polyunsaturated_fat_g * factor
        )
    
    def per_serving(self, servings: int) -> 'NutritionInfo':
        """Calculate nutrition per serving"""
        if servings <= 0:
            return NutritionInfo()
        return self.scale(1.0 / servings)

"""
Nutrition Calculator and Analysis System
Calculate and analyze nutritional information for recipes and meal plans
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class NutritionInfo:
    """Nutritional information for a recipe or meal"""
    calories: float = 0.0
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0
    fiber_g: float = 0.0
    sugar_g: float = 0.0
    sodium_mg: float = 0.0
    cholesterol_mg: float = 0.0
    vitamin_c_mg: float = 0.0
    calcium_mg: float = 0.0
    iron_mg: float = 0.0
    potassium_mg: float = 0.0
    vitamin_a_iu: float = 0.0
    vitamin_d_iu: float = 0.0
    saturated_fat_g: float = 0.0
    trans_fat_g: float = 0.0
    monounsaturated_fat_g: float = 0.0
    polyunsaturated_fat_g: float = 0.0
    
    def __add__(self, other: 'NutritionInfo') -> 'NutritionInfo':
        """Add two nutrition info objects"""
        return NutritionInfo(
            calories=self.calories + other.calories,
            protein_g=self.protein_g + other.protein_g,
            carbs_g=self.carbs_g + other.carbs_g,
            fat_g=self.fat_g + other.fat_g,
            fiber_g=self.fiber_g + other.fiber_g,
            sugar_g=self.sugar_g + other.sugar_g,
            sodium_mg=self.sodium_mg + other.sodium_mg,
            cholesterol_mg=self.cholesterol_mg + other.cholesterol_mg,
            vitamin_c_mg=self.vitamin_c_mg + other.vitamin_c_mg,
            calcium_mg=self.calcium_mg + other.calcium_mg,
            iron_mg=self.iron_mg + other.iron_mg,
            potassium_mg=self.potassium_mg + other.potassium_mg,
            vitamin_a_iu=self.vitamin_a_iu + other.vitamin_a_iu,
            vitamin_d_iu=self.vitamin_d_iu + other.vitamin_d_iu,
            saturated_fat_g=self.saturated_fat_g + other.saturated_fat_g,
            trans_fat_g=self.trans_fat_g + other.trans_fat_g,
            monounsaturated_fat_g=self.monounsaturated_fat_g + other.monounsaturated_fat_g,
            polyunsaturated_fat_g=self.polyunsaturated_fat_g + other.polyunsaturated_fat_g
        )
    
    def scale(self, factor: float) -> 'NutritionInfo':
        """Scale nutrition info by a factor"""
        return NutritionInfo(
            calories=self.calories * factor,
            protein_g=self.protein_g * factor,
            carbs_g=self.carbs_g * factor,
            fat_g=self.fat_g * factor,
            fiber_g=self.fiber_g * factor,
            sugar_g=self.sugar_g * factor,
            sodium_mg=self.sodium_mg * factor,
            cholesterol_mg=self.cholesterol_mg * factor,
            vitamin_c_mg=self.vitamin_c_mg * factor,
            calcium_mg=self.calcium_mg * factor,
            iron_mg=self.iron_mg * factor,
            potassium_mg=self.potassium_mg * factor,
            vitamin_a_iu=self.vitamin_a_iu * factor,
            vitamin_d_iu=self.vitamin_d_iu * factor,
            saturated_fat_g=self.saturated_fat_g * factor,
            trans_fat_g=self.trans_fat_g * factor,
            monounsaturated_fat_g=self.monounsaturated_fat_g * factor,
            polyunsaturated_fat_g=self.polyunsaturated_fat_g * factor
        )
    
    def per_serving(self, servings: int) -> 'NutritionInfo':
        """Calculate nutrition per serving"""
        if servings <= 0:
            return NutritionInfo()
        return self.scale(1.0 / servings)
    
@dataclass
class DailyNutritionTargets:
    """Daily nutrition targets for analysis"""
    calories: float = 2000.0
    protein_g: float = 50.0
    carbs_g: float = 300.0
    fat_g: float = 65.0
    fiber_g: float = 25.0
    sodium_mg: float = 2300.0
    cholesterol_mg: float = 300.0
    calcium_mg: float = 1000.0
    iron_mg: float = 18.0
    vitamin_c_mg: float = 90.0
    potassium_mg: float = 3500.0
    vitamin_a_iu: float = 5000.0
    vitamin_d_iu: float = 400.0
    saturated_fat_g: float = 20.0

class NutritionCalculator:
    """Calculate and analyze nutritional information"""
    
    def __init__(self):
        """Initialize the nutrition calculator"""
        # Basic nutrition database for common ingredients (per 100g)
        self.ingredient_nutrition_db = self._load_ingredient_nutrition_db()
        
        # Common measurement conversions to grams
        self.measurement_conversions = {
            'cup': 240,  # varies by ingredient, this is for liquids
            'cups': 240,
            'c': 240,
            'tbsp': 15,
            'tablespoon': 15,
            'tablespoons': 15,
            'tsp': 5,
            'teaspoon': 5,
            'teaspoons': 5,
            'oz': 28.35,
            'ounce': 28.35,
            'ounces': 28.35,
            'lb': 453.6,
            'pound': 453.6,
            'pounds': 453.6,
            'lbs': 453.6,
            'g': 1,
            'gram': 1,
            'grams': 1,
            'kg': 1000,
            'kilogram': 1000,
            'kilograms': 1000,
            'ml': 1,  # for water-like density
            'milliliter': 1,
            'milliliters': 1,
            'l': 1000,
            'liter': 1000,
            'liters': 1000,
            'qt': 946,
            'quart': 946,
            'quarts': 946,
            'pt': 473,
            'pint': 473,
            'pints': 473,
            'gal': 3785,
            'gallon': 3785,
            'gallons': 3785,
            'fl oz': 29.57,
            'fluid ounce': 29.57,
            'fluid ounces': 29.57
        }
        
        # Ingredient-specific cup conversions (grams per cup)
        self.ingredient_cup_weights = {
            'flour': 125,
            'all-purpose flour': 125,
            'wheat flour': 125,
            'bread flour': 130,
            'cake flour': 110,
            'sugar': 200,
            'granulated sugar': 200,
            'white sugar': 200,
            'brown sugar': 220,
            'powdered sugar': 120,
            'confectioners sugar': 120,
            'rice': 185,
            'white rice': 185,
            'brown rice': 195,
            'pasta': 100,
            'spaghetti': 100,
            'penne': 100,
            'macaroni': 100,
            'oats': 80,
            'rolled oats': 80,
            'quinoa': 170,
            'couscous': 180,
            'cheese': 113,
            'cheddar cheese': 113,
            'parmesan cheese': 100,
            'mozzarella cheese': 110,
            'butter': 227,
            'margarine': 227,
            'milk': 240,
            'whole milk': 240,
            'skim milk': 240,
            '2% milk': 240,
            'heavy cream': 240,
            'sour cream': 240,
            'yogurt': 245,
            'water': 240,
            'oil': 218,
            'olive oil': 218,
            'vegetable oil': 218,
            'canola oil': 218,
            'coconut oil': 220,
            'honey': 340,
            'maple syrup': 320,
            'corn syrup': 340,
            'nuts': 140,
            'almonds': 140,
            'walnuts': 120,
            'pecans': 110,
            'peanuts': 150,
            'beans': 185,
            'black beans': 185,
            'kidney beans': 185,
            'chickpeas': 200,
            'lentils': 200,
            'breadcrumbs': 100,
            'panko': 50,
            'cocoa powder': 85,
            'chocolate chips': 175,
            'raisins': 165,
            'dates': 150,
            'cranberries': 120
        }
        
        logger.info("Nutrition Calculator initialized")
    
    def _load_ingredient_nutrition_db(self) -> Dict[str, NutritionInfo]:
        """Load comprehensive nutrition database for common ingredients (per 100g)"""
        return {
            # PROTEINS
            'chicken breast': NutritionInfo(165, 31.0, 0, 3.6, 0, 0, 74, 85, 0, 15, 0.9, 256, 21, 0, 1.0, 0, 1.0, 0.8),
            'chicken': NutritionInfo(165, 31.0, 0, 3.6, 0, 0, 74, 85, 0, 15, 0.9, 256, 21, 0, 1.0, 0, 1.0, 0.8),
            'chicken thigh': NutritionInfo(209, 26.0, 0, 10.9, 0, 0, 77, 98, 0, 12, 1.3, 230, 30, 0, 3.0, 0, 4.1, 2.3),
            'chicken drumstick': NutritionInfo(172, 28.3, 0, 5.7, 0, 0, 81, 90, 0, 13, 1.1, 240, 25, 0, 1.6, 0, 2.0, 1.2),
            'beef': NutritionInfo(250, 26.0, 0, 15.0, 0, 0, 72, 90, 0, 18, 2.6, 318, 0, 0, 6.2, 0, 6.3, 0.6),
            'ground beef': NutritionInfo(254, 26.1, 0, 15.7, 0, 0, 66, 88, 0, 18, 2.5, 289, 0, 0, 6.2, 0.7, 6.8, 0.6),
            'lean ground beef': NutritionInfo(215, 26.8, 0, 11.3, 0, 0, 70, 78, 0, 21, 2.3, 330, 0, 0, 4.5, 0.4, 4.9, 0.4),
            'beef steak': NutritionInfo(271, 25.4, 0, 18.6, 0, 0, 59, 89, 0, 17, 2.8, 300, 0, 0, 7.3, 0.7, 8.0, 0.7),
            'pork': NutritionInfo(242, 27.3, 0, 13.9, 0, 0, 62, 80, 0, 19, 0.9, 423, 0, 0, 4.9, 0, 6.2, 1.5),
            'pork chop': NutritionInfo(231, 25.7, 0, 13.4, 0, 0, 53, 71, 0.7, 26, 0.7, 372, 0, 0, 4.5, 0, 6.0, 1.4),
            'bacon': NutritionInfo(541, 37.0, 1.4, 41.8, 0, 0, 1717, 110, 0, 11, 1.4, 565, 0, 44, 13.9, 0.1, 19.4, 4.5),
            'ham': NutritionInfo(145, 21.0, 1.5, 5.5, 0, 0, 1203, 57, 0, 6, 0.8, 287, 0, 0, 1.8, 0, 2.6, 0.6),
            'salmon': NutritionInfo(208, 20.0, 0, 12.0, 0, 0, 59, 55, 0, 13, 0.8, 363, 149, 11, 3.2, 0, 3.8, 2.3),
            'tuna': NutritionInfo(144, 23.3, 0, 4.9, 0, 0, 39, 38, 0, 8, 1.0, 252, 655, 154, 1.3, 0, 1.4, 1.3),
            'cod': NutritionInfo(82, 17.8, 0, 0.7, 0, 0, 54, 37, 1, 16, 0.4, 413, 36, 0, 0.1, 0, 0.1, 0.2),
            'shrimp': NutritionInfo(85, 20.1, 0.2, 0.5, 0, 0, 111, 152, 0, 70, 0.2, 182, 180, 0, 0.1, 0, 0.1, 0.2),
            'eggs': NutritionInfo(155, 13.0, 1.1, 11.0, 0, 1.1, 124, 372, 0, 50, 1.8, 126, 487, 87, 3.1, 0, 4.1, 1.9),
            'egg whites': NutritionInfo(52, 10.9, 0.7, 0.2, 0, 0.7, 166, 0, 0, 7, 0.1, 163, 0, 0, 0, 0, 0, 0.1),
            'tofu': NutritionInfo(76, 8.0, 1.9, 4.8, 0.3, 0.7, 7, 0, 0.1, 350, 5.4, 121, 85, 0, 0.7, 0, 1.1, 2.7),
            'tempeh': NutritionInfo(190, 19.0, 9.4, 11.0, 0, 0, 9, 0, 0, 111, 2.7, 412, 0, 0, 2.3, 0, 3.2, 6.4),
            'quinoa': NutritionInfo(120, 4.4, 22.0, 1.9, 2.8, 0.9, 5, 0, 0, 17, 1.5, 172, 5, 0, 0.2, 0, 0.5, 0.9),
            
            # DAIRY PRODUCTS
            'milk': NutritionInfo(42, 3.4, 5.0, 1.0, 0, 5.0, 44, 5, 0, 113, 0.0, 132, 126, 1.3, 0.6, 0, 0.3, 0.0),
            'whole milk': NutritionInfo(61, 3.2, 4.8, 3.3, 0, 4.8, 43, 12, 0, 113, 0.0, 132, 162, 1.3, 1.9, 0, 0.8, 0.1),
            'skim milk': NutritionInfo(34, 3.4, 5.0, 0.2, 0, 5.0, 44, 2, 0, 122, 0.0, 144, 204, 0, 0.1, 0, 0.0, 0.0),
            '2% milk': NutritionInfo(50, 3.3, 4.9, 2.0, 0, 4.9, 44, 8, 0, 116, 0.0, 140, 204, 1.1, 1.2, 0, 0.5, 0.1),
            'cheese': NutritionInfo(113, 7.0, 1.0, 9.0, 0, 1.0, 186, 27, 0, 184, 0.1, 76, 240, 0, 5.9, 0, 2.4, 0.2),
            'cheddar cheese': NutritionInfo(403, 25.0, 1.3, 33.0, 0, 0.5, 621, 105, 0, 721, 0.7, 98, 1242, 0, 21.1, 0, 9.4, 0.9),
            'mozzarella cheese': NutritionInfo(280, 28.0, 2.2, 17.0, 0, 1.0, 627, 79, 0, 731, 0.4, 95, 676, 0, 10.1, 0, 4.6, 0.5),
            'parmesan cheese': NutritionInfo(431, 38.5, 4.1, 29.0, 0, 0.9, 1529, 88, 0, 1184, 0.8, 92, 701, 0, 17.3, 0, 7.7, 0.7),
            'cottage cheese': NutritionInfo(98, 11.1, 3.4, 4.3, 0, 2.7, 364, 9, 0, 83, 0.1, 104, 95, 0, 2.7, 0, 1.2, 0.1),
            'cream cheese': NutritionInfo(342, 6.2, 4.1, 34.0, 0, 3.2, 321, 105, 0, 98, 1.2, 138, 1427, 0, 21.4, 0, 9.6, 1.3),
            'butter': NutritionInfo(717, 0.9, 0.1, 81.0, 0, 0.1, 11, 215, 0, 24, 0.0, 24, 2499, 0, 51.4, 3.3, 21.0, 3.0),
            'margarine': NutritionInfo(717, 0.9, 0.9, 80.0, 0, 0.0, 943, 0, 0, 20, 0.0, 5, 3324, 0, 16.7, 2.8, 35.5, 21.6),
            'yogurt': NutritionInfo(59, 10.0, 3.6, 0.4, 0, 3.2, 36, 5, 0, 110, 0.1, 141, 27, 0, 0.3, 0, 0.1, 0.0),
            'greek yogurt': NutritionInfo(97, 9.0, 4.0, 5.0, 0, 4.0, 35, 10, 0, 115, 0.1, 141, 99, 0, 3.2, 0, 1.4, 0.1),
            'heavy cream': NutritionInfo(345, 2.1, 2.8, 37.0, 0, 2.8, 28, 109, 0, 65, 0.0, 75, 1470, 0, 23.0, 0, 10.7, 1.4),
            'sour cream': NutritionInfo(193, 2.4, 4.6, 19.0, 0, 4.1, 78, 52, 0.9, 14, 0.1, 141, 790, 0, 12.0, 0, 5.5, 0.7),
            
            # GRAINS AND STARCHES
            'rice': NutritionInfo(130, 2.7, 28.0, 0.3, 0.4, 0.1, 1, 0, 0, 10, 0.8, 35, 0, 0, 0.1, 0, 0.1, 0.1),
            'white rice': NutritionInfo(130, 2.7, 28.0, 0.3, 0.4, 0.1, 1, 0, 0, 10, 0.8, 35, 0, 0, 0.1, 0, 0.1, 0.1),
            'brown rice': NutritionInfo(111, 2.6, 22.0, 0.9, 1.8, 0.4, 5, 0, 0, 12, 0.4, 43, 0, 0, 0.2, 0, 0.3, 0.3),
            'wild rice': NutritionInfo(101, 4.0, 21.3, 0.3, 1.8, 0.7, 3, 0, 0, 3, 0.6, 101, 0, 0, 0.1, 0, 0.1, 0.1),
            'pasta': NutritionInfo(131, 5.0, 25.0, 1.1, 1.8, 0.6, 1, 0, 0, 7, 0.9, 44, 0, 0, 0.2, 0, 0.4, 0.4),
            'whole wheat pasta': NutritionInfo(124, 5.4, 25.4, 1.1, 3.7, 0.8, 4, 0, 0, 15, 1.5, 95, 0, 0, 0.2, 0, 0.4, 0.4),
            'spaghetti': NutritionInfo(131, 5.0, 25.0, 1.1, 1.8, 0.6, 1, 0, 0, 7, 0.9, 44, 0, 0, 0.2, 0, 0.4, 0.4),
            'penne': NutritionInfo(131, 5.0, 25.0, 1.1, 1.8, 0.6, 1, 0, 0, 7, 0.9, 44, 0, 0, 0.2, 0, 0.4, 0.4),
            'macaroni': NutritionInfo(131, 5.0, 25.0, 1.1, 1.8, 0.6, 1, 0, 0, 7, 0.9, 44, 0, 0, 0.2, 0, 0.4, 0.4),
            'bread': NutritionInfo(265, 9.0, 49.0, 3.2, 2.7, 5.0, 491, 0, 0, 149, 3.6, 115, 0, 0, 0.7, 0, 1.1, 1.2),
            'white bread': NutritionInfo(265, 9.0, 49.0, 3.2, 2.7, 5.0, 491, 0, 0, 149, 3.6, 115, 0, 0, 0.7, 0, 1.1, 1.2),
            'whole wheat bread': NutritionInfo(247, 13.2, 41.0, 4.2, 7.0, 5.7, 396, 0, 0, 107, 2.5, 248, 0, 0, 0.8, 0, 1.5, 1.7),
            'sourdough bread': NutritionInfo(289, 11.7, 56.0, 2.1, 2.4, 4.7, 590, 0, 0, 56, 2.8, 124, 0, 0, 0.5, 0, 0.7, 0.8),
            'oats': NutritionInfo(389, 16.9, 66.3, 6.9, 10.6, 0.0, 2, 0, 0, 54, 4.7, 429, 0, 0, 1.2, 0, 2.2, 2.5),
            'rolled oats': NutritionInfo(389, 16.9, 66.3, 6.9, 10.6, 0.0, 2, 0, 0, 54, 4.7, 429, 0, 0, 1.2, 0, 2.2, 2.5),
            'quinoa': NutritionInfo(368, 14.1, 64.2, 6.1, 7.0, 0, 5, 0, 0, 47, 4.6, 563, 5, 0, 0.7, 0, 1.6, 3.6),
            'barley': NutritionInfo(354, 12.5, 73.5, 2.3, 17.3, 0.8, 12, 0, 0, 33, 3.6, 452, 22, 0, 0.5, 0, 0.4, 1.1),
            'flour': NutritionInfo(364, 10.3, 76.3, 1.0, 2.7, 0.3, 2, 0, 0, 15, 1.2, 107, 0, 0, 0.2, 0, 0.3, 0.4),
            'all-purpose flour': NutritionInfo(364, 10.3, 76.3, 1.0, 2.7, 0.3, 2, 0, 0, 15, 1.2, 107, 0, 0, 0.2, 0, 0.3, 0.4),
            'whole wheat flour': NutritionInfo(340, 13.7, 72.0, 2.5, 10.7, 0.4, 2, 0, 0, 34, 3.9, 405, 9, 0, 0.4, 0, 0.8, 1.2),
            'bread flour': NutritionInfo(361, 12.9, 74.9, 1.7, 2.4, 0.7, 3, 0, 0, 19, 1.7, 130, 0, 0, 0.3, 0, 0.5, 0.7),
            
            # VEGETABLES
            'tomato': NutritionInfo(18, 0.9, 3.9, 0.2, 1.2, 2.6, 5, 0, 13.7, 10, 0.3, 237, 833, 0, 0.0, 0, 0.0, 0.1),
            'tomatoes': NutritionInfo(18, 0.9, 3.9, 0.2, 1.2, 2.6, 5, 0, 13.7, 10, 0.3, 237, 833, 0, 0.0, 0, 0.0, 0.1),
            'cherry tomatoes': NutritionInfo(18, 0.9, 3.9, 0.2, 1.2, 2.6, 5, 0, 13.7, 10, 0.3, 237, 833, 0, 0.0, 0, 0.0, 0.1),
            'roma tomatoes': NutritionInfo(18, 0.9, 3.9, 0.2, 1.2, 2.6, 5, 0, 13.7, 10, 0.3, 237, 833, 0, 0.0, 0, 0.0, 0.1),
            'onion': NutritionInfo(40, 1.1, 9.3, 0.1, 1.7, 4.2, 4, 0, 7.4, 23, 0.2, 146, 2, 0, 0.0, 0, 0.0, 0.0),
            'onions': NutritionInfo(40, 1.1, 9.3, 0.1, 1.7, 4.2, 4, 0, 7.4, 23, 0.2, 146, 2, 0, 0.0, 0, 0.0, 0.0),
            'red onion': NutritionInfo(40, 1.1, 9.3, 0.1, 1.7, 4.2, 4, 0, 7.4, 23, 0.2, 146, 2, 0, 0.0, 0, 0.0, 0.0),
            'yellow onion': NutritionInfo(40, 1.1, 9.3, 0.1, 1.7, 4.2, 4, 0, 7.4, 23, 0.2, 146, 2, 0, 0.0, 0, 0.0, 0.0),
            'white onion': NutritionInfo(40, 1.1, 9.3, 0.1, 1.7, 4.2, 4, 0, 7.4, 23, 0.2, 146, 2, 0, 0.0, 0, 0.0, 0.0),
            'garlic': NutritionInfo(149, 6.4, 33.1, 0.5, 2.1, 1.0, 17, 0, 31.2, 181, 1.7, 401, 9, 0, 0.1, 0, 0.0, 0.2),
            'garlic cloves': NutritionInfo(149, 6.4, 33.1, 0.5, 2.1, 1.0, 17, 0, 31.2, 181, 1.7, 401, 9, 0, 0.1, 0, 0.0, 0.2),
            'carrot': NutritionInfo(41, 0.9, 9.6, 0.2, 2.8, 4.7, 69, 0, 5.9, 33, 0.3, 320, 16706, 0, 0.0, 0, 0.0, 0.1),
            'carrots': NutritionInfo(41, 0.9, 9.6, 0.2, 2.8, 4.7, 69, 0, 5.9, 33, 0.3, 320, 16706, 0, 0.0, 0, 0.0, 0.1),
            'baby carrots': NutritionInfo(41, 0.9, 9.6, 0.2, 2.8, 4.7, 69, 0, 5.9, 33, 0.3, 320, 16706, 0, 0.0, 0, 0.0, 0.1),
            'broccoli': NutritionInfo(34, 2.8, 6.6, 0.4, 2.6, 1.5, 33, 0, 89.2, 47, 0.7, 316, 623, 0, 0.1, 0, 0.1, 0.1),
            'spinach': NutritionInfo(23, 2.9, 3.6, 0.4, 2.2, 0.4, 79, 0, 28.1, 99, 2.7, 558, 9377, 0, 0.1, 0, 0.1, 0.1),
            'lettuce': NutritionInfo(15, 1.4, 2.9, 0.2, 1.3, 0.8, 28, 0, 9.2, 36, 0.9, 194, 7405, 0, 0.0, 0, 0.0, 0.1),
            'romaine lettuce': NutritionInfo(17, 1.2, 3.3, 0.3, 2.1, 1.2, 8, 0, 4.0, 33, 1.0, 247, 8710, 0, 0.1, 0, 0.0, 0.1),
            'cucumber': NutritionInfo(16, 0.7, 4.0, 0.1, 0.5, 1.7, 2, 0, 2.8, 16, 0.3, 147, 105, 0, 0.0, 0, 0.0, 0.0),
            'bell pepper': NutritionInfo(31, 1.0, 7.3, 0.3, 2.5, 4.2, 4, 0, 127.7, 7, 0.4, 211, 3131, 0, 0.1, 0, 0.0, 0.1),
            'red bell pepper': NutritionInfo(31, 1.0, 7.3, 0.3, 2.5, 4.2, 4, 0, 127.7, 7, 0.4, 211, 3131, 0, 0.1, 0, 0.0, 0.1),
            'green bell pepper': NutritionInfo(20, 0.9, 4.6, 0.2, 1.7, 2.4, 3, 0, 80.4, 10, 0.3, 175, 370, 0, 0.0, 0, 0.0, 0.1),
            'mushrooms': NutritionInfo(22, 3.1, 3.3, 0.3, 1.0, 2.0, 5, 0, 2.1, 3, 0.5, 318, 0, 7, 0.1, 0, 0.0, 0.1),
            'celery': NutritionInfo(14, 0.7, 3.0, 0.2, 1.6, 1.3, 80, 0, 3.1, 40, 0.2, 260, 449, 0, 0.0, 0, 0.0, 0.0),
            'zucchini': NutritionInfo(17, 1.2, 3.1, 0.3, 1.0, 2.5, 8, 0, 17.9, 16, 0.4, 261, 200, 0, 0.1, 0, 0.1, 0.1),
            'eggplant': NutritionInfo(25, 1.0, 5.9, 0.2, 3.0, 3.5, 2, 0, 2.2, 9, 0.2, 229, 23, 0, 0.0, 0, 0.0, 0.1),
            'potatoes': NutritionInfo(77, 2.0, 17.5, 0.1, 2.2, 0.8, 6, 0, 19.7, 12, 0.8, 425, 2, 0, 0.0, 0, 0.0, 0.0),
            'sweet potato': NutritionInfo(86, 1.6, 20.1, 0.1, 3.0, 4.2, 54, 0, 2.4, 30, 0.6, 337, 14187, 0, 0.0, 0, 0.0, 0.0),
            'corn': NutritionInfo(86, 3.3, 19.0, 1.4, 2.7, 3.2, 35, 0, 6.8, 2, 0.5, 270, 187, 0, 0.2, 0, 0.4, 0.6),
            'peas': NutritionInfo(81, 5.4, 14.5, 0.4, 5.7, 5.7, 5, 0, 40.0, 25, 1.5, 244, 765, 0, 0.1, 0, 0.1, 0.2),
            'green beans': NutritionInfo(31, 1.8, 7.0, 0.2, 2.7, 3.3, 6, 0, 12.2, 37, 1.0, 211, 690, 0, 0.0, 0, 0.0, 0.1),
            'asparagus': NutritionInfo(20, 2.2, 3.9, 0.1, 2.1, 1.9, 2, 0, 5.6, 24, 2.1, 202, 756, 0, 0.0, 0, 0.0, 0.1),
            'cauliflower': NutritionInfo(25, 1.9, 5.0, 0.3, 2.0, 1.9, 30, 0, 48.2, 22, 0.4, 299, 13, 0, 0.1, 0, 0.1, 0.1),
            'cabbage': NutritionInfo(25, 1.3, 5.8, 0.1, 2.5, 3.2, 18, 0, 36.6, 40, 0.5, 170, 98, 0, 0.0, 0, 0.0, 0.0),
            
            # FRUITS
            'apple': NutritionInfo(52, 0.3, 13.8, 0.2, 2.4, 10.4, 1, 0, 4.6, 6, 0.1, 107, 54, 0, 0.0, 0, 0.1, 0.1),
            'apples': NutritionInfo(52, 0.3, 13.8, 0.2, 2.4, 10.4, 1, 0, 4.6, 6, 0.1, 107, 54, 0, 0.0, 0, 0.1, 0.1),
            'banana': NutritionInfo(89, 1.1, 22.8, 0.3, 2.6, 12.2, 1, 0, 8.7, 5, 0.3, 358, 64, 0, 0.1, 0, 0.1, 0.1),
            'bananas': NutritionInfo(89, 1.1, 22.8, 0.3, 2.6, 12.2, 1, 0, 8.7, 5, 0.3, 358, 64, 0, 0.1, 0, 0.1, 0.1),
            'orange': NutritionInfo(47, 0.9, 11.8, 0.1, 2.4, 9.4, 0, 0, 53.2, 40, 0.1, 181, 225, 0, 0.0, 0, 0.0, 0.0),
            'oranges': NutritionInfo(47, 0.9, 11.8, 0.1, 2.4, 9.4, 0, 0, 53.2, 40, 0.1, 181, 225, 0, 0.0, 0, 0.0, 0.0),
            'lemon': NutritionInfo(29, 1.1, 9.3, 0.3, 4.7, 1.5, 2, 0, 53.0, 26, 0.6, 138, 22, 0, 0.1, 0, 0.1, 0.1),
            'lemons': NutritionInfo(29, 1.1, 9.3, 0.3, 4.7, 1.5, 2, 0, 53.0, 26, 0.6, 138, 22, 0, 0.1, 0, 0.1, 0.1),
            'lime': NutritionInfo(30, 0.7, 10.5, 0.2, 2.8, 1.7, 2, 0, 29.1, 33, 0.6, 102, 50, 0, 0.0, 0, 0.0, 0.1),
            'strawberry': NutritionInfo(32, 0.7, 7.7, 0.3, 2.0, 4.9, 1, 0, 58.8, 16, 0.4, 153, 12, 0, 0.1, 0, 0.0, 0.1),
            'strawberries': NutritionInfo(32, 0.7, 7.7, 0.3, 2.0, 4.9, 1, 0, 58.8, 16, 0.4, 153, 12, 0, 0.1, 0, 0.0, 0.1),
            'blueberry': NutritionInfo(57, 0.7, 14.5, 0.3, 2.4, 10.0, 1, 0, 9.7, 6, 0.3, 77, 54, 0, 0.1, 0, 0.0, 0.1),
            'blueberries': NutritionInfo(57, 0.7, 14.5, 0.3, 2.4, 10.0, 1, 0, 9.7, 6, 0.3, 77, 54, 0, 0.1, 0, 0.0, 0.1),
            'raspberry': NutritionInfo(52, 1.2, 11.9, 0.7, 6.5, 4.4, 1, 0, 26.2, 25, 0.7, 151, 33, 0, 0.1, 0, 0.1, 0.4),
            'raspberries': NutritionInfo(52, 1.2, 11.9, 0.7, 6.5, 4.4, 1, 0, 26.2, 25, 0.7, 151, 33, 0, 0.1, 0, 0.1, 0.4),
            'blackberry': NutritionInfo(43, 1.4, 9.6, 0.5, 5.3, 4.9, 1, 0, 21.0, 29, 0.6, 162, 214, 0, 0.1, 0, 0.0, 0.3),
            'blackberries': NutritionInfo(43, 1.4, 9.6, 0.5, 5.3, 4.9, 1, 0, 21.0, 29, 0.6, 162, 214, 0, 0.1, 0, 0.0, 0.3),
            'grapes': NutritionInfo(62, 0.6, 16.0, 0.2, 0.9, 15.5, 2, 0, 3.2, 10, 0.4, 191, 66, 0, 0.1, 0, 0.0, 0.1),
            'avocado': NutritionInfo(160, 2.0, 8.5, 14.7, 6.7, 0.7, 7, 0, 10.0, 12, 0.6, 485, 146, 0, 2.1, 0, 9.8, 1.8),
            'mango': NutritionInfo(60, 0.8, 15.0, 0.4, 1.6, 13.7, 1, 0, 36.4, 11, 0.2, 168, 1082, 0, 0.1, 0, 0.1, 0.1),
            'pineapple': NutritionInfo(50, 0.5, 13.1, 0.1, 1.4, 9.9, 1, 0, 47.8, 13, 0.3, 109, 58, 0, 0.0, 0, 0.0, 0.0),
            'watermelon': NutritionInfo(30, 0.6, 7.6, 0.2, 0.4, 6.2, 1, 0, 8.1, 7, 0.2, 112, 569, 0, 0.1, 0, 0.0, 0.1),
            'cantaloupe': NutritionInfo(34, 0.8, 8.2, 0.2, 0.9, 7.9, 16, 0, 36.7, 9, 0.2, 267, 3382, 0, 0.0, 0, 0.0, 0.1),
            'honeydew': NutritionInfo(36, 0.5, 9.1, 0.1, 0.8, 8.1, 18, 0, 18.0, 6, 0.1, 228, 50, 0, 0.0, 0, 0.0, 0.0),
            
            # NUTS AND SEEDS
            'almonds': NutritionInfo(579, 21.2, 21.6, 49.9, 12.5, 4.4, 1, 0, 0, 269, 3.7, 733, 2, 0, 3.8, 0, 31.6, 12.3),
            'walnuts': NutritionInfo(654, 15.2, 13.7, 65.2, 6.7, 2.6, 2, 0, 1.3, 98, 2.9, 441, 20, 0, 6.1, 0, 8.9, 47.2),
            'pecans': NutritionInfo(691, 9.2, 13.9, 72.0, 9.6, 4.0, 0, 0, 1.1, 70, 2.5, 410, 56, 0, 6.2, 0, 40.8, 21.6),
            'cashews': NutritionInfo(553, 18.2, 30.2, 43.9, 3.3, 5.9, 12, 0, 0.5, 37, 6.7, 660, 0, 0, 7.8, 0, 23.8, 7.8),
            'peanuts': NutritionInfo(567, 25.8, 16.1, 49.2, 8.5, 4.7, 18, 0, 0, 92, 4.6, 705, 0, 0, 6.3, 0, 24.4, 15.6),
            'pistachios': NutritionInfo(560, 20.2, 27.2, 45.3, 10.6, 7.7, 1, 0, 5.6, 105, 3.9, 1025, 515, 0, 5.6, 0, 23.3, 13.5),
            'sunflower seeds': NutritionInfo(584, 20.8, 20.0, 51.5, 8.6, 2.6, 9, 0, 1.4, 78, 5.2, 645, 50, 0, 4.5, 0, 18.5, 23.1),
            'pumpkin seeds': NutritionInfo(559, 30.2, 10.7, 49.1, 6.0, 1.4, 7, 0, 1.9, 46, 8.8, 809, 16, 0, 9.5, 0, 16.2, 20.6),
            'sesame seeds': NutritionInfo(573, 17.7, 23.4, 49.7, 11.8, 0.3, 11, 0, 0, 975, 14.6, 468, 9, 0, 6.2, 0, 18.8, 21.8),
            'chia seeds': NutritionInfo(486, 16.5, 42.1, 30.7, 34.4, 0, 16, 0, 1.6, 631, 7.7, 407, 54, 0, 3.3, 0, 2.3, 23.7),
            'flax seeds': NutritionInfo(534, 18.3, 28.9, 42.2, 27.3, 1.6, 30, 0, 0.6, 255, 5.7, 813, 0, 0, 3.7, 0, 7.5, 28.7),
            
            # BEANS AND LEGUMES
            'black beans': NutritionInfo(132, 8.9, 23.7, 0.5, 8.7, 0.3, 2, 0, 0, 27, 2.1, 355, 6, 0, 0.1, 0, 0.1, 0.3),
            'kidney beans': NutritionInfo(127, 8.7, 22.8, 0.5, 7.4, 0.3, 2, 0, 1.2, 28, 2.9, 403, 0, 0, 0.1, 0, 0.1, 0.3),
            'chickpeas': NutritionInfo(164, 8.9, 27.4, 2.6, 7.6, 4.8, 7, 0, 1.3, 49, 2.9, 291, 67, 0, 0.3, 0, 0.6, 1.2),
            'lentils': NutritionInfo(116, 9.0, 20.1, 0.4, 7.9, 1.8, 2, 0, 1.5, 19, 3.3, 369, 8, 0, 0.1, 0, 0.1, 0.2),
            'pinto beans': NutritionInfo(143, 9.0, 26.2, 0.7, 9.0, 0.3, 1, 0, 0.8, 46, 2.1, 436, 0, 0, 0.1, 0, 0.1, 0.4),
            'navy beans': NutritionInfo(140, 8.2, 26.1, 0.6, 10.5, 0.3, 2, 0, 0.2, 52, 2.4, 389, 0, 0, 0.1, 0, 0.1, 0.3),
            'lima beans': NutritionInfo(115, 7.8, 20.9, 0.4, 7.0, 2.9, 2, 0, 0, 17, 2.4, 508, 0, 0, 0.1, 0, 0.1, 0.2),
            'soybeans': NutritionInfo(173, 16.6, 9.9, 9.0, 6.0, 3.0, 2, 0, 29.0, 197, 15.7, 797, 9, 0, 1.3, 0, 1.9, 5.1),
            'edamame': NutritionInfo(121, 11.9, 8.9, 5.2, 5.2, 2.2, 6, 0, 6.1, 63, 2.3, 436, 154, 0, 0.6, 0, 1.3, 2.3),
            'peas': NutritionInfo(81, 5.4, 14.5, 0.4, 5.7, 5.7, 5, 0, 40.0, 25, 1.5, 244, 765, 0, 0.1, 0, 0.1, 0.2),
            
            # FATS AND OILS
            'olive oil': NutritionInfo(884, 0, 0, 100.0, 0, 0, 2, 0, 0, 1, 0.6, 1, 0, 0, 13.8, 0, 73.0, 10.5),
            'oil': NutritionInfo(884, 0, 0, 100.0, 0, 0, 2, 0, 0, 1, 0.6, 1, 0, 0, 13.8, 0, 73.0, 10.5),
            'vegetable oil': NutritionInfo(884, 0, 0, 100.0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0, 15.7, 0.1, 22.8, 57.9),
            'canola oil': NutritionInfo(884, 0, 0, 100.0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0, 7.4, 0.1, 63.3, 28.1),
            'coconut oil': NutritionInfo(862, 0, 0, 100.0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0, 82.5, 0, 6.3, 1.7),
            'sesame oil': NutritionInfo(884, 0, 0, 100.0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0, 14.2, 0, 39.7, 41.7),
            'avocado oil': NutritionInfo(884, 0, 0, 100.0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0, 11.6, 0, 70.6, 13.5),
            
            # CONDIMENTS AND SEASONINGS
            'salt': NutritionInfo(0, 0, 0, 0, 0, 0, 38758, 0, 0, 24, 0.3, 8, 0, 0, 0, 0, 0, 0),
            'pepper': NutritionInfo(251, 10.4, 63.9, 3.3, 25.3, 0.6, 20, 0, 0, 443, 9.7, 1329, 547, 0, 1.4, 0, 0.7, 0.8),
            'black pepper': NutritionInfo(251, 10.4, 63.9, 3.3, 25.3, 0.6, 20, 0, 0, 443, 9.7, 1329, 547, 0, 1.4, 0, 0.7, 0.8),
            'soy sauce': NutritionInfo(8, 1.3, 0.8, 0.0, 0.1, 0.4, 5493, 0, 0, 3, 0.4, 37, 0, 0, 0.0, 0, 0.0, 0.0),
            'vinegar': NutritionInfo(18, 0, 0.0, 0, 0, 0, 5, 0, 0, 6, 0.2, 2, 0, 0, 0, 0, 0, 0),
            'balsamic vinegar': NutritionInfo(88, 0.5, 17.0, 0, 0, 12.0, 23, 0, 0, 27, 0.7, 112, 0, 0, 0, 0, 0, 0),
            'apple cider vinegar': NutritionInfo(22, 0, 0.9, 0, 0, 0.4, 5, 0, 0, 7, 0.2, 73, 0, 0, 0, 0, 0, 0),
            'mustard': NutritionInfo(66, 3.7, 5.8, 3.3, 3.2, 1.3, 1135, 0, 0.7, 58, 1.8, 138, 138, 0, 0.2, 0, 2.0, 0.8),
            'ketchup': NutritionInfo(112, 1.7, 25.8, 0.3, 0.4, 22.8, 1110, 0, 4.1, 18, 0.4, 281, 1019, 0, 0.1, 0, 0.1, 0.1),
            'mayonnaise': NutritionInfo(680, 1.0, 0.6, 75.0, 0, 0.3, 504, 60, 0, 19, 0.2, 19, 252, 0, 10.9, 0, 22.6, 39.8),
            'hot sauce': NutritionInfo(12, 1.3, 0.8, 0.8, 1.4, 0.5, 568, 0, 7.1, 15, 0.9, 145, 2970, 0, 0.1, 0, 0.1, 0.4),
            'worcestershire sauce': NutritionInfo(78, 0, 19.5, 0, 0, 0, 1305, 0, 0, 22, 0.9, 136, 0, 0, 0, 0, 0, 0),
            'honey': NutritionInfo(304, 0.3, 82.4, 0, 0.2, 82.1, 4, 0, 0.5, 6, 0.4, 52, 0, 0, 0, 0, 0, 0),
            'maple syrup': NutritionInfo(260, 0, 67.0, 0.1, 0, 60.0, 12, 0, 0, 102, 0.1, 204, 0, 0, 0.0, 0, 0.0, 0.0),
            'sugar': NutritionInfo(387, 0, 100.0, 0, 0, 99.8, 1, 0, 0, 2, 0.0, 2, 0, 0, 0, 0, 0, 0),
            'brown sugar': NutritionInfo(380, 0, 98.1, 0, 0, 97.0, 28, 0, 0, 83, 0.7, 346, 0, 0, 0, 0, 0, 0),
            
            # HERBS AND SPICES
            'basil': NutritionInfo(22, 3.2, 2.6, 0.6, 1.6, 0.3, 4, 0, 18.0, 177, 3.2, 295, 5275, 0, 0.0, 0, 0.0, 0.4),
            'oregano': NutritionInfo(265, 9.0, 68.9, 4.3, 42.5, 4.1, 25, 0, 2.3, 1597, 36.8, 1260, 1007, 0, 1.6, 0, 0.9, 1.4),
            'thyme': NutritionInfo(101, 5.6, 24.5, 1.7, 14.0, 1.7, 9, 0, 160.0, 405, 17.5, 609, 1895, 0, 0.5, 0, 0.1, 0.5),
            'rosemary': NutritionInfo(131, 3.3, 20.7, 5.9, 14.1, 0, 26, 0, 21.8, 317, 6.7, 668, 2924, 0, 2.8, 0, 0.9, 1.2),
            'sage': NutritionInfo(315, 10.6, 60.7, 12.8, 40.3, 1.7, 11, 0, 32.4, 1652, 28.1, 1070, 5900, 0, 2.2, 0, 2.2, 7.0),
            'parsley': NutritionInfo(36, 3.0, 6.3, 0.8, 3.3, 0.9, 56, 0, 133.0, 138, 6.2, 554, 8424, 0, 0.1, 0, 0.1, 0.4),
            'cilantro': NutritionInfo(23, 2.1, 3.7, 0.5, 2.8, 0.9, 46, 0, 27.0, 67, 1.8, 521, 6748, 0, 0.0, 0, 0.0, 0.3),
            'dill': NutritionInfo(43, 3.5, 7.0, 1.1, 2.1, 0, 61, 0, 85.0, 208, 6.6, 738, 7717, 0, 0.1, 0, 0.1, 0.8),
            'mint': NutritionInfo(70, 3.8, 14.9, 0.9, 8.0, 0, 31, 0, 31.8, 243, 5.1, 569, 4248, 0, 0.2, 0, 0.1, 0.5),
            'ginger': NutritionInfo(80, 1.8, 17.8, 0.8, 2.0, 1.7, 13, 0, 5.0, 16, 0.6, 415, 0, 0, 0.2, 0, 0.2, 0.2),
            'turmeric': NutritionInfo(354, 7.8, 64.9, 9.9, 21.1, 3.2, 38, 0, 25.9, 183, 41.4, 2525, 0, 0, 1.8, 0, 1.7, 5.1),
            'cumin': NutritionInfo(375, 17.8, 44.2, 22.3, 10.5, 2.3, 168, 0, 7.7, 931, 66.4, 1788, 1270, 0, 1.5, 0, 14.0, 3.3),
            'paprika': NutritionInfo(282, 14.1, 53.9, 12.9, 34.9, 10.3, 68, 0, 190.0, 229, 21.1, 2280, 52540, 0, 2.1, 0, 1.8, 7.5),
            'cinnamon': NutritionInfo(247, 4.0, 80.6, 1.2, 53.1, 2.2, 10, 0, 3.8, 1002, 8.3, 431, 295, 0, 0.1, 0, 0.2, 0.1),
            'nutmeg': NutritionInfo(525, 5.8, 49.3, 36.3, 20.8, 28.5, 16, 0, 3.0, 184, 3.0, 350, 102, 0, 25.9, 0, 4.6, 0.3),
            'cloves': NutritionInfo(274, 6.0, 65.5, 13.0, 33.9, 2.4, 243, 0, 0.2, 632, 11.8, 1020, 530, 0, 4.0, 0, 1.4, 6.8),
            
            # BAKING INGREDIENTS
            'baking powder': NutritionInfo(53, 0, 27.7, 0, 0.2, 0, 10973, 0, 0, 5876, 0.0, 471, 0, 0, 0, 0, 0, 0),
            'baking soda': NutritionInfo(0, 0, 0, 0, 0, 0, 27360, 0, 0, 0, 0.0, 0, 0, 0, 0, 0, 0, 0),
            'vanilla extract': NutritionInfo(288, 0.1, 12.7, 0.1, 0, 12.7, 9, 0, 0, 11, 0.1, 148, 0, 0, 0.0, 0, 0.0, 0.0),
            'cocoa powder': NutritionInfo(228, 19.6, 57.9, 13.7, 33.2, 1.8, 21, 0, 0, 128, 13.9, 1524, 0, 0, 8.1, 0, 4.6, 0.4),
            'chocolate chips': NutritionInfo(479, 4.2, 69.0, 24.5, 4.5, 60.3, 5, 0, 0, 40, 2.8, 222, 13, 0, 14.6, 0, 7.8, 0.8),
            'dark chocolate': NutritionInfo(546, 4.9, 61.3, 31.3, 7.0, 47.9, 7, 0, 0, 35, 6.3, 365, 50, 0, 18.5, 0, 9.8, 1.1),
            'yeast': NutritionInfo(325, 45.0, 36.0, 7.6, 27.0, 0, 51, 0, 0, 30, 2.2, 955, 0, 0, 2.0, 0, 1.0, 3.0),
            
            # BEVERAGES (per 100ml)
            'coffee': NutritionInfo(1, 0.1, 0, 0, 0, 0, 2, 0, 0, 2, 0.0, 49, 0, 0, 0, 0, 0, 0),
            'tea': NutritionInfo(1, 0, 0.3, 0, 0, 0, 1, 0, 0, 0, 0.0, 8, 0, 0, 0, 0, 0, 0),
            'wine': NutritionInfo(83, 0.1, 2.6, 0, 0, 0.6, 4, 0, 0, 8, 0.3, 71, 0, 0, 0, 0, 0, 0),
            'beer': NutritionInfo(43, 0.5, 3.6, 0, 0, 0, 4, 0, 0, 4, 0.0, 27, 0, 0, 0, 0, 0, 0),
            
            # MISCELLANEOUS
            'breadcrumbs': NutritionInfo(395, 13.4, 71.9, 5.3, 4.5, 6.2, 732, 0, 0, 121, 4.0, 152, 0, 0, 1.2, 0, 1.9, 2.0),
            'panko': NutritionInfo(373, 12.3, 77.0, 2.4, 3.0, 5.0, 628, 0, 0, 62, 3.5, 127, 0, 0, 0.5, 0, 0.8, 1.0),
            'cornstarch': NutritionInfo(381, 0.3, 91.3, 0.1, 0.9, 0, 9, 0, 0, 2, 0.5, 3, 0, 0, 0.0, 0, 0.0, 0.0),
            'gelatin': NutritionInfo(355, 85.6, 0, 0.1, 0, 0, 196, 0, 0, 0, 0.0, 0, 0, 0, 0.0, 0, 0.0, 0.0),
        }
    
