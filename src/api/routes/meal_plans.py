"""
meal planning api endpoints
handles meal plan crud operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
import logging

from src.models.meal_plan import (
    MealPlanCreate, MealPlanUpdate, MealPlanResponse, MealPlanSummary
)
from src.models.user import UserResponse
from src.services.meal_planner import MealPlannerService
from src.database import get_db
from src.auth.dependencies import get_current_user
from src.config.settings import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["meal_plans"])
settings = get_settings()


def get_meal_planner() -> MealPlannerService:
    """dependency to get meal planner service"""
    db = get_db(settings.DATABASE_URL)
    return MealPlannerService(db.conn)


@router.post("/meal-plans", response_model=MealPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_meal_plan(
    plan_data: MealPlanCreate,
    current_user: UserResponse = Depends(get_current_user),
    meal_planner: MealPlannerService = Depends(get_meal_planner)
):
    """
    create new meal plan
    """
    try:
        plan = await meal_planner.create_meal_plan(plan_data, current_user.id)
        logger.info(f"user {current_user.id} created meal plan {plan.id}")
        return plan
        
    except Exception as e:
        logger.error(f"error creating meal plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error creating meal plan"
        )


@router.get("/meal-plans/{plan_id}", response_model=MealPlanResponse)
async def get_meal_plan(
    plan_id: int,
    current_user: UserResponse = Depends(get_current_user),
    meal_planner: MealPlannerService = Depends(get_meal_planner)
):
    """
    get meal plan by id
    """
    try:
        plan = await meal_planner.get_meal_plan(plan_id, current_user.id)
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="meal plan not found"
            )
        
        return plan
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"error getting meal plan {plan_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error retrieving meal plan"
        )


@router.put("/meal-plans/{plan_id}", response_model=MealPlanResponse)
async def update_meal_plan(
    plan_id: int,
    plan_data: MealPlanUpdate,
    current_user: UserResponse = Depends(get_current_user),
    meal_planner: MealPlannerService = Depends(get_meal_planner)
):
    """
    update meal plan (owner only)
    """
    try:
        plan = await meal_planner.update_meal_plan(plan_id, plan_data, current_user.id)
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="meal plan not found"
            )
        
        logger.info(f"user {current_user.id} updated meal plan {plan_id}")
        return plan
        
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you do not have permission to update this meal plan"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"error updating meal plan {plan_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error updating meal plan"
        )


@router.delete("/meal-plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meal_plan(
    plan_id: int,
    current_user: UserResponse = Depends(get_current_user),
    meal_planner: MealPlannerService = Depends(get_meal_planner)
):
    """
    delete meal plan (owner only)
    """
    try:
        deleted = await meal_planner.delete_meal_plan(plan_id, current_user.id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="meal plan not found"
            )
        
        logger.info(f"user {current_user.id} deleted meal plan {plan_id}")
        
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you do not have permission to delete this meal plan"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"error deleting meal plan {plan_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error deleting meal plan"
        )


@router.get("/meal-plans", response_model=dict)
async def get_meal_plans(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    active_only: bool = Query(False),
    current_user: UserResponse = Depends(get_current_user),
    meal_planner: MealPlannerService = Depends(get_meal_planner)
):
    """
    get current user's meal plans
    """
    try:
        plans, total = await meal_planner.get_user_meal_plans(
            current_user.id, limit, offset, active_only
        )
        
        return {
            "meal_plans": plans,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total
        }
        
    except Exception as e:
        logger.error(f"error getting meal plans: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error retrieving meal plans"
        )


@router.get("/meal-plans/current/me", response_model=MealPlanResponse)
async def get_current_meal_plan(
    current_user: UserResponse = Depends(get_current_user),
    meal_planner: MealPlannerService = Depends(get_meal_planner)
):
    """
    get current user's active meal plan (today's date within range)
    """
    try:
        plan = await meal_planner.get_current_meal_plan(current_user.id)
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="no active meal plan found"
            )
        
        return plan
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"error getting current meal plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error retrieving current meal plan"
        )

