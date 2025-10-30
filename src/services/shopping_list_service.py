"""
shopping list service
handles shopping list crud and auto-generation from meal plans/recipes
"""

import sqlite3
import json
import logging
from typing import Optional, List, Tuple, Dict
from datetime import datetime
from collections import defaultdict
from src.models.shopping_list import (
    ShoppingListCreate, ShoppingListUpdate, ShoppingListResponse,
    ShoppingListSummary, ShoppingItem
)

logger = logging.getLogger(__name__)


class ShoppingListService:
    """manages shopping list operations"""
    
    def __init__(self, db_connection: sqlite3.Connection):
        self.conn = db_connection
        self.conn.row_factory = sqlite3.Row
        
        #ingredient categories for organization
        self.categories = {
            'produce': ['vegetable', 'fruit', 'lettuce', 'tomato', 'onion', 'garlic', 'potato', 'carrot', 'apple', 'banana'],
            'meat': ['chicken', 'beef', 'pork', 'fish', 'turkey', 'lamb', 'bacon', 'sausage'],
            'dairy': ['milk', 'cheese', 'butter', 'yogurt', 'cream', 'egg'],
            'grains': ['rice', 'pasta', 'bread', 'flour', 'oat', 'quinoa', 'cereal'],
            'canned': ['canned', 'can', 'jar', 'jarred'],
            'spices': ['salt', 'pepper', 'spice', 'herb', 'oregano', 'basil', 'thyme', 'cumin'],
            'condiments': ['sauce', 'oil', 'vinegar', 'ketchup', 'mustard', 'mayo'],
            'frozen': ['frozen'],
            'beverages': ['juice', 'coffee', 'tea', 'soda', 'water'],
            'bakery': ['cake', 'cookie', 'pastry', 'muffin'],
            'snacks': ['chip', 'cracker', 'nut', 'snack']
        }
    
    async def create_shopping_list(
        self,
        list_data: ShoppingListCreate,
        user_id: int
    ) -> ShoppingListResponse:
        """
        create shopping list with auto-generation from recipes/meal plan
        
        args:
            list_data: shopping list creation data
            user_id: user creating list
            
        returns:
            created shopping list
        """
        try:
            cursor = self.conn.cursor()
            
            #collect ingredients from all sources
            all_items = []
            
            #from meal plan
            if list_data.meal_plan_id:
                plan_items = await self._get_items_from_meal_plan(list_data.meal_plan_id, user_id)
                all_items.extend(plan_items)
            
            #from individual recipes
            if list_data.recipe_ids:
                recipe_items = await self._get_items_from_recipes(list_data.recipe_ids)
                all_items.extend(recipe_items)
            
            #add custom items
            if list_data.custom_items:
                all_items.extend(list_data.custom_items)
            
            #consolidate and organize items
            consolidated_items = self._consolidate_items(all_items)
            
            #exclude pantry items if requested
            if list_data.exclude_pantry:
                consolidated_items = await self._exclude_pantry_items(consolidated_items, user_id)
            
            #categorize items if requested
            if list_data.group_by_category:
                consolidated_items = self._categorize_items(consolidated_items)
            
            #serialize items
            items_json = json.dumps([item.model_dump() for item in consolidated_items])
            
            #insert shopping list
            cursor.execute("""
                INSERT INTO shopping_lists (
                    user_id, list_name, items_json, meal_plan_id,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                list_data.name,
                items_json,
                list_data.meal_plan_id,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            list_id = cursor.lastrowid
            self.conn.commit()
            
            logger.info(f"created shopping list {list_id} with {len(consolidated_items)} items")
            
            return await self.get_shopping_list(list_id, user_id)
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"error creating shopping list: {e}")
            raise
    
    async def get_shopping_list(
        self,
        list_id: int,
        user_id: int
    ) -> Optional[ShoppingListResponse]:
        """get shopping list by id"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                SELECT * FROM shopping_lists
                WHERE id = ? AND user_id = ?
            """, (list_id, user_id))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            #deserialize items
            items = [ShoppingItem(**item) for item in json.loads(row['items_json'])]
            
            #calculate stats
            total_items = len(items)
            checked_items = sum(1 for item in items if item.checked)
            categories = list(set(item.category for item in items if item.category))
            
            shopping_list = ShoppingListResponse(
                id=row['id'],
                user_id=row['user_id'],
                name=row['list_name'],
                items=items,
                meal_plan_id=row['meal_plan_id'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']),
                total_items=total_items,
                checked_items=checked_items,
                categories=sorted(categories)
            )
            
            return shopping_list
            
        except Exception as e:
            logger.error(f"error getting shopping list {list_id}: {e}")
            raise
    
    async def update_shopping_list(
        self,
        list_id: int,
        list_data: ShoppingListUpdate,
        user_id: int
    ) -> Optional[ShoppingListResponse]:
        """update shopping list"""
        try:
            cursor = self.conn.cursor()
            
            #check ownership
            cursor.execute("""
                SELECT user_id FROM shopping_lists WHERE id = ?
            """, (list_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            if row['user_id'] != user_id:
                raise PermissionError("user does not own this shopping list")
            
            #build update
            updates = []
            params = []
            
            if list_data.name is not None:
                updates.append("list_name = ?")
                params.append(list_data.name)
            
            if list_data.items is not None:
                updates.append("items_json = ?")
                params.append(json.dumps([item.model_dump() for item in list_data.items]))
            
            updates.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            
            if updates:
                params.append(list_id)
                query = f"UPDATE shopping_lists SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, params)
                self.conn.commit()
            
            logger.info(f"updated shopping list {list_id}")
            
            return await self.get_shopping_list(list_id, user_id)
            
        except PermissionError:
            raise
        except Exception as e:
            self.conn.rollback()
            logger.error(f"error updating shopping list {list_id}: {e}")
            raise
    
    async def delete_shopping_list(
        self,
        list_id: int,
        user_id: int
    ) -> bool:
        """delete shopping list"""
        try:
            cursor = self.conn.cursor()
            
            #check ownership
            cursor.execute("""
                SELECT user_id FROM shopping_lists WHERE id = ?
            """, (list_id,))
            row = cursor.fetchone()
            
            if not row:
                return False
            
            if row['user_id'] != user_id:
                raise PermissionError("user does not own this shopping list")
            
            cursor.execute("DELETE FROM shopping_lists WHERE id = ?", (list_id,))
            self.conn.commit()
            
            logger.info(f"deleted shopping list {list_id}")
            return True
            
        except PermissionError:
            raise
        except Exception as e:
            self.conn.rollback()
            logger.error(f"error deleting shopping list {list_id}: {e}")
            raise
    
    async def get_user_shopping_lists(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[ShoppingListSummary], int]:
        """get user's shopping lists"""
        try:
            cursor = self.conn.cursor()
            
            #get total count
            cursor.execute("""
                SELECT COUNT(*) as count FROM shopping_lists
                WHERE user_id = ?
            """, (user_id,))
            total_count = cursor.fetchone()['count']
            
            #get lists
            cursor.execute("""
                SELECT * FROM shopping_lists
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (user_id, limit, offset))
            rows = cursor.fetchall()
            
            lists = []
            for row in rows:
                items = [ShoppingItem(**item) for item in json.loads(row['items_json'])]
                total_items = len(items)
                checked_items = sum(1 for item in items if item.checked)
                
                shopping_list = ShoppingListSummary(
                    id=row['id'],
                    name=row['list_name'],
                    total_items=total_items,
                    checked_items=checked_items,
                    created_at=datetime.fromisoformat(row['created_at'])
                )
                lists.append(shopping_list)
            
            return lists, total_count
            
        except Exception as e:
            logger.error(f"error getting shopping lists for user {user_id}: {e}")
            raise
    
    async def _get_items_from_meal_plan(
        self,
        meal_plan_id: int,
        user_id: int
    ) -> List[ShoppingItem]:
        """extract ingredients from all recipes in meal plan"""
        try:
            cursor = self.conn.cursor()
            
            #get meal plan
            cursor.execute("""
                SELECT meals_json FROM meal_plans
                WHERE id = ? AND user_id = ?
            """, (meal_plan_id, user_id))
            row = cursor.fetchone()
            
            if not row:
                return []
            
            #parse meal plan
            meals = json.loads(row['meals_json'])
            recipe_ids = set()
            
            #collect all recipe ids
            for day_meals in meals.values():
                for meal_type in ['breakfast', 'lunch', 'dinner']:
                    if meal_type in day_meals:
                        recipe_ids.add(day_meals[meal_type]['recipe_id'])
                if 'snacks' in day_meals:
                    for snack in day_meals['snacks']:
                        recipe_ids.add(snack['recipe_id'])
            
            #get ingredients from all recipes
            return await self._get_items_from_recipes(list(recipe_ids))
            
        except Exception as e:
            logger.error(f"error getting items from meal plan {meal_plan_id}: {e}")
            return []
    
    async def _get_items_from_recipes(
        self,
        recipe_ids: List[int]
    ) -> List[ShoppingItem]:
        """extract ingredients from recipes"""
        if not recipe_ids:
            return []
        
        try:
            cursor = self.conn.cursor()
            
            placeholders = ','.join(['?' for _ in recipe_ids])
            cursor.execute(f"""
                SELECT ingredients_json FROM recipes
                WHERE id IN ({placeholders}) AND is_deleted = 0
            """, recipe_ids)
            rows = cursor.fetchall()
            
            items = []
            for row in rows:
                ingredients = json.loads(row['ingredients_json'])
                for ing in ingredients:
                    items.append(ShoppingItem(
                        ingredient=ing['name'],
                        quantity=ing.get('quantity'),
                        unit=ing.get('unit'),
                        checked=False
                    ))
            
            return items
            
        except Exception as e:
            logger.error(f"error getting items from recipes: {e}")
            return []
    
    def _consolidate_items(self, items: List[ShoppingItem]) -> List[ShoppingItem]:
        """combine duplicate ingredients"""
        consolidated = defaultdict(lambda: {'quantity': 0, 'unit': None, 'notes': []})
        
        for item in items:
            key = item.ingredient.lower()
            
            #add quantities if same unit or no unit
            if item.quantity:
                if consolidated[key]['unit'] is None or consolidated[key]['unit'] == item.unit:
                    consolidated[key]['quantity'] += item.quantity
                    consolidated[key]['unit'] = item.unit
                else:
                    #different units - can't consolidate quantity
                    if item.notes:
                        consolidated[key]['notes'].append(item.notes)
            
            if item.notes and item.notes not in consolidated[key]['notes']:
                consolidated[key]['notes'].append(item.notes)
        
        #convert back to shopping items
        result = []
        for ingredient, data in consolidated.items():
            result.append(ShoppingItem(
                ingredient=ingredient,
                quantity=data['quantity'] if data['quantity'] > 0 else None,
                unit=data['unit'],
                checked=False,
                notes='; '.join(data['notes']) if data['notes'] else None
            ))
        
        return sorted(result, key=lambda x: x.ingredient)
    
    async def _exclude_pantry_items(
        self,
        items: List[ShoppingItem],
        user_id: int
    ) -> List[ShoppingItem]:
        """remove items user already has in pantry"""
        try:
            cursor = self.conn.cursor()
            
            #get user's pantry items
            cursor.execute("""
                SELECT LOWER(ingredient_name) as name FROM user_pantry
                WHERE user_id = ?
            """, (user_id,))
            pantry_items = set(row['name'] for row in cursor.fetchall())
            
            #filter out pantry items
            return [item for item in items if item.ingredient.lower() not in pantry_items]
            
        except Exception as e:
            logger.error(f"error excluding pantry items: {e}")
            return items  #return all items on error
    
    def _categorize_items(self, items: List[ShoppingItem]) -> List[ShoppingItem]:
        """assign categories to items for organization"""
        for item in items:
            if not item.category:
                item.category = self._get_category(item.ingredient)
        
        return sorted(items, key=lambda x: (x.category or 'other', x.ingredient))
    
    def _get_category(self, ingredient: str) -> str:
        """determine category for ingredient"""
        ingredient_lower = ingredient.lower()
        
        for category, keywords in self.categories.items():
            if any(keyword in ingredient_lower for keyword in keywords):
                return category
        
        return 'other'

