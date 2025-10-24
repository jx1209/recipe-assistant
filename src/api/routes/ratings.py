"""
rating and review api endpoints
handles recipe ratings and reviews
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
import logging

from src.models.rating import (
    RatingCreate, RatingUpdate, RatingResponse, RatingSummary
)
from src.models.user import UserResponse
from src.services.rating_manager import RatingManager
from src.database import get_db
from src.auth.dependencies import get_current_user
from src.config.settings import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["ratings"])
settings = get_settings()


def get_rating_manager() -> RatingManager:
    """dependency to get rating manager"""
    db = get_db(settings.DATABASE_URL)
    return RatingManager(db.conn)


@router.post("/recipes/{recipe_id}/ratings", response_model=RatingResponse)
async def create_or_update_rating(
    recipe_id: int,
    rating_data: RatingCreate,
    current_user: UserResponse = Depends(get_current_user),
    rating_manager: RatingManager = Depends(get_rating_manager)
):
    """
    create or update rating for recipe
    user can only have one rating per recipe
    """
    try:
        rating = await rating_manager.create_or_update_rating(
            recipe_id, current_user.id, rating_data
        )
        
        logger.info(f"user {current_user.id} rated recipe {recipe_id}: {rating_data.rating} stars")
        return rating
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"error creating/updating rating: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error saving rating"
        )


@router.get("/recipes/{recipe_id}/ratings", response_model=dict)
async def get_recipe_ratings(
    recipe_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    min_rating: Optional[int] = Query(None, ge=1, le=5),
    rating_manager: RatingManager = Depends(get_rating_manager)
):
    """
    get all ratings for recipe
    returns paginated results
    """
    try:
        ratings, total = await rating_manager.get_recipe_ratings(
            recipe_id, limit, offset, min_rating
        )
        
        return {
            "ratings": ratings,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total
        }
        
    except Exception as e:
        logger.error(f"error getting ratings for recipe {recipe_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error retrieving ratings"
        )


@router.get("/recipes/{recipe_id}/ratings/summary", response_model=RatingSummary)
async def get_recipe_rating_summary(
    recipe_id: int,
    rating_manager: RatingManager = Depends(get_rating_manager)
):
    """
    get rating summary/statistics for recipe
    includes average rating and distribution
    """
    try:
        summary = await rating_manager.get_recipe_rating_summary(recipe_id)
        return summary
        
    except Exception as e:
        logger.error(f"error getting rating summary for recipe {recipe_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error retrieving rating summary"
        )


@router.get("/recipes/{recipe_id}/ratings/me", response_model=RatingResponse)
async def get_my_rating(
    recipe_id: int,
    current_user: UserResponse = Depends(get_current_user),
    rating_manager: RatingManager = Depends(get_rating_manager)
):
    """
    get current user's rating for recipe
    """
    try:
        rating = await rating_manager.get_user_rating_for_recipe(
            recipe_id, current_user.id
        )
        
        if not rating:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="no rating found"
            )
        
        return rating
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"error getting user rating: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error retrieving rating"
        )


@router.delete("/ratings/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rating(
    rating_id: int,
    current_user: UserResponse = Depends(get_current_user),
    rating_manager: RatingManager = Depends(get_rating_manager)
):
    """
    delete rating (only by creator)
    """
    try:
        deleted = await rating_manager.delete_rating(rating_id, current_user.id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="rating not found"
            )
        
        logger.info(f"user {current_user.id} deleted rating {rating_id}")
        
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you do not have permission to delete this rating"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"error deleting rating {rating_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error deleting rating"
        )

