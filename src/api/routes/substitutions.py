"""
ingredient substitution api endpoints
suggests intelligent substitutions based on dietary needs and pantry availability
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional, Dict
import logging

from src.models.user import UserResponse
from src.substitution_engine import SubstitutionEngine
from src.database import get_db
from src.auth.dependencies import get_current_user, get_current_user_optional
from src.config.settings import get_settings
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(tags=["substitutions"])
settings = get_settings()


class SubstitutionRequest(BaseModel):
    """request model for ingredient substitution"""
    ingredient: str
    dietary_restrictions: Optional[List[str]] = None
    use_pantry: bool = False


class BulkSubstitutionRequest(BaseModel):
    """request model for bulk ingredient substitutions"""
    ingredients: List[str]
    dietary_restrictions: Optional[List[str]] = None
    use_pantry: bool = False


class SubstitutionResponse(BaseModel):
    """response model for substitution suggestions"""
    ingredient: str
    substitutions: List[str]
    pantry_priority: Optional[List[str]] = None


def get_substitution_engine() -> SubstitutionEngine:
    """dependency to get substitution engine"""
    return SubstitutionEngine()


@router.post("/substitutions/suggest", response_model=SubstitutionResponse)
async def suggest_substitution(
    request: SubstitutionRequest,
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
    engine: SubstitutionEngine = Depends(get_substitution_engine)
):
    """
    suggest substitutions for a single ingredient
    optionally filters by dietary restrictions and user's pantry
    """
    try:
        pantry_items = []
        
        #get user's pantry if requested
        if request.use_pantry and current_user:
            db = get_db(settings.DATABASE_URL)
            cursor = db.conn.cursor()
            cursor.execute("""
                SELECT ingredient_name FROM user_pantry
                WHERE user_id = ?
            """, (current_user.id,))
            pantry_items = [row[0].lower() for row in cursor.fetchall()]
        
        #get substitutions
        substitutions = engine.suggest(
            request.ingredient,
            dietary_flags=request.dietary_restrictions,
            pantry=pantry_items if pantry_items else None
        )
        
        #separate pantry-based priority suggestions
        pantry_priority = []
        if pantry_items:
            pantry_priority = [sub for sub in substitutions 
                             if any(p in sub.lower() for p in pantry_items)]
        
        logger.info(f"suggested {len(substitutions)} substitutions for '{request.ingredient}'")
        
        return SubstitutionResponse(
            ingredient=request.ingredient,
            substitutions=substitutions,
            pantry_priority=pantry_priority if pantry_priority else None
        )
        
    except Exception as e:
        logger.error(f"error suggesting substitutions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error generating substitution suggestions"
        )


@router.post("/substitutions/bulk", response_model=List[SubstitutionResponse])
async def suggest_bulk_substitutions(
    request: BulkSubstitutionRequest,
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
    engine: SubstitutionEngine = Depends(get_substitution_engine)
):
    """
    suggest substitutions for multiple ingredients at once
    useful for recipe substitution suggestions
    """
    try:
        pantry_items = []
        
        #get user's pantry if requested
        if request.use_pantry and current_user:
            db = get_db(settings.DATABASE_URL)
            cursor = db.conn.cursor()
            cursor.execute("""
                SELECT ingredient_name FROM user_pantry
                WHERE user_id = ?
            """, (current_user.id,))
            pantry_items = [row[0].lower() for row in cursor.fetchall()]
        
        results = []
        
        for ingredient in request.ingredients:
            substitutions = engine.suggest(
                ingredient,
                dietary_flags=request.dietary_restrictions,
                pantry=pantry_items if pantry_items else None
            )
            
            #separate pantry-based priority
            pantry_priority = []
            if pantry_items:
                pantry_priority = [sub for sub in substitutions 
                                 if any(p in sub.lower() for p in pantry_items)]
            
            results.append(SubstitutionResponse(
                ingredient=ingredient,
                substitutions=substitutions,
                pantry_priority=pantry_priority if pantry_priority else None
            ))
        
        logger.info(f"suggested substitutions for {len(request.ingredients)} ingredients")
        return results
        
    except Exception as e:
        logger.error(f"error suggesting bulk substitutions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error generating bulk substitutions"
        )


@router.get("/substitutions/recipe/{recipe_id}", response_model=List[SubstitutionResponse])
async def suggest_recipe_substitutions(
    recipe_id: int,
    dietary_restrictions: Optional[str] = Query(None),
    use_pantry: bool = Query(False),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
    engine: SubstitutionEngine = Depends(get_substitution_engine)
):
    """
    suggest substitutions for all ingredients in a recipe
    helpful for adapting recipes to dietary needs or available ingredients
    """
    try:
        db = get_db(settings.DATABASE_URL)
        cursor = db.conn.cursor()
        
        #get recipe
        cursor.execute("""
            SELECT ingredients_json FROM recipes
            WHERE id = ? AND is_deleted = 0
        """, (recipe_id,))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="recipe not found"
            )
        
        import json
        ingredients = json.loads(row['ingredients_json'])
        
        #parse dietary restrictions
        dietary_flags = None
        if dietary_restrictions:
            dietary_flags = [d.strip().lower() for d in dietary_restrictions.split(',')]
        
        #get pantry items if requested
        pantry_items = []
        if use_pantry and current_user:
            cursor.execute("""
                SELECT ingredient_name FROM user_pantry
                WHERE user_id = ?
            """, (current_user.id,))
            pantry_items = [row[0].lower() for row in cursor.fetchall()]
        
        results = []
        
        for ing in ingredients:
            ingredient_name = ing['name']
            
            substitutions = engine.suggest(
                ingredient_name,
                dietary_flags=dietary_flags,
                pantry=pantry_items if pantry_items else None
            )
            
            if substitutions:  #only include ingredients that have substitutions
                pantry_priority = []
                if pantry_items:
                    pantry_priority = [sub for sub in substitutions 
                                     if any(p in sub.lower() for p in pantry_items)]
                
                results.append(SubstitutionResponse(
                    ingredient=ingredient_name,
                    substitutions=substitutions,
                    pantry_priority=pantry_priority if pantry_priority else None
                ))
        
        logger.info(f"suggested substitutions for recipe {recipe_id}: {len(results)} ingredients")
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"error suggesting recipe substitutions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error generating recipe substitutions"
        )


@router.get("/substitutions/supported", response_model=List[str])
async def get_supported_ingredients(
    engine: SubstitutionEngine = Depends(get_substitution_engine)
):
    """
    get list of all ingredients that have known substitutions
    """
    try:
        supported = engine.get_supported_ingredients()
        return sorted(supported)
        
    except Exception as e:
        logger.error(f"error getting supported ingredients: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error retrieving supported ingredients"
        )


@router.get("/substitutions/all", response_model=Dict[str, List[str]])
async def get_all_substitution_rules(
    engine: SubstitutionEngine = Depends(get_substitution_engine)
):
    """
    get all substitution rules in the system
    useful for understanding available substitutions
    """
    try:
        all_rules = engine.get_all_rules()
        return all_rules
        
    except Exception as e:
        logger.error(f"error getting all substitution rules: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error retrieving substitution rules"
        )

