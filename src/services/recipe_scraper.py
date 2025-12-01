from typing import Optional, Dict, Any
from recipe_scrapers import scrape_me, WebsiteNotImplementedError, NoSchemaFoundInWildMode
import logging
from src.models.recipe import RecipeCreate, RecipeIngredient, RecipeNutrition, DifficultyLevel
import re

logger = logging.getLogger(__name__)


class RecipeScraperService:
    
    def __init__(self):
        self.supported_sites_count = 100
    
    async def scrape_recipe_from_url(self, url: str) -> Optional[RecipeCreate]:
        """
        scrape recipe data from url
        
        args:
            url: recipe url to scrape
            
        returns:
            recipeCreate object if successful, none if failed
        """
        try:
            logger.info(f"scraping recipe from url: {url}")
            
            #use recipe-scrapers library
            scraper = scrape_me(url, wild_mode=True)
            
            #extract basic information
            title = scraper.title()
            if not title or len(title) < 2:
                raise ValueError("recipe title is too short or missing")
            
            #parse ingredients into structured format
            raw_ingredients = scraper.ingredients()
            ingredients = self._parse_ingredients(raw_ingredients)
            
            if not ingredients:
                raise ValueError("no ingredients found in recipe")
            
            #parse instructions
            instructions_text = scraper.instructions()
            instructions = self._parse_instructions(instructions_text)
            
            if not instructions:
                raise ValueError("no instructions found in recipe")
            
            #extract timing information
            prep_time = self._parse_time(scraper.prep_time())
            cook_time = self._parse_time(scraper.cook_time())
            total_time = self._parse_time(scraper.total_time())
            
            #extract servings
            servings = self._parse_servings(scraper.yields())
            
            #extract image
            image_url = None
            try:
                image = scraper.image()
                if image and self._is_valid_url(image):
                    image_url = image
            except Exception:
                pass
            
            #extract nutrition if available
            nutrition = None
            try:
                nutrients = scraper.nutrients()
                if nutrients:
                    nutrition = self._parse_nutrition(nutrients)
            except Exception as e:
                logger.debug(f"no nutrition data available: {e}")
            
            #extract host/source name
            source_name = scraper.host()
            
            #extract description if available
            description = None
            try:
                description = scraper.description()
                if description and len(description) > 1000:
                    description = description[:997] + "..."
            except Exception:
                pass
            
            #infer difficulty based on time and steps
            difficulty = self._infer_difficulty(total_time or prep_time or cook_time, len(instructions))
            
            #auto-generate tags based on content
            tags = self._generate_tags(title, instructions_text, raw_ingredients)
            
            #create recipe object
            recipe = RecipeCreate(
                title=title,
                description=description,
                source_url=str(url),
                source_name=source_name,
                ingredients=ingredients,
                instructions=instructions,
                image_url=image_url,
                prep_time_minutes=prep_time,
                cook_time_minutes=cook_time,
                servings=servings,
                difficulty=difficulty,
                tags=tags,
                nutrition=nutrition
            )
            
            logger.info(f"successfully scraped recipe: {title}")
            return recipe
            
        except WebsiteNotImplementedError:
            logger.error(f"website not supported by recipe-scrapers: {url}")
            return None
        except NoSchemaFoundInWildMode:
            logger.error(f"no recipe schema found on page: {url}")
            return None
        except Exception as e:
            logger.error(f"error scraping recipe from {url}: {str(e)}")
            return None
    
    def _parse_ingredients(self, raw_ingredients: list) -> list[RecipeIngredient]:
        """parse raw ingredient strings into structured format"""
        ingredients = []
        
        for ing in raw_ingredients:
            if not ing or not ing.strip():
                continue
            
            #basic parsing - extract quantity, unit, and name
            ingredient_data = self._parse_ingredient_string(ing.strip())
            ingredients.append(RecipeIngredient(**ingredient_data))
        
        return ingredients
    
    def _parse_ingredient_string(self, ing: str) -> dict:
        """
        parse single ingredient string
        tries to extract quantity, unit, and ingredient name
        """
        #common measurement units
        units = [
            'cup', 'cups', 'tablespoon', 'tablespoons', 'tbsp', 'teaspoon', 'teaspoons', 'tsp',
            'ounce', 'ounces', 'oz', 'pound', 'pounds', 'lb', 'lbs', 'gram', 'grams', 'g',
            'kilogram', 'kilograms', 'kg', 'liter', 'liters', 'l', 'milliliter', 'milliliters', 'ml',
            'clove', 'cloves', 'pinch', 'dash', 'can', 'cans', 'package', 'packages', 'bunch',
            'piece', 'pieces', 'slice', 'slices', 'large', 'medium', 'small'
        ]
        
        #try to match pattern: quantity + unit + ingredient
        pattern = r'^(\d+(?:\.\d+)?(?:/\d+)?)\s*(' + '|'.join(units) + r')?\s*(.+)$'
        match = re.match(pattern, ing, re.IGNORECASE)
        
        if match:
            quantity_str, unit, name = match.groups()
            
            #parse quantity (handle fractions)
            quantity = self._parse_quantity(quantity_str)
            
            return {
                'name': name.strip(),
                'quantity': quantity,
                'unit': unit.lower() if unit else None
            }
        
        #if no quantity found, treat entire string as ingredient name
        return {
            'name': ing,
            'quantity': None,
            'unit': None
        }
    
    def _parse_quantity(self, quantity_str: str) -> Optional[float]:
        """parse quantity string including fractions"""
        try:
            if '/' in quantity_str:
                parts = quantity_str.split('/')
                return float(parts[0]) / float(parts[1])
            return float(quantity_str)
        except (ValueError, ZeroDivisionError):
            return None
    
    def _parse_instructions(self, instructions_text: str) -> list[str]:
        """parse instruction text into list of steps"""
        if not instructions_text:
            return []
        
        #split by newlines or numbered steps
        steps = re.split(r'\n+|\d+\.\s*', instructions_text)
        
        #clean and filter steps
        cleaned_steps = []
        for step in steps:
            step = step.strip()
            if step and len(step) > 5:  #filter out very short steps
                cleaned_steps.append(step)
        
        return cleaned_steps
    
    def _parse_time(self, time_value: Optional[int]) -> Optional[int]:
        """parse time value to minutes"""
        if time_value is None:
            return None
        
        #recipe-scrapers returns time in minutes
        if isinstance(time_value, int) and time_value > 0:
            return min(time_value, 1440)  #cap at 24 hours
        
        return None
    
    def _parse_servings(self, yields_str: Optional[str]) -> int:
        """extract number of servings from yields string"""
        if not yields_str:
            return 4  #default
        
        #try to extract number from string
        match = re.search(r'(\d+)', str(yields_str))
        if match:
            servings = int(match.group(1))
            return min(max(servings, 1), 100)  #clamp between 1-100
        
        return 4  #default
    
    def _parse_nutrition(self, nutrients: dict) -> Optional[RecipeNutrition]:
        """parse nutrition data from scraper"""
        try:
            #extract numeric values from strings like "250 calories"
            def extract_number(value):
                if value is None:
                    return None
                match = re.search(r'(\d+(?:\.\d+)?)', str(value))
                return float(match.group(1)) if match else None
            
            nutrition_data = {}
            
            #map scraper keys to our model keys
            key_mapping = {
                'calories': 'calories',
                'protein': 'protein_g',
                'carbohydrates': 'carbs_g',
                'carbohydrateContent': 'carbs_g',
                'fat': 'fat_g',
                'fatContent': 'fat_g',
                'fiber': 'fiber_g',
                'fiberContent': 'fiber_g',
                'sugar': 'sugar_g',
                'sugarContent': 'sugar_g',
                'sodium': 'sodium_mg',
                'sodiumContent': 'sodium_mg',
                'cholesterol': 'cholesterol_mg',
                'cholesterolContent': 'cholesterol_mg',
            }
            
            for scraper_key, model_key in key_mapping.items():
                if scraper_key in nutrients:
                    value = extract_number(nutrients[scraper_key])
                    if value is not None:
                        nutrition_data[model_key] = value
            
            if nutrition_data:
                return RecipeNutrition(**nutrition_data)
            
            return None
        except Exception as e:
            logger.debug(f"error parsing nutrition: {e}")
            return None
    
    def _infer_difficulty(self, total_minutes: Optional[int], step_count: int) -> Optional[DifficultyLevel]:
        """infer recipe difficulty based on time and steps"""
        if total_minutes is None:
            total_minutes = 30  #assume medium time if unknown
        
        #scoring system
        time_score = 0
        if total_minutes <= 20:
            time_score = 1
        elif total_minutes <= 60:
            time_score = 2
        else:
            time_score = 3
        
        step_score = 0
        if step_count <= 5:
            step_score = 1
        elif step_count <= 10:
            step_score = 2
        else:
            step_score = 3
        
        #combine scores
        avg_score = (time_score + step_score) / 2
        
        if avg_score <= 1.5:
            return DifficultyLevel.EASY
        elif avg_score <= 2.5:
            return DifficultyLevel.MEDIUM
        else:
            return DifficultyLevel.HARD
    
    def _generate_tags(self, title: str, instructions: str, ingredients: list) -> list[str]:
        """auto-generate tags based on recipe content"""
        tags = set()
        
        #combine all text for analysis
        all_text = f"{title} {instructions} {' '.join(ingredients)}".lower()
        
        #meal type tags
        if any(word in all_text for word in ['breakfast', 'brunch', 'morning']):
            tags.add('breakfast')
        if any(word in all_text for word in ['lunch', 'sandwich', 'salad']):
            tags.add('lunch')
        if any(word in all_text for word in ['dinner', 'supper']):
            tags.add('dinner')
        if any(word in all_text for word in ['dessert', 'cake', 'cookie', 'sweet', 'chocolate']):
            tags.add('dessert')
        if any(word in all_text for word in ['appetizer', 'starter', 'snack']):
            tags.add('appetizer')
        
        #dietary tags
        if not any(word in all_text for word in ['chicken', 'beef', 'pork', 'fish', 'meat', 'bacon']):
            tags.add('vegetarian')
        if not any(word in all_text for word in ['egg', 'milk', 'cheese', 'butter', 'cream', 'yogurt']):
            tags.add('vegan')
        if any(word in all_text for word in ['gluten-free', 'gluten free']):
            tags.add('gluten-free')
        
        #cooking method tags
        if any(word in all_text for word in ['bake', 'baking', 'oven']):
            tags.add('baked')
        if any(word in all_text for word in ['grill', 'grilled', 'grilling']):
            tags.add('grilled')
        if any(word in all_text for word in ['fry', 'fried', 'frying']):
            tags.add('fried')
        if 'slow cooker' in all_text or 'crockpot' in all_text:
            tags.add('slow-cooker')
        
        #quick/easy tags
        if any(word in title.lower() for word in ['quick', 'easy', 'simple', '15 minute', '20 minute']):
            tags.add('quick')
        
        return list(tags)
    
    def _is_valid_url(self, url: str) -> bool:
        """check if string is a valid url"""
        url_pattern = re.compile(
            r'^https?://'  #http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  #domain...
            r'localhost|'  #localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  #...or ip
            r'(?::\d+)?'  #optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None

