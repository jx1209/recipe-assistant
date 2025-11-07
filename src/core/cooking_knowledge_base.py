"""
cooking knowledge base - FAQ system
provides rule-based cooking advice and answers without requiring AI
"""

from typing import List, Dict, Optional, Tuple
import re


class CookingKnowledgeBase:
    """rule-based cooking Q&A system for fallback when AI is unavailable"""
    
    def __init__(self):
        self.knowledge_base = self._build_knowledge_base()
        self.categories = {
            "techniques": ["how to", "what is", "technique", "method", "process"],
            "timing": ["how long", "cook time", "duration", "minutes", "hours"],
            "temperature": ["temperature", "degrees", "heat", "oven", "stove"],
            "storage": ["store", "keep", "save", "freeze", "refrigerate", "shelf life"],
            "safety": ["safe", "raw", "undercooked", "bacteria", "foodborne"],
            "substitution": ["substitute", "replace", "alternative", "instead of"],
            "measurements": ["measure", "convert", "cup", "tablespoon", "gram", "ounce"],
            "equipment": ["tool", "equipment", "pan", "knife", "appliance"],
        }
    
    def _build_knowledge_base(self) -> Dict[str, Dict]:
        """build comprehensive cooking knowledge base"""
        return {
            # Cooking techniques
            "sauté": {
                "answer": "To sauté, heat oil or butter in a pan over medium-high heat. Add ingredients and cook while stirring frequently until browned and cooked through. Use high heat and keep food moving.",
                "keywords": ["sauté", "saute", "pan fry", "stir fry"],
                "category": "techniques"
            },
            "roast": {
                "answer": "Roasting cooks food with dry heat in an oven, typically at 375-450°F (190-230°C). Use a roasting pan, coat with oil, and cook until browned and tender. Great for vegetables and meats.",
                "keywords": ["roast", "roasting", "oven roast"],
                "category": "techniques"
            },
            "blanch": {
                "answer": "Blanching involves briefly boiling food (usually vegetables) for 1-3 minutes, then immediately plunging into ice water to stop cooking. This preserves color, texture, and nutrients.",
                "keywords": ["blanch", "blanching", "parboil"],
                "category": "techniques"
            },
            "braise": {
                "answer": "Braising is cooking food slowly in a small amount of liquid in a covered pot. Brown the food first, add liquid (wine, broth), cover, and cook low and slow until tender. Perfect for tough cuts of meat.",
                "keywords": ["braise", "braising", "pot roast", "slow cook"],
                "category": "techniques"
            },
            "simmer": {
                "answer": "Simmering means cooking in liquid just below boiling point (180-200°F/82-93°C). You'll see small bubbles breaking the surface. Used for soups, sauces, and tender foods.",
                "keywords": ["simmer", "simmering", "low boil"],
                "category": "techniques"
            },
            
            # Cooking times
            "chicken_time": {
                "answer": "Chicken breast: 20-30 minutes at 375°F. Whole chicken: 20 minutes per pound at 375°F. Chicken thighs: 35-45 minutes. Always check internal temperature reaches 165°F (74°C).",
                "keywords": ["chicken time", "cook chicken", "how long chicken"],
                "category": "timing"
            },
            "pasta_time": {
                "answer": "Pasta typically cooks in 8-12 minutes in boiling salted water. Check package directions. Fresh pasta cooks in 2-4 minutes. Pasta should be al dente (firm to the bite).",
                "keywords": ["pasta time", "cook pasta", "boil pasta", "spaghetti time"],
                "category": "timing"
            },
            "rice_time": {
                "answer": "White rice: 15-20 minutes (1:2 rice to water ratio). Brown rice: 40-50 minutes (1:2.5 ratio). Bring to boil, reduce to simmer, cover until water absorbed.",
                "keywords": ["rice time", "cook rice", "how long rice"],
                "category": "timing"
            },
            "steak_time": {
                "answer": "For 1-inch steak: Rare (2-3 min/side), Medium-rare (3-4 min/side), Medium (4-5 min/side), Well-done (5-6 min/side). Let rest 5 minutes before cutting.",
                "keywords": ["steak time", "cook steak", "grill steak", "how long steak"],
                "category": "timing"
            },
            
            # Temperatures
            "oven_temp": {
                "answer": "Common oven temperatures: Slow (250-300°F), Moderate (325-375°F), Hot (400-450°F), Very hot (450-500°F). Most recipes use 350-375°F.",
                "keywords": ["oven temperature", "oven temp", "baking temperature"],
                "category": "temperature"
            },
            "meat_temp": {
                "answer": "Safe internal temperatures: Poultry 165°F (74°C), Ground meat 160°F (71°C), Beef/pork/lamb (whole cuts) 145°F (63°C), Fish 145°F (63°C). Always use a meat thermometer.",
                "keywords": ["meat temperature", "internal temperature", "safe temperature", "cooking temperature"],
                "category": "temperature"
            },
            
            # Storage
            "refrigerate": {
                "answer": "Refrigerator temp should be 40°F (4°C) or below. Leftovers last 3-4 days. Raw meat lasts 1-2 days. Always store in airtight containers. Cool hot food to room temp before refrigerating.",
                "keywords": ["refrigerate", "fridge", "store leftovers", "how long fridge"],
                "category": "storage"
            },
            "freeze": {
                "answer": "Freezer temp should be 0°F (-18°C). Most foods last 3-6 months frozen. Use airtight containers or freezer bags. Label with date. Thaw in fridge, not on counter.",
                "keywords": ["freeze", "freezer", "frozen", "how long freeze"],
                "category": "storage"
            },
            
            # Food safety
            "food_safety": {
                "answer": "Follow the 2-hour rule: Don't leave food at room temperature for more than 2 hours (1 hour if above 90°F). When in doubt, throw it out. Always wash hands and surfaces.",
                "keywords": ["food safety", "safe to eat", "food poisoning", "bacteria"],
                "category": "safety"
            },
            "raw_chicken": {
                "answer": "Never eat raw or undercooked chicken. It must reach 165°F (74°C) internal temperature. Wash hands after handling. Don't rinse raw chicken (spreads bacteria). Use separate cutting boards.",
                "keywords": ["raw chicken", "undercooked chicken", "chicken safety"],
                "category": "safety"
            },
            
            # Measurements
            "conversions": {
                "answer": "Common conversions: 1 cup = 16 tablespoons = 48 teaspoons = 8 fluid ounces. 1 tablespoon = 3 teaspoons. 1 stick butter = 8 tablespoons = 1/2 cup. 1 pound = 16 ounces.",
                "keywords": ["convert", "conversion", "measurements", "cups to tablespoons"],
                "category": "measurements"
            },
            "metric_conversion": {
                "answer": "Metric conversions: 1 cup = 240ml, 1 tablespoon = 15ml, 1 teaspoon = 5ml, 1 ounce = 28g, 1 pound = 454g, 350°F = 177°C. For temp: (F-32) × 5/9 = C.",
                "keywords": ["metric", "grams", "celsius", "milliliters", "convert metric"],
                "category": "measurements"
            },
            
            # Equipment
            "knife_types": {
                "answer": "Essential knives: Chef's knife (8-inch, all-purpose), Paring knife (small tasks), Serrated knife (bread). Keep sharp with a honing steel. Use cutting board, not countertop.",
                "keywords": ["knife", "knives", "chef knife", "which knife"],
                "category": "equipment"
            },
            "pan_types": {
                "answer": "Essential pans: Non-stick (eggs, delicate), Cast iron (searing, oven-safe), Stainless steel (browning), Sauté pan (general cooking). Different pans for different tasks.",
                "keywords": ["pan", "skillet", "pot", "cookware", "which pan"],
                "category": "equipment"
            },
            
            # Ingredients
            "salt": {
                "answer": "Salt enhances flavor. Types: Table salt (fine, iodized), Kosher salt (coarse, cooking), Sea salt (finishing). Season throughout cooking, not just at the end. Taste as you go.",
                "keywords": ["salt", "season", "seasoning", "how much salt"],
                "category": "techniques"
            },
            "eggs": {
                "answer": "Room temperature eggs work better in baking. Store in fridge. Test freshness: place in water—fresh eggs sink. Hard-boiled: 10-12 minutes. Scrambled: low heat, constant stirring.",
                "keywords": ["eggs", "egg", "cook eggs", "boil eggs"],
                "category": "techniques"
            },
            
            # Baking
            "baking_basics": {
                "answer": "Baking is a science: Measure accurately, preheat oven, use room temperature ingredients (unless specified), don't overmix, check doneness before stated time, let cool before cutting.",
                "keywords": ["baking", "bake", "baking tips", "how to bake"],
                "category": "techniques"
            },
            "yeast": {
                "answer": "Activate yeast in warm water (105-115°F) with sugar for 5-10 minutes until foamy. Too hot kills yeast, too cold won't activate. Dough should double in size (1-2 hours in warm place).",
                "keywords": ["yeast", "bread", "activate yeast", "proof yeast"],
                "category": "techniques"
            },
            
            # Vegetables
            "garlic": {
                "answer": "Mince garlic for maximum flavor. Add near end of cooking (burns easily). One clove = 1/2 teaspoon minced. Roasted garlic (whole head, 40 min at 400°F) is sweet and mild.",
                "keywords": ["garlic", "cook garlic", "mince garlic"],
                "category": "techniques"
            },
            "onion": {
                "answer": "Cut onion without crying: chill first, use sharp knife, cut near running water. Cook until translucent (soft) or caramelized (brown, sweet, 30-45 minutes low heat).",
                "keywords": ["onion", "cook onion", "caramelize onion", "cut onion"],
                "category": "techniques"
            },
        }
    
    def search(self, query: str) -> List[Dict]:
        """
        search knowledge base for relevant answers
        returns list of matching results sorted by relevance
        """
        query_lower = query.lower()
        results = []
        
        for topic, data in self.knowledge_base.items():
            score = 0
            
            # Check if any keywords match
            for keyword in data["keywords"]:
                if keyword in query_lower:
                    score += 10
                    # Exact match gets bonus
                    if keyword == query_lower:
                        score += 20
            
            # Check if words from query appear in keywords or answer
            query_words = set(re.findall(r'\w+', query_lower))
            for word in query_words:
                if len(word) > 3:  # Skip small words
                    if word in data["answer"].lower():
                        score += 2
                    for keyword in data["keywords"]:
                        if word in keyword:
                            score += 3
            
            if score > 0:
                results.append({
                    "topic": topic,
                    "answer": data["answer"],
                    "category": data["category"],
                    "relevance_score": score
                })
        
        # Sort by relevance score
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:5]  # Return top 5 results
    
    def get_answer(self, query: str) -> Optional[str]:
        """get the best answer for a query"""
        results = self.search(query)
        if results and results[0]["relevance_score"] >= 10:
            return results[0]["answer"]
        return None
    
    def get_category_tips(self, category: str) -> List[Dict]:
        """get all tips from a specific category"""
        return [
            {"topic": topic, "answer": data["answer"]}
            for topic, data in self.knowledge_base.items()
            if data["category"] == category
        ]
    
    def suggest_related(self, query: str, limit: int = 3) -> List[str]:
        """suggest related topics based on query"""
        results = self.search(query)
        
        if not results:
            return []
        
        # Get category of top result
        top_category = results[0]["category"]
        
        # Find other topics in same category
        related = []
        for topic, data in self.knowledge_base.items():
            if data["category"] == top_category and len(related) < limit:
                if topic not in [r["topic"] for r in results[:1]]:
                    related.append(data["answer"])
        
        return related

