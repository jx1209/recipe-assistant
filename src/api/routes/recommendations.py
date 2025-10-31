"""
recipe recommendation api endpoints
provides intelligent recipe recommendations
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional, Dict
import logging

from src.models.user import UserResponse
from src.services.recommendation_service import RecommendationService
from src.database import get_db
from src.auth.dependencies import get_current_user, get_current_user_optional
from src.config.settings import get_settings
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(tags=["recommendations"])
settings = get_settings()


class RecommendByIngredientsRequest(BaseModel):
    """request model for ingredient-based recommendations"""
    ingredients: List[str]
    limit: int = 10


def get_recommendation_service() -> RecommendationService:
    """dependency to get recommendation service"""
    db = get_db(settings.DATABASE_URL)
    return RecommendationService(db.conn)


@router.get("/recommendations/for-you", response_model=List[Dict])
async def get_personalized_recommendations(
    limit: int = Query(10, ge=1, le=50),
    exclude_viewed: bool = Query(False),
    current_user: UserResponse = Depends(get_current_user),
    rec_service: RecommendationService = Depends(get_recommendation_service)
):
    """
    get personalized recipe recommendations for the current user
    based on favorites, ratings, and dietary preferences
    """
    try:
        recommendations = await rec_service.get_recommendations_for_user(
            current_user.id,
            limit=limit,
            exclude_viewed=exclude_viewed
        )
        
        logger.info(f"generated {len(recommendations)} recommendations for user {current_user.id}")
        return recommendations
        
    except Exception as e:
        logger.error(f"error generating recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error generating recommendations"
        )


@router.get("/recommendations/similar/{recipe_id}", response_model=List[Dict])
async def get_similar_recipes(
    recipe_id: int,
    limit: int = Query(10, ge=1, le=50),
    rec_service: RecommendationService = Depends(get_recommendation_service)
):
    """
    find recipes similar to the given recipe
    based on cuisine, tags, ingredients, and difficulty
    """
    try:
        recommendations = await rec_service.get_similar_recipes(
            recipe_id,
            limit=limit
        )
        
        if not recommendations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="recipe not found or no similar recipes available"
            )
        
        logger.info(f"found {len(recommendations)} similar recipes for recipe {recipe_id}")
        return recommendations
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"error finding similar recipes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error finding similar recipes"
        )


@router.post("/recommendations/by-ingredients", response_model=List[Dict])
async def recommend_by_ingredients(
    request: RecommendByIngredientsRequest,
    rec_service: RecommendationService = Depends(get_recommendation_service)
):
    """
    recommend recipes based on available ingredients
    returns recipes that can be made with the provided ingredients
    """
    try:
        if not request.ingredients:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="at least one ingredient is required"
            )
        
        recommendations = await rec_service.get_recommendations_by_ingredients(
            request.ingredients,
            limit=request.limit
        )
        
        logger.info(f"found {len(recommendations)} recipes for {len(request.ingredients)} ingredients")
        return recommendations
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"error recommending by ingredients: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error generating recommendations"
        )


@router.get("/recommendations/by-pantry", response_model=List[Dict])
async def recommend_by_pantry(
    limit: int = Query(10, ge=1, le=50),
    current_user: UserResponse = Depends(get_current_user),
    rec_service: RecommendationService = Depends(get_recommendation_service)
):
    """
    recommend recipes based on user's pantry items
    finds recipes that can be made with available pantry ingredients
    """
    try:
        #get user's pantry
        db = get_db(settings.DATABASE_URL)
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT ingredient_name FROM user_pantry
            WHERE user_id = ?
        """, (current_user.id,))
        
        pantry_items = [row[0] for row in cursor.fetchall()]
        
        if not pantry_items:
            return []
        
        recommendations = await rec_service.get_recommendations_by_ingredients(
            pantry_items,
            limit=limit
        )
        
        logger.info(f"found {len(recommendations)} recipes for user's pantry ({len(pantry_items)} items)")
        return recommendations
        
    except Exception as e:
        logger.error(f"error recommending by pantry: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error generating pantry-based recommendations"
        )


@router.get("/recommendations/trending", response_model=List[Dict])
async def get_trending_recipes(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(10, ge=1, le=50),
    rec_service: RecommendationService = Depends(get_recommendation_service)
):
    """
    get trending recipes based on recent activity
    shows popular recipes with high views, favorites, and ratings
    """
    try:
        recommendations = await rec_service.get_trending_recipes(
            days=days,
            limit=limit
        )
        
        logger.info(f"retrieved {len(recommendations)} trending recipes")
        return recommendations
        
    except Exception as e:
        logger.error(f"error getting trending recipes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error retrieving trending recipes"
        )


@router.get("/recommendations/quick", response_model=List[Dict])
async def get_quick_recipes(
    max_time: int = Query(30, ge=5, le=60),
    limit: int = Query(10, ge=1, le=50),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional)
):
    """
    get quick recipe recommendations
    finds highly-rated recipes that can be made quickly
    """
    try:
        db = get_db(settings.DATABASE_URL)
        cursor = db.conn.cursor()
        
        cursor.execute("""
            SELECT r.*,
                (SELECT AVG(rating) FROM recipe_ratings WHERE recipe_id = r.id) as avg_rating,
                (SELECT COUNT(*) FROM recipe_ratings WHERE recipe_id = r.id) as rating_count
            FROM recipes r
            WHERE r.is_deleted = 0
            AND (r.total_time_minutes <= ? OR r.total_time_minutes IS NULL)
            AND (
                SELECT AVG(rating) FROM recipe_ratings WHERE recipe_id = r.id
            ) >= 3.5
            ORDER BY avg_rating DESC, rating_count DESC
            LIMIT ?
        """, (max_time, limit))
        
        recipes = cursor.fetchall()
        
        results = []
        for recipe in recipes:
            results.append({
                'id': recipe['id'],
                'title': recipe['title'],
                'description': recipe['description'],
                'image_url': recipe['image_url'],
                'cuisine': recipe['cuisine'],
                'difficulty': recipe['difficulty'],
                'total_time_minutes': recipe['total_time_minutes'],
                'average_rating': round(recipe['avg_rating'], 2) if recipe['avg_rating'] else None,
                'rating_count': recipe['rating_count']
            })
        
        logger.info(f"found {len(results)} quick recipes (max {max_time} minutes)")
        return results
        
    except Exception as e:
        logger.error(f"error getting quick recipes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error retrieving quick recipes"
        )

