"""
shopping list api endpoints
handles shopping list crud and auto-generation
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
import logging

from src.models.shopping_list import (
    ShoppingListCreate, ShoppingListUpdate, ShoppingListResponse,
    ShoppingListSummary
)
from src.models.user import UserResponse
from src.services.shopping_list_service import ShoppingListService
from src.database import get_db
from src.auth.dependencies import get_current_user
from src.config.settings import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["shopping_lists"])
settings = get_settings()


def get_shopping_list_service() -> ShoppingListService:
    """dependency to get shopping list service"""
    db = get_db(settings.DATABASE_URL)
    return ShoppingListService(db.conn)


@router.post("/shopping-lists", response_model=ShoppingListResponse, status_code=status.HTTP_201_CREATED)
async def create_shopping_list(
    list_data: ShoppingListCreate,
    current_user: UserResponse = Depends(get_current_user),
    shopping_service: ShoppingListService = Depends(get_shopping_list_service)
):
    """
    create shopping list
    auto-generates from meal plans or recipes
    """
    try:
        shopping_list = await shopping_service.create_shopping_list(list_data, current_user.id)
        logger.info(f"user {current_user.id} created shopping list {shopping_list.id}")
        return shopping_list
        
    except Exception as e:
        logger.error(f"error creating shopping list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error creating shopping list"
        )


@router.get("/shopping-lists/{list_id}", response_model=ShoppingListResponse)
async def get_shopping_list(
    list_id: int,
    current_user: UserResponse = Depends(get_current_user),
    shopping_service: ShoppingListService = Depends(get_shopping_list_service)
):
    """
    get shopping list by id
    """
    try:
        shopping_list = await shopping_service.get_shopping_list(list_id, current_user.id)
        
        if not shopping_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="shopping list not found"
            )
        
        return shopping_list
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"error getting shopping list {list_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error retrieving shopping list"
        )


@router.put("/shopping-lists/{list_id}", response_model=ShoppingListResponse)
async def update_shopping_list(
    list_id: int,
    list_data: ShoppingListUpdate,
    current_user: UserResponse = Depends(get_current_user),
    shopping_service: ShoppingListService = Depends(get_shopping_list_service)
):
    """
    update shopping list (owner only)
    typically used to check off items
    """
    try:
        shopping_list = await shopping_service.update_shopping_list(list_id, list_data, current_user.id)
        
        if not shopping_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="shopping list not found"
            )
        
        logger.info(f"user {current_user.id} updated shopping list {list_id}")
        return shopping_list
        
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you do not have permission to update this shopping list"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"error updating shopping list {list_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error updating shopping list"
        )


@router.delete("/shopping-lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_list(
    list_id: int,
    current_user: UserResponse = Depends(get_current_user),
    shopping_service: ShoppingListService = Depends(get_shopping_list_service)
):
    """
    delete shopping list (owner only)
    """
    try:
        deleted = await shopping_service.delete_shopping_list(list_id, current_user.id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="shopping list not found"
            )
        
        logger.info(f"user {current_user.id} deleted shopping list {list_id}")
        
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you do not have permission to delete this shopping list"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"error deleting shopping list {list_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error deleting shopping list"
        )


@router.get("/shopping-lists", response_model=dict)
async def get_shopping_lists(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserResponse = Depends(get_current_user),
    shopping_service: ShoppingListService = Depends(get_shopping_list_service)
):
    """
    get current user's shopping lists
    """
    try:
        lists, total = await shopping_service.get_user_shopping_lists(
            current_user.id, limit, offset
        )
        
        return {
            "shopping_lists": lists,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total
        }
        
    except Exception as e:
        logger.error(f"error getting shopping lists: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error retrieving shopping lists"
        )

