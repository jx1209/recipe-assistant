"""
Claude API client service
Handles communication with Anthropic's Claude API for AI-powered features
"""

import anthropic
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class ClaudeClient:
    """Claude API client with rate limiting and error handling"""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize Claude client
        
        Args:
            api_key: Anthropic API key
            model: Claude model to use
        """
        self.api_key = api_key
        self.model = model
        self.client = anthropic.Anthropic(api_key=api_key)
        
        # Rate limiting (simple in-memory for now)
        self.last_request_time = None
        self.min_request_interval = timedelta(seconds=1)  # 1 second between requests
        
    async def generate_recipe_from_ingredients(
        self,
        ingredients: List[str],
        dietary_restrictions: Optional[List[str]] = None,
        cuisine: Optional[str] = None,
        meal_type: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a recipe using provided ingredients
        
        Args:
            ingredients: List of available ingredients
            dietary_restrictions: Optional dietary restrictions
            cuisine: Optional cuisine type
            meal_type: Optional meal type (breakfast, lunch, dinner)
            difficulty: Optional difficulty level
            
        Returns:
            Dict with recipe data
        """
        try:
            # Build prompt
            prompt = self._build_recipe_generation_prompt(
                ingredients, dietary_restrictions, cuisine, meal_type, difficulty
            )
            
            # Call Claude API
            response = await self._make_api_call(prompt, max_tokens=2000)
            
            # Parse response into recipe format
            recipe_data = self._parse_recipe_response(response)
            
            return recipe_data
            
        except Exception as e:
            logger.error(f"Error generating recipe: {e}")
            raise
    
    async def generate_recipe_from_description(
        self,
        description: str,
        dietary_restrictions: Optional[List[str]] = None,
        servings: int = 4
    ) -> Dict[str, Any]:
        """
        Generate a recipe from a text description
        
        Args:
            description: Natural language description of desired recipe
            dietary_restrictions: Optional dietary restrictions
            servings: Number of servings
            
        Returns:
            Dict with recipe data
        """
        try:
            prompt = self._build_description_prompt(
                description, dietary_restrictions, servings
            )
            
            response = await self._make_api_call(prompt, max_tokens=2000)
            recipe_data = self._parse_recipe_response(response)
            
            return recipe_data
            
        except Exception as e:
            logger.error(f"Error generating recipe from description: {e}")
            raise
    
    async def answer_cooking_question(
        self,
        question: str,
        recipe_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Answer a cooking-related question
        
        Args:
            question: The cooking question
            recipe_context: Optional recipe context for recipe-specific questions
            
        Returns:
            Answer as text
        """
        try:
            prompt = self._build_qa_prompt(question, recipe_context)
            response = await self._make_api_call(prompt, max_tokens=1000)
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error answering cooking question: {e}")
            raise
    
    async def suggest_substitutions(
        self,
        ingredient: str,
        dietary_restrictions: Optional[List[str]] = None,
        recipe_context: Optional[str] = None
    ) -> List[str]:
        """
        Get AI-powered ingredient substitution suggestions
        
        Args:
            ingredient: Ingredient to substitute
            dietary_restrictions: Optional dietary restrictions
            recipe_context: Optional recipe context
            
        Returns:
            List of substitution suggestions
        """
        try:
            prompt = self._build_substitution_prompt(
                ingredient, dietary_restrictions, recipe_context
            )
            
            response = await self._make_api_call(prompt, max_tokens=500)
            
            # Parse response into list
            substitutions = self._parse_substitution_response(response)
            
            return substitutions
            
        except Exception as e:
            logger.error(f"Error suggesting substitutions: {e}")
            raise
    
    async def modify_recipe(
        self,
        recipe_data: Dict[str, Any],
        modification_type: str,
        specific_request: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Modify an existing recipe based on requirements
        
        Args:
            recipe_data: Original recipe data
            modification_type: Type of modification (healthier, vegetarian, vegan, gluten-free, etc)
            specific_request: Optional specific modification request
            
        Returns:
            Modified recipe data
        """
        try:
            prompt = self._build_recipe_modification_prompt(
                recipe_data, modification_type, specific_request
            )
            
            response = await self._make_api_call(prompt, max_tokens=2000)
            modified_recipe = self._parse_recipe_response(response)
            
            return modified_recipe
            
        except Exception as e:
            logger.error(f"Error modifying recipe: {e}")
            raise
    
    async def generate_meal_plan(
        self,
        days: int,
        dietary_restrictions: Optional[List[str]] = None,
        cuisine_preferences: Optional[List[str]] = None,
        calories_target: Optional[int] = None,
        meal_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate an AI-powered meal plan
        
        Args:
            days: Number of days to plan for
            dietary_restrictions: Optional dietary restrictions
            cuisine_preferences: Optional cuisine preferences
            calories_target: Optional daily calorie target
            meal_types: Which meals to include (breakfast, lunch, dinner, snacks)
            
        Returns:
            Meal plan data with recipes for each day
        """
        try:
            prompt = self._build_meal_plan_prompt(
                days, dietary_restrictions, cuisine_preferences, 
                calories_target, meal_types
            )
            
            response = await self._make_api_call(prompt, max_tokens=3000)
            meal_plan = self._parse_meal_plan_response(response)
            
            return meal_plan
            
        except Exception as e:
            logger.error(f"Error generating meal plan: {e}")
            raise
    
    async def suggest_ingredient_pairings(
        self,
        main_ingredient: str,
        cuisine: Optional[str] = None,
        meal_type: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Suggest ingredients that pair well with a main ingredient
        
        Args:
            main_ingredient: The main ingredient
            cuisine: Optional cuisine context
            meal_type: Optional meal type
            
        Returns:
            List of ingredient pairings with explanations
        """
        try:
            prompt = self._build_pairing_prompt(main_ingredient, cuisine, meal_type)
            response = await self._make_api_call(prompt, max_tokens=800)
            
            pairings = self._parse_pairing_response(response)
            
            return pairings
            
        except Exception as e:
            logger.error(f"Error suggesting pairings: {e}")
            raise
    
    async def _make_api_call(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 1.0
    ) -> str:
        """
        Make an API call to Claude with rate limiting
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            
        Returns:
            Response text
        """
        # Simple rate limiting
        if self.last_request_time:
            time_since_last = datetime.now() - self.last_request_time
            if time_since_last < self.min_request_interval:
                wait_time = (self.min_request_interval - time_since_last).total_seconds()
                import asyncio
                await asyncio.sleep(wait_time)
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            self.last_request_time = datetime.now()
            
            # Extract text from response
            response_text = message.content[0].text
            
            logger.info(f"Claude API call successful. Tokens used: {message.usage.input_tokens + message.usage.output_tokens}")
            
            return response_text
            
        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}")
            raise ValueError(f"Claude API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error calling Claude API: {e}")
            raise
    
    def _build_recipe_generation_prompt(
        self,
        ingredients: List[str],
        dietary_restrictions: Optional[List[str]],
        cuisine: Optional[str],
        meal_type: Optional[str],
        difficulty: Optional[str]
    ) -> str:
        """Build prompt for recipe generation from ingredients"""
        
        prompt = f"""You are a professional chef assistant. Create a detailed recipe using the following ingredients:

Ingredients available: {', '.join(ingredients)}
"""
        
        if dietary_restrictions:
            prompt += f"\nDietary restrictions: {', '.join(dietary_restrictions)}"
        
        if cuisine:
            prompt += f"\nCuisine type: {cuisine}"
        
        if meal_type:
            prompt += f"\nMeal type: {meal_type}"
        
        if difficulty:
            prompt += f"\nDifficulty level: {difficulty}"
        
        prompt += """

Please provide a complete recipe in the following JSON format:
{
  "title": "Recipe Name",
  "description": "Brief description",
  "ingredients": [
    {"name": "ingredient", "quantity": 1, "unit": "cup", "notes": "optional notes"}
  ],
  "instructions": [
    "Step 1 instruction",
    "Step 2 instruction"
  ],
  "prep_time_minutes": 15,
  "cook_time_minutes": 30,
  "servings": 4,
  "difficulty": "Easy/Medium/Hard",
  "cuisine": "cuisine type",
  "tags": ["tag1", "tag2"]
}

Make sure the recipe is practical, uses most of the provided ingredients, and provides clear step-by-step instructions."""
        
        return prompt
    
    def _build_description_prompt(
        self,
        description: str,
        dietary_restrictions: Optional[List[str]],
        servings: int
    ) -> str:
        """Build prompt for recipe generation from description"""
        
        prompt = f"""You are a professional chef assistant. Create a detailed recipe based on this description:

"{description}"

Servings: {servings}
"""
        
        if dietary_restrictions:
            prompt += f"Dietary restrictions: {', '.join(dietary_restrictions)}\n"
        
        prompt += """
Please provide a complete recipe in the following JSON format:
{
  "title": "Recipe Name",
  "description": "Brief description",
  "ingredients": [
    {"name": "ingredient", "quantity": 1, "unit": "cup", "notes": "optional notes"}
  ],
  "instructions": [
    "Step 1 instruction",
    "Step 2 instruction"
  ],
  "prep_time_minutes": 15,
  "cook_time_minutes": 30,
  "servings": 4,
  "difficulty": "Easy/Medium/Hard",
  "cuisine": "cuisine type",
  "tags": ["tag1", "tag2"]
}

Make sure the recipe is practical and provides clear step-by-step instructions."""
        
        return prompt
    
    def _build_qa_prompt(
        self,
        question: str,
        recipe_context: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for cooking Q&A"""
        
        prompt = "You are an expert chef and cooking instructor. Answer the following cooking question:\n\n"
        
        if recipe_context:
            prompt += f"Recipe context:\n"
            prompt += f"Title: {recipe_context.get('title', 'N/A')}\n"
            if recipe_context.get('ingredients'):
                prompt += f"Ingredients: {', '.join(ing.get('name', '') for ing in recipe_context['ingredients'])}\n"
            prompt += "\n"
        
        prompt += f"Question: {question}\n\n"
        prompt += "Please provide a clear, helpful, and accurate answer. If the question is about a specific technique, provide step-by-step guidance."
        
        return prompt
    
    def _build_substitution_prompt(
        self,
        ingredient: str,
        dietary_restrictions: Optional[List[str]],
        recipe_context: Optional[str]
    ) -> str:
        """Build prompt for ingredient substitution"""
        
        prompt = f"""You are an expert chef. Suggest suitable substitutions for this ingredient:

Ingredient: {ingredient}
"""
        
        if dietary_restrictions:
            prompt += f"Dietary restrictions: {', '.join(dietary_restrictions)}\n"
        
        if recipe_context:
            prompt += f"Recipe context: {recipe_context}\n"
        
        prompt += """
Provide 3-5 practical substitution suggestions. For each substitution, briefly explain how it works and any adjustments needed.

Format your response as a numbered list:
1. Substitution name - brief explanation
2. Substitution name - brief explanation
etc."""
        
        return prompt
    
    def _parse_recipe_response(self, response: str) -> Dict[str, Any]:
        """Parse Claude's recipe response into structured format"""
        
        try:
            # Try to extract JSON from response
            # Claude might wrap JSON in markdown code blocks
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                # Try to find JSON object
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
            
            recipe_data = json.loads(json_str)
            
            return recipe_data
            
        except Exception as e:
            logger.error(f"Error parsing recipe response: {e}")
            logger.debug(f"Response was: {response}")
            raise ValueError("Failed to parse recipe from AI response")
    
    def _parse_substitution_response(self, response: str) -> List[str]:
        """Parse substitution suggestions from response"""
        
        # Simple parsing - extract numbered list items
        substitutions = []
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Remove leading number/bullet and clean up
                cleaned = line.lstrip('0123456789.-•) ').strip()
                if cleaned:
                    substitutions.append(cleaned)
        
        return substitutions if substitutions else [response.strip()]


class ClaudeClientFactory:
    """Factory for creating Claude clients with different API keys"""
    
    _system_client: Optional[ClaudeClient] = None
    _user_clients: Dict[str, ClaudeClient] = {}
    
    @classmethod
    def get_system_client(cls, api_key: str) -> ClaudeClient:
        """Get or create system-wide Claude client"""
        if not cls._system_client or cls._system_client.api_key != api_key:
            cls._system_client = ClaudeClient(api_key)
        return cls._system_client
    
    @classmethod
    def get_user_client(cls, user_id: int, api_key: str) -> ClaudeClient:
        """Get or create user-specific Claude client"""
        cache_key = f"{user_id}:{api_key[:8]}"  # Use partial key for cache
        
        if cache_key not in cls._user_clients:
            cls._user_clients[cache_key] = ClaudeClient(api_key)
        
        return cls._user_clients[cache_key]
    
    @classmethod
    def clear_user_client(cls, user_id: int):
        """Clear cached client for user"""
        keys_to_remove = [k for k in cls._user_clients.keys() if k.startswith(f"{user_id}:")]
        for key in keys_to_remove:
            del cls._user_clients[key]

