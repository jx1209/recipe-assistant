"""
recipe api endpoints
handles recipe crud, search, import, and favorites
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
import logging

from src.models.recipe import (
    RecipeCreate, RecipeUpdate, RecipeResponse, RecipeSummary,
    RecipeSearch, RecipeImportUrl, DifficultyLevel
)
from src.models.user import UserResponse
from src.services.recipe_scraper import RecipeScraperService
from src.services.recipe_manager import RecipeManager
from src.database import get_db
from src.auth.dependencies import get_current_user, get_current_user_optional
from src.config.settings import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["recipes"])
settings = get_settings()


def get_recipe_manager() -> RecipeManager:
    """dependency to get recipe manager"""
    db = get_db(settings.DATABASE_URL)
    return RecipeManager(db.conn)


def get_recipe_scraper() -> RecipeScraperService:
    """dependency to get recipe scraper"""
    return RecipeScraperService()


@router.post("/recipes/import", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
async def import_recipe_from_url(
    import_data: RecipeImportUrl,
    current_user: UserResponse = Depends(get_current_user),
    scraper: RecipeScraperService = Depends(get_recipe_scraper),
    recipe_manager: RecipeManager = Depends(get_recipe_manager)
):
    """
    import recipe from url using recipe-scrapers
    supports 100+ recipe websites automatically
    """
    try:
        #scrape recipe from url
        recipe_data = await scraper.scrape_recipe_from_url(str(import_data.url))
        
        if not recipe_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="could not scrape recipe from url. website may not be supported or no recipe found"
            )
        
        #save to database
        recipe = await recipe_manager.create_recipe(recipe_data, current_user.id)
        
        logger.info(f"user {current_user.id} imported recipe from {import_data.url}")
        return recipe
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"error importing recipe: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error importing recipe"
        )


@router.post("/recipes", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    recipe_data: RecipeCreate,
    current_user: UserResponse = Depends(get_current_user),
    recipe_manager: RecipeManager = Depends(get_recipe_manager)
):
    """
    create new recipe manually
    """
    try:
        recipe = await recipe_manager.create_recipe(recipe_data, current_user.id)
        logger.info(f"user {current_user.id} created recipe {recipe.id}")
        return recipe
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"error creating recipe: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error creating recipe"
        )


@router.get("/recipes/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(
    recipe_id: int,
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
    recipe_manager: RecipeManager = Depends(get_recipe_manager)
):
    """
    get recipe by id
    includes user-specific data if authenticated (favorites, ratings)
    """
    try:
        user_id = current_user.id if current_user else None
        recipe = await recipe_manager.get_recipe(recipe_id, user_id)
        
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="recipe not found"
            )
        
        return recipe
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"error getting recipe {recipe_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error retrieving recipe"
        )


@router.put("/recipes/{recipe_id}", response_model=RecipeResponse)
async def update_recipe(
    recipe_id: int,
    recipe_data: RecipeUpdate,
    current_user: UserResponse = Depends(get_current_user),
    recipe_manager: RecipeManager = Depends(get_recipe_manager)
):
    """
    update recipe (only by creator)
    """
    try:
        recipe = await recipe_manager.update_recipe(recipe_id, recipe_data, current_user.id)
        
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="recipe not found"
            )
        
        logger.info(f"user {current_user.id} updated recipe {recipe_id}")
        return recipe
        
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you do not have permission to update this recipe"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"error updating recipe {recipe_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error updating recipe"
        )


@router.delete("/recipes/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: int,
    current_user: UserResponse = Depends(get_current_user),
    recipe_manager: RecipeManager = Depends(get_recipe_manager)
):
    """
    delete recipe (only by creator)
    """
    try:
        deleted = await recipe_manager.delete_recipe(recipe_id, current_user.id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="recipe not found"
            )
        
        logger.info(f"user {current_user.id} deleted recipe {recipe_id}")
        
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you do not have permission to delete this recipe"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"error deleting recipe {recipe_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error deleting recipe"
        )


@router.get("/recipes", response_model=dict)
async def search_recipes(
    query: Optional[str] = Query(None, max_length=200),
    cuisine: Optional[str] = Query(None, max_length=50),
    difficulty: Optional[DifficultyLevel] = None,
    max_time: Optional[int] = Query(None, ge=0, le=1440),
    tags: Optional[str] = Query(None),  #comma-separated
    ingredients: Optional[str] = Query(None),  #comma-separated
    exclude_ingredients: Optional[str] = Query(None),  #comma-separated
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("created_at", regex="^(created_at|rating|time|title)$"),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
    recipe_manager: RecipeManager = Depends(get_recipe_manager)
):
    """
    search recipes with filters
    returns paginated results with total count
    """
    try:
        #parse comma-separated lists
        tag_list = [t.strip() for t in tags.split(',')] if tags else None
        ingredient_list = [i.strip() for i in ingredients.split(',')] if ingredients else None
        exclude_list = [i.strip() for i in exclude_ingredients.split(',')] if exclude_ingredients else None
        
        #build search params
        search_params = RecipeSearch(
            query=query,
            cuisine=cuisine,
            difficulty=difficulty,
            max_time=max_time,
            tags=tag_list,
            ingredients=ingredient_list,
            exclude_ingredients=exclude_list,
            min_rating=min_rating,
            limit=limit,
            offset=offset,
            sort_by=sort_by
        )
        
        user_id = current_user.id if current_user else None
        recipes, total = await recipe_manager.search_recipes(search_params, user_id)
        
        return {
            "recipes": recipes,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total
        }
        
    except Exception as e:
        logger.error(f"error searching recipes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error searching recipes"
        )


@router.post("/recipes/{recipe_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
async def add_to_favorites(
    recipe_id: int,
    current_user: UserResponse = Depends(get_current_user),
    recipe_manager: RecipeManager = Depends(get_recipe_manager)
):
    """
    add recipe to favorites
    """
    try:
        success = await recipe_manager.add_to_favorites(recipe_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="recipe already in favorites"
            )
        
        logger.info(f"user {current_user.id} favorited recipe {recipe_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"error adding to favorites: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error adding to favorites"
        )


@router.delete("/recipes/{recipe_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_favorites(
    recipe_id: int,
    current_user: UserResponse = Depends(get_current_user),
    recipe_manager: RecipeManager = Depends(get_recipe_manager)
):
    """
    remove recipe from favorites
    """
    try:
        success = await recipe_manager.remove_from_favorites(recipe_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="recipe not in favorites"
            )
        
        logger.info(f"user {current_user.id} unfavorited recipe {recipe_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"error removing from favorites: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error removing from favorites"
        )


@router.get("/recipes/favorites/me", response_model=dict)
async def get_my_favorites(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserResponse = Depends(get_current_user),
    recipe_manager: RecipeManager = Depends(get_recipe_manager)
):
    """
    get current user's favorite recipes
    """
    try:
        recipes, total = await recipe_manager.get_user_favorites(
            current_user.id, limit, offset
        )
        
        return {
            "recipes": recipes,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total
        }
        
    except Exception as e:
        logger.error(f"error getting favorites: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error retrieving favorites"
        )

