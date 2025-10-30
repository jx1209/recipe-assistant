"""
meal planner service
handles meal plan crud operations and smart meal planning
"""

import sqlite3
import json
import logging
from typing import Optional, List, Tuple
from datetime import datetime, date, timedelta
from src.models.meal_plan import (
    MealPlanCreate, MealPlanUpdate, MealPlanResponse, MealPlanSummary,
    DayPlan, DayMeal
)

logger = logging.getLogger(__name__)


class MealPlannerService:
    """manages meal plan database operations"""
    
    def __init__(self, db_connection: sqlite3.Connection):
        self.conn = db_connection
        self.conn.row_factory = sqlite3.Row
    
    async def create_meal_plan(
        self,
        plan_data: MealPlanCreate,
        user_id: int
    ) -> MealPlanResponse:
        """
        create new meal plan
        
        args:
            plan_data: meal plan creation data
            user_id: user creating plan
            
        returns:
            created meal plan
        """
        try:
            cursor = self.conn.cursor()
            
            #serialize days to json
            meals_json = self._serialize_days(plan_data.days)
            
            #insert meal plan
            cursor.execute("""
                INSERT INTO meal_plans (
                    user_id, plan_name, start_date, end_date,
                    meals_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                plan_data.name,
                plan_data.start_date.isoformat(),
                plan_data.end_date.isoformat(),
                meals_json,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            plan_id = cursor.lastrowid
            self.conn.commit()
            
            logger.info(f"created meal plan {plan_id} for user {user_id}")
            
            #fetch and return created plan
            return await self.get_meal_plan(plan_id, user_id)
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"error creating meal plan: {e}")
            raise
    
    async def get_meal_plan(
        self,
        plan_id: int,
        user_id: int
    ) -> Optional[MealPlanResponse]:
        """
        get meal plan by id
        
        args:
            plan_id: meal plan id
            user_id: requesting user id (for ownership check)
            
        returns:
            meal plan or none if not found/unauthorized
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                SELECT * FROM meal_plans
                WHERE id = ? AND user_id = ?
            """, (plan_id, user_id))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            #deserialize days
            days = self._deserialize_days(row['meals_json'])
            
            #calculate totals
            total_recipes = sum(
                1 for day in days
                for meal_type in ['breakfast', 'lunch', 'dinner', 'snacks']
                for _ in (getattr(day, meal_type) if meal_type != 'snacks' else day.snacks)
                if getattr(day, meal_type) is not None
            )
            
            total_days = len(days)
            
            plan = MealPlanResponse(
                id=row['id'],
                user_id=row['user_id'],
                name=row['plan_name'],
                start_date=date.fromisoformat(row['start_date']),
                end_date=date.fromisoformat(row['end_date']),
                days=days,
                notes=None,  #not stored in current schema
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']),
                total_recipes=total_recipes,
                total_days=total_days
            )
            
            return plan
            
        except Exception as e:
            logger.error(f"error getting meal plan {plan_id}: {e}")
            raise
    
    async def update_meal_plan(
        self,
        plan_id: int,
        plan_data: MealPlanUpdate,
        user_id: int
    ) -> Optional[MealPlanResponse]:
        """
        update meal plan
        
        args:
            plan_id: plan to update
            plan_data: updated data
            user_id: user performing update (must be owner)
            
        returns:
            updated plan or none if not found/unauthorized
        """
        try:
            cursor = self.conn.cursor()
            
            #check ownership
            cursor.execute("""
                SELECT user_id FROM meal_plans WHERE id = ?
            """, (plan_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            if row['user_id'] != user_id:
                raise PermissionError("user does not own this meal plan")
            
            #build update query
            updates = []
            params = []
            
            if plan_data.name is not None:
                updates.append("plan_name = ?")
                params.append(plan_data.name)
            
            if plan_data.start_date is not None:
                updates.append("start_date = ?")
                params.append(plan_data.start_date.isoformat())
            
            if plan_data.end_date is not None:
                updates.append("end_date = ?")
                params.append(plan_data.end_date.isoformat())
            
            if plan_data.days is not None:
                updates.append("meals_json = ?")
                params.append(self._serialize_days(plan_data.days))
            
            #always update timestamp
            updates.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            
            if updates:
                params.append(plan_id)
                query = f"UPDATE meal_plans SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, params)
                self.conn.commit()
            
            logger.info(f"updated meal plan {plan_id}")
            
            return await self.get_meal_plan(plan_id, user_id)
            
        except PermissionError:
            raise
        except Exception as e:
            self.conn.rollback()
            logger.error(f"error updating meal plan {plan_id}: {e}")
            raise
    
    async def delete_meal_plan(
        self,
        plan_id: int,
        user_id: int
    ) -> bool:
        """
        delete meal plan
        
        args:
            plan_id: plan to delete
            user_id: user performing deletion (must be owner)
            
        returns:
            true if deleted, false if not found/unauthorized
        """
        try:
            cursor = self.conn.cursor()
            
            #check ownership
            cursor.execute("""
                SELECT user_id FROM meal_plans WHERE id = ?
            """, (plan_id,))
            row = cursor.fetchone()
            
            if not row:
                return False
            
            if row['user_id'] != user_id:
                raise PermissionError("user does not own this meal plan")
            
            cursor.execute("DELETE FROM meal_plans WHERE id = ?", (plan_id,))
            self.conn.commit()
            
            logger.info(f"deleted meal plan {plan_id}")
            return True
            
        except PermissionError:
            raise
        except Exception as e:
            self.conn.rollback()
            logger.error(f"error deleting meal plan {plan_id}: {e}")
            raise
    
    async def get_user_meal_plans(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
        active_only: bool = False
    ) -> Tuple[List[MealPlanSummary], int]:
        """
        get user's meal plans
        
        args:
            user_id: user id
            limit: max results
            offset: pagination offset
            active_only: only return active plans (current or future)
            
        returns:
            tuple of (meal plans, total count)
        """
        try:
            cursor = self.conn.cursor()
            
            #build where clause
            where_clause = "user_id = ?"
            params = [user_id]
            
            if active_only:
                today = date.today().isoformat()
                where_clause += " AND end_date >= ?"
                params.append(today)
            
            #get total count
            cursor.execute(f"""
                SELECT COUNT(*) as count FROM meal_plans
                WHERE {where_clause}
            """, params)
            total_count = cursor.fetchone()['count']
            
            #get plans
            params.extend([limit, offset])
            cursor.execute(f"""
                SELECT * FROM meal_plans
                WHERE {where_clause}
                ORDER BY start_date DESC
                LIMIT ? OFFSET ?
            """, params)
            rows = cursor.fetchall()
            
            plans = []
            for row in rows:
                #deserialize to count recipes
                days = self._deserialize_days(row['meals_json'])
                total_recipes = sum(
                    1 for day in days
                    for meal_type in ['breakfast', 'lunch', 'dinner', 'snacks']
                    for _ in (getattr(day, meal_type) if meal_type != 'snacks' else day.snacks)
                    if getattr(day, meal_type) is not None
                )
                
                plan = MealPlanSummary(
                    id=row['id'],
                    name=row['plan_name'],
                    start_date=date.fromisoformat(row['start_date']),
                    end_date=date.fromisoformat(row['end_date']),
                    total_days=len(days),
                    total_recipes=total_recipes,
                    created_at=datetime.fromisoformat(row['created_at'])
                )
                plans.append(plan)
            
            return plans, total_count
            
        except Exception as e:
            logger.error(f"error getting meal plans for user {user_id}: {e}")
            raise
    
    async def get_current_meal_plan(
        self,
        user_id: int
    ) -> Optional[MealPlanResponse]:
        """
        get user's current active meal plan (today's date within range)
        """
        try:
            cursor = self.conn.cursor()
            today = date.today().isoformat()
            
            cursor.execute("""
                SELECT * FROM meal_plans
                WHERE user_id = ?
                AND start_date <= ?
                AND end_date >= ?
                ORDER BY start_date DESC
                LIMIT 1
            """, (user_id, today, today))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return await self.get_meal_plan(row['id'], user_id)
            
        except Exception as e:
            logger.error(f"error getting current meal plan for user {user_id}: {e}")
            raise
    
    def _serialize_days(self, days: List[DayPlan]) -> str:
        """serialize day plans to json"""
        meals_dict = {}
        
        for day in days:
            day_key = day.date.isoformat()
            meals_dict[day_key] = {}
            
            if day.breakfast:
                meals_dict[day_key]['breakfast'] = {
                    'recipe_id': day.breakfast.recipe_id,
                    'servings': day.breakfast.servings,
                    'notes': day.breakfast.notes
                }
            
            if day.lunch:
                meals_dict[day_key]['lunch'] = {
                    'recipe_id': day.lunch.recipe_id,
                    'servings': day.lunch.servings,
                    'notes': day.lunch.notes
                }
            
            if day.dinner:
                meals_dict[day_key]['dinner'] = {
                    'recipe_id': day.dinner.recipe_id,
                    'servings': day.dinner.servings,
                    'notes': day.dinner.notes
                }
            
            if day.snacks:
                meals_dict[day_key]['snacks'] = [
                    {
                        'recipe_id': snack.recipe_id,
                        'servings': snack.servings,
                        'notes': snack.notes
                    }
                    for snack in day.snacks
                ]
        
        return json.dumps(meals_dict)
    
    def _deserialize_days(self, meals_json: str) -> List[DayPlan]:
        """deserialize json to day plans"""
        meals_dict = json.loads(meals_json)
        days = []
        
        for day_key, day_meals in meals_dict.items():
            day_date = date.fromisoformat(day_key)
            
            breakfast = None
            if 'breakfast' in day_meals:
                meal_data = day_meals['breakfast']
                breakfast = DayMeal(
                    meal_type='breakfast',
                    recipe_id=meal_data['recipe_id'],
                    servings=meal_data.get('servings', 1.0),
                    notes=meal_data.get('notes')
                )
            
            lunch = None
            if 'lunch' in day_meals:
                meal_data = day_meals['lunch']
                lunch = DayMeal(
                    meal_type='lunch',
                    recipe_id=meal_data['recipe_id'],
                    servings=meal_data.get('servings', 1.0),
                    notes=meal_data.get('notes')
                )
            
            dinner = None
            if 'dinner' in day_meals:
                meal_data = day_meals['dinner']
                dinner = DayMeal(
                    meal_type='dinner',
                    recipe_id=meal_data['recipe_id'],
                    servings=meal_data.get('servings', 1.0),
                    notes=meal_data.get('notes')
                )
            
            snacks = []
            if 'snacks' in day_meals:
                for snack_data in day_meals['snacks']:
                    snacks.append(DayMeal(
                        meal_type='snack',
                        recipe_id=snack_data['recipe_id'],
                        servings=snack_data.get('servings', 1.0),
                        notes=snack_data.get('notes')
                    ))
            
            day_plan = DayPlan(
                date=day_date,
                breakfast=breakfast,
                lunch=lunch,
                dinner=dinner,
                snacks=snacks
            )
            days.append(day_plan)
        
        #sort by date
        days.sort(key=lambda d: d.date)
        return days

