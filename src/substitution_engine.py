"""
ingredient substitution engine
suggests intelligent substitutions based on dietary needs, pantry, or availability
"""

from typing import List, Dict, Optional


class SubstitutionEngine:
    def __init__(self):
        self.substitution_rules: Dict[str, List[str]] = {
            # Dairy substitutions
            "egg": ["1 tbsp flaxseed + 3 tbsp water", "1 tbsp chia seeds + 3 tbsp water", "1/4 cup applesauce", "1/4 cup silken tofu", "1/2 mashed banana", "3 tbsp aquafaba"],
            "milk": ["almond milk", "soy milk", "oat milk", "coconut milk", "cashew milk", "rice milk"],
            "buttermilk": ["1 cup milk + 1 tbsp vinegar", "1 cup milk + 1 tbsp lemon juice", "1 cup plain yogurt thinned with milk"],
            "butter": ["coconut oil", "olive oil", "avocado oil", "applesauce (for baking)", "mashed banana (for baking)", "ghee"],
            "heavy cream": ["coconut cream", "cashew cream", "evaporated milk", "greek yogurt + milk"],
            "sour cream": ["greek yogurt", "coconut cream", "cashew cream + lemon juice", "silken tofu blended with vinegar"],
            "yogurt": ["sour cream", "coconut yogurt", "cashew cream", "silken tofu"],
            "cream cheese": ["greek yogurt", "neufchatel cheese", "cashew cream cheese", "silken tofu + nutritional yeast"],
            "cheese": ["nutritional yeast", "vegan cheese", "cashew cheese", "tofu ricotta"],
            "parmesan": ["pecorino romano", "grana padano", "nutritional yeast + salt", "vegan parmesan"],
            
            # Sweeteners
            "sugar": ["honey", "maple syrup", "agave nectar", "coconut sugar", "date sugar", "stevia (use less)"],
            "brown sugar": ["white sugar + molasses", "coconut sugar", "date sugar", "maple sugar"],
            "honey": ["maple syrup", "agave nectar", "brown rice syrup", "date syrup"],
            "corn syrup": ["honey", "maple syrup", "golden syrup", "agave nectar"],
            
            # Flours & grains
            "all-purpose flour": ["whole wheat flour (3/4 cup per 1 cup)", "spelt flour", "bread flour", "cake flour + cornstarch"],
            "bread flour": ["all-purpose flour", "whole wheat flour", "spelt flour"],
            "cake flour": ["all-purpose flour minus 2 tbsp + 2 tbsp cornstarch per cup"],
            "self-rising flour": ["all-purpose flour + 1.5 tsp baking powder + 1/4 tsp salt per cup"],
            "wheat flour": ["almond flour (use more)", "oat flour", "coconut flour (use less)", "rice flour"],
            "cornstarch": ["arrowroot powder", "tapioca starch", "potato starch", "flour (use 2x amount)"],
            "breadcrumbs": ["panko", "crushed crackers", "crushed cereal", "oats", "crushed tortilla chips"],
            
            # Proteins
            "beef": ["ground turkey", "ground chicken", "plant-based ground meat", "lentils", "mushrooms"],
            "chicken": ["turkey", "tofu", "tempeh", "seitan", "jackfruit"],
            "pork": ["chicken", "turkey", "tempeh", "mushrooms"],
            "bacon": ["turkey bacon", "tempeh bacon", "coconut bacon", "smoked paprika for flavor"],
            "ground meat": ["lentils", "black beans", "mushrooms", "walnut meat", "plant-based ground"],
            "fish": ["tofu", "tempeh", "hearts of palm", "chickpeas"],
            
            # Condiments & sauces
            "soy sauce": ["tamari (gluten-free)", "coconut aminos", "Worcestershire sauce", "liquid aminos"],
            "worcestershire sauce": ["soy sauce + vinegar + molasses", "tamari + apple cider vinegar", "balsamic vinegar"],
            "mayonnaise": ["greek yogurt", "avocado", "hummus", "vegan mayo", "sour cream"],
            "ketchup": ["tomato paste + vinegar + sugar", "sriracha (spicier)", "bbq sauce"],
            "tomato paste": ["ketchup (reduce other liquids)", "tomato sauce (reduce liquids)", "sun-dried tomatoes blended"],
            "tomato sauce": ["crushed tomatoes", "diced tomatoes blended", "tomato paste + water"],
            
            # Oils & fats
            "vegetable oil": ["canola oil", "sunflower oil", "grapeseed oil", "melted coconut oil", "applesauce (baking)"],
            "olive oil": ["avocado oil", "canola oil", "vegetable oil", "melted butter"],
            "coconut oil": ["butter", "vegetable oil", "avocado oil", "olive oil"],
            
            # Baking ingredients
            "baking powder": ["1/4 tsp baking soda + 1/2 tsp cream of tartar per 1 tsp", "self-rising flour (reduce other leavening)"],
            "baking soda": ["baking powder (use 3x amount)", "potassium bicarbonate"],
            "yeast": ["baking powder (for quick breads)", "sourdough starter"],
            "vanilla extract": ["vanilla bean paste", "almond extract (use less)", "maple syrup", "vanilla powder"],
            
            # Vegetables
            "onion": ["shallots", "leeks", "green onions", "onion powder (1 tbsp = 1 medium onion)"],
            "garlic": ["garlic powder (1/8 tsp = 1 clove)", "shallots", "garlic scapes", "asafoetida (pinch)"],
            "bell pepper": ["poblano pepper", "cubanelle pepper", "banana pepper"],
            "mushrooms": ["eggplant", "zucchini", "tofu", "extra veggies"],
            
            # Nuts & seeds
            "peanut butter": ["almond butter", "sunflower seed butter", "cashew butter", "tahini"],
            "almonds": ["cashews", "walnuts", "pecans", "sunflower seeds"],
            "walnuts": ["pecans", "almonds", "hazelnuts", "cashews"],
            
            # Herbs & spices
            "fresh herbs": ["dried herbs (use 1/3 amount)", "herb paste", "frozen herbs"],
            "dried herbs": ["fresh herbs (use 3x amount)"],
            "italian seasoning": ["equal parts basil, oregano, thyme, rosemary"],
            "cajun seasoning": ["paprika + cayenne + garlic powder + oregano"],
            
            # Misc
            "wine": ["grape juice + vinegar", "broth + vinegar", "apple cider"],
            "beer": ["non-alcoholic beer", "broth", "apple juice"],
            "lemon juice": ["lime juice", "white wine vinegar", "apple cider vinegar"],
            "vinegar": ["lemon juice", "lime juice", "white wine"],
        }

    def suggest(self, ingredient: str, dietary_flags: Optional[List[str]] = None, pantry: Optional[List[str]] = None) -> List[str]:
        """
        suggest substitutions for an ingredient, optionally filtered by dietary needs and pantry inventory
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
        add or overwrite a custom substitution rule
        """
        self.substitution_rules[ingredient.lower()] = alternatives

    def get_supported_ingredients(self) -> List[str]:
        return list(self.substitution_rules.keys())

    def get_all_rules(self) -> Dict[str, List[str]]:
        return self.substitution_rules
