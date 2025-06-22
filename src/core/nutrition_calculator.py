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
