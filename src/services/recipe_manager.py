"""
recipe manager service
handles all recipe crud operations with database
"""

import sqlite3
import json
import logging
from typing import Optional, List, Dict, Tuple
from datetime import datetime
from src.models.recipe import (
    RecipeCreate, RecipeUpdate, RecipeResponse, RecipeSummary,
    RecipeSearch, RecipeIngredient, RecipeNutrition
)

logger = logging.getLogger(__name__)


class RecipeManager:
    """manages recipe database operations"""
    
    def __init__(self, db_connection: sqlite3.Connection):
        self.conn = db_connection
        self.conn.row_factory = sqlite3.Row
    
    async def create_recipe(
        self,
        recipe_data: RecipeCreate,
        user_id: Optional[int] = None
    ) -> RecipeResponse:
        """
        create new recipe in database
        
        args:
            recipe_data: recipe creation data
            user_id: id of user creating recipe (optional)
            
        returns:
            created recipe with id
        """
        try:
            #serialize json fields
            ingredients_json = json.dumps([ing.model_dump() for ing in recipe_data.ingredients])
            instructions_json = json.dumps(recipe_data.instructions)
            nutrition_json = json.dumps(recipe_data.nutrition.model_dump()) if recipe_data.nutrition else None
            
            #calculate total time
            total_time = None
            if recipe_data.prep_time_minutes and recipe_data.cook_time_minutes:
                total_time = recipe_data.prep_time_minutes + recipe_data.cook_time_minutes
            elif recipe_data.prep_time_minutes:
                total_time = recipe_data.prep_time_minutes
            elif recipe_data.cook_time_minutes:
                total_time = recipe_data.cook_time_minutes
            
            #insert recipe
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO recipes (
                    title, description, source_url, source_name,
                    ingredients_json, instructions_json, nutrition_json,
                    image_url, prep_time_minutes, cook_time_minutes,
                    total_time_minutes, servings, difficulty, cuisine,
                    created_by, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                recipe_data.title,
                recipe_data.description,
                str(recipe_data.source_url) if recipe_data.source_url else None,
                recipe_data.source_name,
                ingredients_json,
                instructions_json,
                nutrition_json,
                str(recipe_data.image_url) if recipe_data.image_url else None,
                recipe_data.prep_time_minutes,
                recipe_data.cook_time_minutes,
                total_time,
                recipe_data.servings,
                recipe_data.difficulty.value if recipe_data.difficulty else None,
                recipe_data.cuisine,
                user_id,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            recipe_id = cursor.lastrowid
            
            #insert tags
            if recipe_data.tags:
                for tag in recipe_data.tags:
                    cursor.execute("""
                        INSERT INTO recipe_tags (recipe_id, tag_name)
                        VALUES (?, ?)
                    """, (recipe_id, tag.lower()))
            
            self.conn.commit()
            
            logger.info(f"created recipe {recipe_id}: {recipe_data.title}")
            
            #fetch and return created recipe
            return await self.get_recipe(recipe_id, user_id)
            
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            logger.error(f"integrity error creating recipe: {e}")
            raise ValueError("recipe with this data already exists")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"error creating recipe: {e}")
            raise
    
    async def get_recipe(
        self,
        recipe_id: int,
        user_id: Optional[int] = None
    ) -> Optional[RecipeResponse]:
        """
        get recipe by id
        
        args:
            recipe_id: recipe id
            user_id: requesting user id (for favorites/ratings)
            
        returns:
            recipe data or none if not found
        """
        try:
            cursor = self.conn.cursor()
            
            #get recipe
            cursor.execute("""
                SELECT * FROM recipes
                WHERE id = ? AND is_deleted = 0
            """, (recipe_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            #increment view count
            cursor.execute("""
                UPDATE recipes SET view_count = view_count + 1
                WHERE id = ?
            """, (recipe_id,))
            self.conn.commit()
            
            #get tags
            cursor.execute("""
                SELECT tag_name FROM recipe_tags
                WHERE recipe_id = ?
            """, (recipe_id,))
            tags = [row[0] for row in cursor.fetchall()]
            
            #get average rating
            cursor.execute("""
                SELECT AVG(rating) as avg_rating, COUNT(*) as count
                FROM recipe_ratings
                WHERE recipe_id = ?
            """, (recipe_id,))
            rating_row = cursor.fetchone()
            avg_rating = rating_row['avg_rating']
            rating_count = rating_row['count']
            
            #check if favorite
            is_favorite = False
            user_rating = None
            if user_id:
                cursor.execute("""
                    SELECT 1 FROM user_favorites
                    WHERE user_id = ? AND recipe_id = ?
                """, (user_id, recipe_id))
                is_favorite = cursor.fetchone() is not None
                
                cursor.execute("""
                    SELECT rating FROM recipe_ratings
                    WHERE user_id = ? AND recipe_id = ?
                """, (user_id, recipe_id))
                user_rating_row = cursor.fetchone()
                if user_rating_row:
                    user_rating = user_rating_row['rating']
            
            #parse json fields
            ingredients = [
                RecipeIngredient(**ing)
                for ing in json.loads(row['ingredients_json'])
            ]
            instructions = json.loads(row['instructions_json'])
            nutrition = None
            if row['nutrition_json']:
                nutrition = RecipeNutrition(**json.loads(row['nutrition_json']))
            
            #construct response
            recipe = RecipeResponse(
                id=row['id'],
                title=row['title'],
                description=row['description'],
                source_url=row['source_url'],
                source_name=row['source_name'],
                ingredients=ingredients,
                instructions=instructions,
                nutrition=nutrition,
                image_url=row['image_url'],
                prep_time_minutes=row['prep_time_minutes'],
                cook_time_minutes=row['cook_time_minutes'],
                total_time_minutes=row['total_time_minutes'],
                servings=row['servings'],
                difficulty=row['difficulty'],
                cuisine=row['cuisine'],
                tags=tags,
                created_by=row['created_by'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']),
                view_count=row['view_count'],
                is_favorite=is_favorite,
                average_rating=round(avg_rating, 2) if avg_rating else None,
                rating_count=rating_count,
                user_rating=user_rating
            )
            
            return recipe
            
        except Exception as e:
            logger.error(f"error getting recipe {recipe_id}: {e}")
            raise
    
    async def update_recipe(
        self,
        recipe_id: int,
        recipe_data: RecipeUpdate,
        user_id: int
    ) -> Optional[RecipeResponse]:
        """
        update existing recipe
        
        args:
            recipe_id: recipe to update
            recipe_data: updated recipe data
            user_id: user performing update (must be creator)
            
        returns:
            updated recipe or none if not found/unauthorized
        """
        try:
            cursor = self.conn.cursor()
            
            #check if recipe exists and user owns it
            cursor.execute("""
                SELECT created_by FROM recipes
                WHERE id = ? AND is_deleted = 0
            """, (recipe_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            if row['created_by'] != user_id:
                raise PermissionError("user does not own this recipe")
            
            #build update query dynamically based on provided fields
            updates = []
            params = []
            
            if recipe_data.title is not None:
                updates.append("title = ?")
                params.append(recipe_data.title)
            
            if recipe_data.description is not None:
                updates.append("description = ?")
                params.append(recipe_data.description)
            
            if recipe_data.source_url is not None:
                updates.append("source_url = ?")
                params.append(str(recipe_data.source_url))
            
            if recipe_data.source_name is not None:
                updates.append("source_name = ?")
                params.append(recipe_data.source_name)
            
            if recipe_data.ingredients is not None:
                updates.append("ingredients_json = ?")
                params.append(json.dumps([ing.model_dump() for ing in recipe_data.ingredients]))
            
            if recipe_data.instructions is not None:
                updates.append("instructions_json = ?")
                params.append(json.dumps(recipe_data.instructions))
            
            if recipe_data.nutrition is not None:
                updates.append("nutrition_json = ?")
                params.append(json.dumps(recipe_data.nutrition.model_dump()))
            
            if recipe_data.image_url is not None:
                updates.append("image_url = ?")
                params.append(str(recipe_data.image_url))
            
            if recipe_data.prep_time_minutes is not None:
                updates.append("prep_time_minutes = ?")
                params.append(recipe_data.prep_time_minutes)
            
            if recipe_data.cook_time_minutes is not None:
                updates.append("cook_time_minutes = ?")
                params.append(recipe_data.cook_time_minutes)
            
            #recalculate total time if either prep or cook time changed
            if recipe_data.prep_time_minutes is not None or recipe_data.cook_time_minutes is not None:
                #get current values
                cursor.execute("""
                    SELECT prep_time_minutes, cook_time_minutes FROM recipes WHERE id = ?
                """, (recipe_id,))
                current = cursor.fetchone()
                
                prep_time = recipe_data.prep_time_minutes if recipe_data.prep_time_minutes is not None else current['prep_time_minutes']
                cook_time = recipe_data.cook_time_minutes if recipe_data.cook_time_minutes is not None else current['cook_time_minutes']
                
                total_time = None
                if prep_time and cook_time:
                    total_time = prep_time + cook_time
                elif prep_time:
                    total_time = prep_time
                elif cook_time:
                    total_time = cook_time
                
                updates.append("total_time_minutes = ?")
                params.append(total_time)
            
            if recipe_data.servings is not None:
                updates.append("servings = ?")
                params.append(recipe_data.servings)
            
            if recipe_data.difficulty is not None:
                updates.append("difficulty = ?")
                params.append(recipe_data.difficulty.value)
            
            if recipe_data.cuisine is not None:
                updates.append("cuisine = ?")
                params.append(recipe_data.cuisine)
            
            #always update timestamp
            updates.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            
            if updates:
                params.append(recipe_id)
                query = f"UPDATE recipes SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, params)
            
            #update tags if provided
            if recipe_data.tags is not None:
                #delete existing tags
                cursor.execute("DELETE FROM recipe_tags WHERE recipe_id = ?", (recipe_id,))
                
                #insert new tags
                for tag in recipe_data.tags:
                    cursor.execute("""
                        INSERT INTO recipe_tags (recipe_id, tag_name)
                        VALUES (?, ?)
                    """, (recipe_id, tag.lower()))
            
            self.conn.commit()
            
            logger.info(f"updated recipe {recipe_id}")
            
            #return updated recipe
            return await self.get_recipe(recipe_id, user_id)
            
        except PermissionError:
            raise
        except Exception as e:
            self.conn.rollback()
            logger.error(f"error updating recipe {recipe_id}: {e}")
            raise
    
    async def delete_recipe(self, recipe_id: int, user_id: int) -> bool:
        """
        soft delete recipe (mark as deleted)
        
        args:
            recipe_id: recipe to delete
            user_id: user performing deletion (must be creator)
            
        returns:
            true if deleted, false if not found/unauthorized
        """
        try:
            cursor = self.conn.cursor()
            
            #check if recipe exists and user owns it
            cursor.execute("""
                SELECT created_by FROM recipes
                WHERE id = ? AND is_deleted = 0
            """, (recipe_id,))
            row = cursor.fetchone()
            
            if not row:
                return False
            
            if row['created_by'] != user_id:
                raise PermissionError("user does not own this recipe")
            
            #soft delete
            cursor.execute("""
                UPDATE recipes
                SET is_deleted = 1, updated_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), recipe_id))
            
            self.conn.commit()
            
            logger.info(f"deleted recipe {recipe_id}")
            return True
            
        except PermissionError:
            raise
        except Exception as e:
            self.conn.rollback()
            logger.error(f"error deleting recipe {recipe_id}: {e}")
            raise
    
    async def search_recipes(
        self,
        search_params: RecipeSearch,
        user_id: Optional[int] = None
    ) -> Tuple[List[RecipeSummary], int]:
        """
        search recipes with filters
        
        args:
            search_params: search parameters
            user_id: requesting user id (for favorites)
            
        returns:
            tuple of (list of recipes, total count)
        """
        try:
            cursor = self.conn.cursor()
            
            #build where clauses
            where_clauses = ["is_deleted = 0"]
            params = []
            
            #full-text search
            if search_params.query:
                where_clauses.append("""
                    id IN (
                        SELECT rowid FROM recipes_fts
                        WHERE recipes_fts MATCH ?
                    )
                """)
                params.append(search_params.query)
            
            #cuisine filter
            if search_params.cuisine:
                where_clauses.append("LOWER(cuisine) = LOWER(?)")
                params.append(search_params.cuisine)
            
            #difficulty filter
            if search_params.difficulty:
                where_clauses.append("difficulty = ?")
                params.append(search_params.difficulty.value)
            
            #time filter
            if search_params.max_time:
                where_clauses.append("(total_time_minutes IS NULL OR total_time_minutes <= ?)")
                params.append(search_params.max_time)
            
            #rating filter
            if search_params.min_rating:
                where_clauses.append("""
                    id IN (
                        SELECT recipe_id FROM recipe_ratings
                        GROUP BY recipe_id
                        HAVING AVG(rating) >= ?
                    )
                """)
                params.append(search_params.min_rating)
            
            #tags filter
            if search_params.tags:
                tag_placeholders = ','.join(['?' for _ in search_params.tags])
                where_clauses.append(f"""
                    id IN (
                        SELECT recipe_id FROM recipe_tags
                        WHERE LOWER(tag_name) IN ({tag_placeholders})
                        GROUP BY recipe_id
                        HAVING COUNT(DISTINCT tag_name) = ?
                    )
                """)
                params.extend(search_params.tags)
                params.append(len(search_params.tags))
            
            #ingredients filter (recipe must contain all specified ingredients)
            if search_params.ingredients:
                ingredient_conditions = []
                for ing in search_params.ingredients:
                    ingredient_conditions.append("LOWER(ingredients_json) LIKE ?")
                    params.append(f"%{ing.lower()}%")
                where_clauses.append(f"({' AND '.join(ingredient_conditions)})")
            
            #exclude ingredients filter
            if search_params.exclude_ingredients:
                for ing in search_params.exclude_ingredients:
                    where_clauses.append("LOWER(ingredients_json) NOT LIKE ?")
                    params.append(f"%{ing.lower()}%")
            
            where_sql = " AND ".join(where_clauses)
            
            #get total count
            count_query = f"SELECT COUNT(*) as count FROM recipes WHERE {where_sql}"
            cursor.execute(count_query, params)
            total_count = cursor.fetchone()['count']
            
            #build sort
            sort_column = {
                "created_at": "created_at DESC",
                "rating": "(SELECT AVG(rating) FROM recipe_ratings WHERE recipe_id = recipes.id) DESC",
                "time": "total_time_minutes ASC",
                "title": "title ASC"
            }.get(search_params.sort_by, "created_at DESC")
            
            #get recipes
            query = f"""
                SELECT r.*,
                    (SELECT AVG(rating) FROM recipe_ratings WHERE recipe_id = r.id) as avg_rating,
                    (SELECT COUNT(*) FROM recipe_ratings WHERE recipe_id = r.id) as rating_count
                FROM recipes r
                WHERE {where_sql}
                ORDER BY {sort_column}
                LIMIT ? OFFSET ?
            """
            
            params.extend([search_params.limit, search_params.offset])
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            #build recipe summaries
            recipes = []
            for row in rows:
                #check if favorite
                is_favorite = False
                if user_id:
                    cursor.execute("""
                        SELECT 1 FROM user_favorites
                        WHERE user_id = ? AND recipe_id = ?
                    """, (user_id, row['id']))
                    is_favorite = cursor.fetchone() is not None
                
                recipe = RecipeSummary(
                    id=row['id'],
                    title=row['title'],
                    description=row['description'],
                    image_url=row['image_url'],
                    total_time_minutes=row['total_time_minutes'],
                    difficulty=row['difficulty'],
                    cuisine=row['cuisine'],
                    servings=row['servings'],
                    average_rating=round(row['avg_rating'], 2) if row['avg_rating'] else None,
                    rating_count=row['rating_count'],
                    is_favorite=is_favorite
                )
                recipes.append(recipe)
            
            return recipes, total_count
            
        except Exception as e:
            logger.error(f"error searching recipes: {e}")
            raise
    
    async def add_to_favorites(self, recipe_id: int, user_id: int) -> bool:
        """add recipe to user favorites"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO user_favorites (user_id, recipe_id)
                VALUES (?, ?)
            """, (user_id, recipe_id))
            self.conn.commit()
            logger.info(f"user {user_id} favorited recipe {recipe_id}")
            return True
        except sqlite3.IntegrityError:
            return False  #already favorited
        except Exception as e:
            self.conn.rollback()
            logger.error(f"error adding favorite: {e}")
            raise
    
    async def remove_from_favorites(self, recipe_id: int, user_id: int) -> bool:
        """remove recipe from user favorites"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                DELETE FROM user_favorites
                WHERE user_id = ? AND recipe_id = ?
            """, (user_id, recipe_id))
            self.conn.commit()
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"user {user_id} unfavorited recipe {recipe_id}")
            return deleted
        except Exception as e:
            self.conn.rollback()
            logger.error(f"error removing favorite: {e}")
            raise
    
    async def get_user_favorites(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[RecipeSummary], int]:
        """get user's favorite recipes"""
        try:
            cursor = self.conn.cursor()
            
            #get total count
            cursor.execute("""
                SELECT COUNT(*) as count FROM user_favorites
                WHERE user_id = ?
            """, (user_id,))
            total_count = cursor.fetchone()['count']
            
            #get favorites
            cursor.execute("""
                SELECT r.*,
                    (SELECT AVG(rating) FROM recipe_ratings WHERE recipe_id = r.id) as avg_rating,
                    (SELECT COUNT(*) FROM recipe_ratings WHERE recipe_id = r.id) as rating_count
                FROM recipes r
                INNER JOIN user_favorites uf ON r.id = uf.recipe_id
                WHERE uf.user_id = ? AND r.is_deleted = 0
                ORDER BY uf.added_at DESC
                LIMIT ? OFFSET ?
            """, (user_id, limit, offset))
            rows = cursor.fetchall()
            
            recipes = []
            for row in rows:
                recipe = RecipeSummary(
                    id=row['id'],
                    title=row['title'],
                    description=row['description'],
                    image_url=row['image_url'],
                    total_time_minutes=row['total_time_minutes'],
                    difficulty=row['difficulty'],
                    cuisine=row['cuisine'],
                    servings=row['servings'],
                    average_rating=round(row['avg_rating'], 2) if row['avg_rating'] else None,
                    rating_count=row['rating_count'],
                    is_favorite=True
                )
                recipes.append(recipe)
            
            return recipes, total_count
            
        except Exception as e:
            logger.error(f"error getting favorites for user {user_id}: {e}")
            raise

