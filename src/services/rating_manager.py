"""
rating and review manager service
handles recipe ratings and reviews
"""

import sqlite3
import logging
from typing import Optional, List, Tuple
from datetime import datetime
from src.models.rating import (
    RatingCreate, RatingUpdate, RatingResponse, RatingSummary
)

logger = logging.getLogger(__name__)


class RatingManager:
    """manages recipe ratings and reviews"""
    
    def __init__(self, db_connection: sqlite3.Connection):
        self.conn = db_connection
        self.conn.row_factory = sqlite3.Row
    
    async def create_or_update_rating(
        self,
        recipe_id: int,
        user_id: int,
        rating_data: RatingCreate
    ) -> RatingResponse:
        """
        create or update recipe rating
        user can only have one rating per recipe
        
        args:
            recipe_id: recipe to rate
            user_id: user creating rating
            rating_data: rating data
            
        returns:
            created/updated rating
        """
        try:
            cursor = self.conn.cursor()
            
            #check if recipe exists
            cursor.execute("""
                SELECT id FROM recipes WHERE id = ? AND is_deleted = 0
            """, (recipe_id,))
            if not cursor.fetchone():
                raise ValueError("recipe not found")
            
            #check if rating already exists
            cursor.execute("""
                SELECT id FROM recipe_ratings
                WHERE recipe_id = ? AND user_id = ?
            """, (recipe_id, user_id))
            existing = cursor.fetchone()
            
            if existing:
                #update existing rating
                cursor.execute("""
                    UPDATE recipe_ratings
                    SET rating = ?, review_text = ?, updated_at = ?
                    WHERE id = ?
                """, (
                    rating_data.rating,
                    rating_data.review_text,
                    datetime.now().isoformat(),
                    existing['id']
                ))
                rating_id = existing['id']
                logger.info(f"updated rating {rating_id} for recipe {recipe_id}")
            else:
                #create new rating
                cursor.execute("""
                    INSERT INTO recipe_ratings (
                        recipe_id, user_id, rating, review_text,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    recipe_id,
                    user_id,
                    rating_data.rating,
                    rating_data.review_text,
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                rating_id = cursor.lastrowid
                logger.info(f"created rating {rating_id} for recipe {recipe_id}")
            
            self.conn.commit()
            
            #fetch and return rating
            return await self.get_rating(rating_id)
            
        except ValueError:
            raise
        except Exception as e:
            self.conn.rollback()
            logger.error(f"error creating/updating rating: {e}")
            raise
    
    async def get_rating(self, rating_id: int) -> Optional[RatingResponse]:
        """get rating by id"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT rr.*, u.email, u.full_name
                FROM recipe_ratings rr
                LEFT JOIN users u ON rr.user_id = u.id
                WHERE rr.id = ?
            """, (rating_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return RatingResponse(
                id=row['id'],
                recipe_id=row['recipe_id'],
                user_id=row['user_id'],
                user_name=row['full_name'] or row['email'],
                rating=row['rating'],
                review_text=row['review_text'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at'])
            )
            
        except Exception as e:
            logger.error(f"error getting rating {rating_id}: {e}")
            raise
    
    async def get_user_rating_for_recipe(
        self,
        recipe_id: int,
        user_id: int
    ) -> Optional[RatingResponse]:
        """get user's rating for specific recipe"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT rr.*, u.email, u.full_name
                FROM recipe_ratings rr
                LEFT JOIN users u ON rr.user_id = u.id
                WHERE rr.recipe_id = ? AND rr.user_id = ?
            """, (recipe_id, user_id))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return RatingResponse(
                id=row['id'],
                recipe_id=row['recipe_id'],
                user_id=row['user_id'],
                user_name=row['full_name'] or row['email'],
                rating=row['rating'],
                review_text=row['review_text'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at'])
            )
            
        except Exception as e:
            logger.error(f"error getting user rating: {e}")
            raise
    
    async def get_recipe_ratings(
        self,
        recipe_id: int,
        limit: int = 20,
        offset: int = 0,
        min_rating: Optional[int] = None
    ) -> Tuple[List[RatingResponse], int]:
        """
        get all ratings for recipe
        
        args:
            recipe_id: recipe id
            limit: max results
            offset: pagination offset
            min_rating: filter by minimum rating
            
        returns:
            tuple of (ratings list, total count)
        """
        try:
            cursor = self.conn.cursor()
            
            #build where clause
            where_clause = "rr.recipe_id = ?"
            params = [recipe_id]
            
            if min_rating:
                where_clause += " AND rr.rating >= ?"
                params.append(min_rating)
            
            #get total count
            cursor.execute(f"""
                SELECT COUNT(*) as count
                FROM recipe_ratings rr
                WHERE {where_clause}
            """, params)
            total_count = cursor.fetchone()['count']
            
            #get ratings
            params.extend([limit, offset])
            cursor.execute(f"""
                SELECT rr.*, u.email, u.full_name
                FROM recipe_ratings rr
                LEFT JOIN users u ON rr.user_id = u.id
                WHERE {where_clause}
                ORDER BY rr.created_at DESC
                LIMIT ? OFFSET ?
            """, params)
            rows = cursor.fetchall()
            
            ratings = []
            for row in rows:
                rating = RatingResponse(
                    id=row['id'],
                    recipe_id=row['recipe_id'],
                    user_id=row['user_id'],
                    user_name=row['full_name'] or row['email'],
                    rating=row['rating'],
                    review_text=row['review_text'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
                ratings.append(rating)
            
            return ratings, total_count
            
        except Exception as e:
            logger.error(f"error getting ratings for recipe {recipe_id}: {e}")
            raise
    
    async def delete_rating(self, rating_id: int, user_id: int) -> bool:
        """
        delete rating (user can only delete their own)
        
        args:
            rating_id: rating to delete
            user_id: user performing deletion
            
        returns:
            true if deleted, false if not found/unauthorized
        """
        try:
            cursor = self.conn.cursor()
            
            #check if rating exists and user owns it
            cursor.execute("""
                SELECT user_id FROM recipe_ratings WHERE id = ?
            """, (rating_id,))
            row = cursor.fetchone()
            
            if not row:
                return False
            
            if row['user_id'] != user_id:
                raise PermissionError("user does not own this rating")
            
            #delete rating
            cursor.execute("DELETE FROM recipe_ratings WHERE id = ?", (rating_id,))
            self.conn.commit()
            
            logger.info(f"deleted rating {rating_id}")
            return True
            
        except PermissionError:
            raise
        except Exception as e:
            self.conn.rollback()
            logger.error(f"error deleting rating {rating_id}: {e}")
            raise
    
    async def get_recipe_rating_summary(self, recipe_id: int) -> RatingSummary:
        """get rating summary for recipe"""
        try:
            cursor = self.conn.cursor()
            
            #get rating distribution
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_count,
                    AVG(rating) as average_rating,
                    SUM(CASE WHEN rating = 5 THEN 1 ELSE 0 END) as five_star_count,
                    SUM(CASE WHEN rating = 4 THEN 1 ELSE 0 END) as four_star_count,
                    SUM(CASE WHEN rating = 3 THEN 1 ELSE 0 END) as three_star_count,
                    SUM(CASE WHEN rating = 2 THEN 1 ELSE 0 END) as two_star_count,
                    SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END) as one_star_count
                FROM recipe_ratings
                WHERE recipe_id = ?
            """, (recipe_id,))
            row = cursor.fetchone()
            
            return RatingSummary(
                recipe_id=recipe_id,
                total_count=row['total_count'],
                average_rating=round(row['average_rating'], 2) if row['average_rating'] else 0.0,
                five_star_count=row['five_star_count'],
                four_star_count=row['four_star_count'],
                three_star_count=row['three_star_count'],
                two_star_count=row['two_star_count'],
                one_star_count=row['one_star_count']
            )
            
        except Exception as e:
            logger.error(f"error getting rating summary for recipe {recipe_id}: {e}")
            raise

