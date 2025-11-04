"""
AI-powered features API endpoints
Handles Claude API integration for recipe generation and cooking assistance
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
import logging
import os

from src.models.user import UserResponse
from src.models.recipe import RecipeCreate, RecipeResponse
from src.services.claude_client import ClaudeClient, ClaudeClientFactory
from src.services.recipe_manager import RecipeManager
from src.database import get_db
from src.auth.dependencies import get_current_user
from src.config.settings import get_settings
from src.utils.encryption import get_encryption_service
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter(tags=["ai"])
settings = get_settings()


class AIRecipeGenerateRequest(BaseModel):
    """Request model for AI recipe generation"""
    ingredients: Optional[List[str]] = None
    description: Optional[str] = None
    dietary_restrictions: Optional[List[str]] = None
    cuisine: Optional[str] = None
    meal_type: Optional[str] = None
    difficulty: Optional[str] = None
    servings: int = Field(default=4, ge=1, le=20)
    save_recipe: bool = False  # Whether to save generated recipe


class CookingQuestionRequest(BaseModel):
    """Request model for cooking Q&A"""
    question: str = Field(..., min_length=5, max_length=500)
    recipe_id: Optional[int] = None  # Optional recipe context


class UserAPIKeyRequest(BaseModel):
    """Request model for setting user API key"""
    api_key: str = Field(..., min_length=20)


class SubstitutionRequest(BaseModel):
    """Request model for AI substitution suggestions"""
    ingredient: str
    dietary_restrictions: Optional[List[str]] = None
    recipe_context: Optional[str] = None


def get_claude_client(current_user: UserResponse = Depends(get_current_user)) -> ClaudeClient:
    """
    Get Claude client for current user
    Uses user's API key if available, otherwise system key
    """
    db = get_db(settings.DATABASE_URL)
    cursor = db.conn.cursor()
    
    # Check if user has their own API key
    cursor.execute(
        "SELECT claude_api_key_encrypted FROM users WHERE id = ?",
        (current_user.id,)
    )
    row = cursor.fetchone()
    
    if row and row[0]:
        # User has their own key - decrypt and use it
        encryption_service = get_encryption_service()
        user_api_key = encryption_service.decrypt(row[0])
        return ClaudeClientFactory.get_user_client(current_user.id, user_api_key)
    
    # Use system API key
    system_api_key = os.getenv('CLAUDE_API_KEY')
    if not system_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI features are not available. Please set your own Claude API key or contact administrator."
        )
    
    return ClaudeClientFactory.get_system_client(system_api_key)


def get_recipe_manager() -> RecipeManager:
    """Dependency to get recipe manager"""
    db = get_db(settings.DATABASE_URL)
    return RecipeManager(db.conn)


@router.post("/ai/generate-recipe", response_model=Dict[str, Any])
async def generate_recipe(
    request: AIRecipeGenerateRequest,
    current_user: UserResponse = Depends(get_current_user),
    claude_client: ClaudeClient = Depends(get_claude_client),
    recipe_manager: RecipeManager = Depends(get_recipe_manager)
):
    """
    Generate a recipe using AI
    Can generate from ingredients list or text description
    """
    try:
        # Validate request
        if not request.ingredients and not request.description:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either ingredients or description must be provided"
            )
        
        # Generate recipe using Claude
        if request.ingredients:
            recipe_data = await claude_client.generate_recipe_from_ingredients(
                ingredients=request.ingredients,
                dietary_restrictions=request.dietary_restrictions,
                cuisine=request.cuisine,
                meal_type=request.meal_type,
                difficulty=request.difficulty
            )
        else:
            recipe_data = await claude_client.generate_recipe_from_description(
                description=request.description,
                dietary_restrictions=request.dietary_restrictions,
                servings=request.servings
            )
        
        logger.info(f"Generated recipe for user {current_user.id}: {recipe_data.get('title')}")
        
        # Save recipe if requested
        saved_recipe = None
        if request.save_recipe:
            try:
                # Convert to RecipeCreate model
                recipe_create = RecipeCreate(**recipe_data)
                saved_recipe = await recipe_manager.create_recipe(recipe_create, current_user.id)
                
                return {
                    "recipe": recipe_data,
                    "saved": True,
                    "recipe_id": saved_recipe.id,
                    "message": "Recipe generated and saved successfully"
                }
            except Exception as e:
                logger.error(f"Error saving generated recipe: {e}")
                return {
                    "recipe": recipe_data,
                    "saved": False,
                    "message": "Recipe generated but could not be saved"
                }
        
        return {
            "recipe": recipe_data,
            "saved": False,
            "message": "Recipe generated successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating recipe: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating recipe with AI"
        )


@router.post("/ai/ask-cooking", response_model=Dict[str, str])
async def ask_cooking_question(
    request: CookingQuestionRequest,
    current_user: UserResponse = Depends(get_current_user),
    claude_client: ClaudeClient = Depends(get_claude_client),
    recipe_manager: RecipeManager = Depends(get_recipe_manager)
):
    """
    Ask a cooking-related question
    Optionally provide recipe context for recipe-specific questions
    """
    try:
        recipe_context = None
        
        # Get recipe context if provided
        if request.recipe_id:
            recipe = await recipe_manager.get_recipe(request.recipe_id, current_user.id)
            if recipe:
                recipe_context = {
                    "title": recipe.title,
                    "ingredients": [ing.model_dump() for ing in recipe.ingredients],
                    "instructions": recipe.instructions
                }
        
        # Get answer from Claude
        answer = await claude_client.answer_cooking_question(
            question=request.question,
            recipe_context=recipe_context
        )
        
        logger.info(f"Answered cooking question for user {current_user.id}")
        
        return {
            "question": request.question,
            "answer": answer,
            "recipe_id": str(request.recipe_id) if request.recipe_id else None
        }
        
    except Exception as e:
        logger.error(f"Error answering cooking question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing your question"
        )


@router.post("/ai/suggest-substitution", response_model=Dict[str, Any])
async def suggest_ai_substitution(
    request: SubstitutionRequest,
    current_user: UserResponse = Depends(get_current_user),
    claude_client: ClaudeClient = Depends(get_claude_client)
):
    """
    Get AI-powered ingredient substitution suggestions
    More intelligent than rule-based substitutions
    """
    try:
        substitutions = await claude_client.suggest_substitutions(
            ingredient=request.ingredient,
            dietary_restrictions=request.dietary_restrictions,
            recipe_context=request.recipe_context
        )
        
        logger.info(f"Suggested AI substitutions for '{request.ingredient}' for user {current_user.id}")
        
        return {
            "ingredient": request.ingredient,
            "substitutions": substitutions,
            "source": "AI-powered"
        }
        
    except Exception as e:
        logger.error(f"Error suggesting AI substitutions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating substitution suggestions"
        )


# User API Key Management

@router.post("/ai/api-key", status_code=status.HTTP_204_NO_CONTENT)
async def set_user_api_key(
    request: UserAPIKeyRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Set user's personal Claude API key
    The key is encrypted before storage
    """
    try:
        # Validate API key format (basic check)
        if not request.api_key.startswith('sk-ant-'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Claude API key format"
            )
        
        # Encrypt API key
        encryption_service = get_encryption_service()
        encrypted_key = encryption_service.encrypt(request.api_key)
        
        # Store encrypted key
        db = get_db(settings.DATABASE_URL)
        cursor = db.conn.cursor()
        cursor.execute("""
            UPDATE users 
            SET claude_api_key_encrypted = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (encrypted_key, current_user.id))
        db.conn.commit()
        
        # Clear cached client
        ClaudeClientFactory.clear_user_client(current_user.id)
        
        logger.info(f"User {current_user.id} set their Claude API key")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting user API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error saving API key"
        )


@router.delete("/ai/api-key", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_api_key(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Delete user's personal Claude API key
    User will fall back to system API key if available
    """
    try:
        db = get_db(settings.DATABASE_URL)
        cursor = db.conn.cursor()
        cursor.execute("""
            UPDATE users 
            SET claude_api_key_encrypted = NULL, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (current_user.id,))
        db.conn.commit()
        
        # Clear cached client
        ClaudeClientFactory.clear_user_client(current_user.id)
        
        logger.info(f"User {current_user.id} deleted their Claude API key")
        
    except Exception as e:
        logger.error(f"Error deleting user API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting API key"
        )


@router.get("/ai/api-key/status", response_model=Dict[str, Any])
async def get_api_key_status(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Check if user has API key configured and if system key is available
    """
    try:
        db = get_db(settings.DATABASE_URL)
        cursor = db.conn.cursor()
        cursor.execute(
            "SELECT claude_api_key_encrypted FROM users WHERE id = ?",
            (current_user.id,)
        )
        row = cursor.fetchone()
        
        has_user_key = bool(row and row[0])
        has_system_key = bool(os.getenv('CLAUDE_API_KEY'))
        
        return {
            "has_user_key": has_user_key,
            "has_system_key": has_system_key,
            "ai_available": has_user_key or has_system_key,
            "using": "user_key" if has_user_key else ("system_key" if has_system_key else "none")
        }
        
    except Exception as e:
        logger.error(f"Error checking API key status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error checking API key status"
        )

