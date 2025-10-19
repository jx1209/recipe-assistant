"""
Database Manager for Recipe Assistant
Handles SQLite database connections, operations, and management
"""

import sqlite3
import json
import logging
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime, timedelta
import shutil

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Comprehensive database manager for Recipe Assistant
    Handles connections, CRUD operations, transactions, and maintenance
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, db_path: str = "data/recipe_assistant.db"):
        """Singleton pattern to ensure only one database manager exists"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, db_path: str = "data/recipe_assistant.db"):
        """Initialize database manager"""
        if hasattr(self, '_initialized'):
            return
            
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Thread-local storage for connections
        self._local = threading.local()
        
        # Initialize database
        self._initialize_database()
        
        self._initialized = True
        logger.info(f"Database Manager initialized: {self.db_path}")
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection"""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,
                timeout=30.0
            )
            self._local.connection.row_factory = sqlite3.Row
            # Enable foreign keys
            self._local.connection.execute("PRAGMA foreign_keys = ON")
            # Enable WAL mode for better concurrency
            self._local.connection.execute("PRAGMA journal_mode = WAL")
        
        return self._local.connection
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database cursor"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            cursor.close()
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions"""
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Transaction error: {e}")
            raise
    
    def _initialize_database(self):
        """Initialize database with schema"""
        schema_file = Path(__file__).parent / "schema.sql"
        
        if not schema_file.exists():
            logger.error(f"Schema file not found: {schema_file}")
            raise FileNotFoundError(f"Schema file not found: {schema_file}")
        
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        with self.get_cursor() as cursor:
            cursor.executescript(schema_sql)
        
        logger.info("Database schema initialized successfully")
    
    # ========== USER OPERATIONS ==========
    
    def create_user(self, email: str, password_hash: str, full_name: Optional[str] = None) -> int:
        """Create a new user"""
        with self.get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (email, password_hash, full_name) VALUES (?, ?, ?)",
                (email, password_hash, full_name)
            )
            return cursor.lastrowid
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        with self.get_cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = ? AND is_active = 1", (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        with self.get_cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = ? AND is_active = 1", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user fields"""
        if not kwargs:
            return False
        
        allowed_fields = ['email', 'full_name', 'preferences_json', 'is_verified']
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not update_fields:
            return False
        
        set_clause = ', '.join([f"{field} = ?" for field in update_fields.keys()])
        values = list(update_fields.values()) + [user_id]
        
        with self.get_cursor() as cursor:
            cursor.execute(
                f"UPDATE users SET {set_clause} WHERE id = ?",
                values
            )
            return cursor.rowcount > 0
    
    def update_user_preferences(self, user_id: int, preferences: Dict) -> bool:
        """Update user preferences"""
        return self.update_user(user_id, preferences_json=json.dumps(preferences))
    
    # ========== RECIPE OPERATIONS ==========
    
    def create_recipe(self, recipe_data: Dict) -> int:
        """Create a new recipe"""
        required_fields = ['title', 'ingredients_json', 'instructions_json']
        for field in required_fields:
            if field not in recipe_data:
                raise ValueError(f"Missing required field: {field}")
        
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO recipes (
                    title, description, source_url, source_name,
                    ingredients_json, instructions_json, nutrition_json,
                    image_url, prep_time_minutes, cook_time_minutes,
                    total_time_minutes, servings, difficulty, cuisine, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                recipe_data.get('title'),
                recipe_data.get('description'),
                recipe_data.get('source_url'),
                recipe_data.get('source_name'),
                recipe_data.get('ingredients_json'),
                recipe_data.get('instructions_json'),
                recipe_data.get('nutrition_json'),
                recipe_data.get('image_url'),
                recipe_data.get('prep_time_minutes'),
                recipe_data.get('cook_time_minutes'),
                recipe_data.get('total_time_minutes'),
                recipe_data.get('servings', 1),
                recipe_data.get('difficulty'),
                recipe_data.get('cuisine'),
                recipe_data.get('created_by')
            ))
            return cursor.lastrowid
    
    def get_recipe(self, recipe_id: int, increment_view: bool = False) -> Optional[Dict]:
        """Get recipe by ID"""
        with self.get_cursor() as cursor:
            if increment_view:
                cursor.execute(
                    "UPDATE recipes SET view_count = view_count + 1 WHERE id = ?",
                    (recipe_id,)
                )
            
            cursor.execute(
                "SELECT * FROM recipes WHERE id = ? AND is_deleted = 0",
                (recipe_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_recipe(self, recipe_id: int, recipe_data: Dict) -> bool:
        """Update recipe"""
        allowed_fields = [
            'title', 'description', 'source_url', 'source_name',
            'ingredients_json', 'instructions_json', 'nutrition_json',
            'image_url', 'prep_time_minutes', 'cook_time_minutes',
            'total_time_minutes', 'servings', 'difficulty', 'cuisine'
        ]
        
        update_fields = {k: v for k, v in recipe_data.items() if k in allowed_fields}
        
        if not update_fields:
            return False
        
        set_clause = ', '.join([f"{field} = ?" for field in update_fields.keys()])
        values = list(update_fields.values()) + [recipe_id]
        
        with self.get_cursor() as cursor:
            cursor.execute(
                f"UPDATE recipes SET {set_clause} WHERE id = ? AND is_deleted = 0",
                values
            )
            return cursor.rowcount > 0
    
    def delete_recipe(self, recipe_id: int, soft: bool = True) -> bool:
        """Delete recipe (soft delete by default)"""
        with self.get_cursor() as cursor:
            if soft:
                cursor.execute(
                    "UPDATE recipes SET is_deleted = 1 WHERE id = ?",
                    (recipe_id,)
                )
            else:
                cursor.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
            return cursor.rowcount > 0
    
    def search_recipes(self, 
                      query: Optional[str] = None,
                      cuisine: Optional[str] = None,
                      difficulty: Optional[str] = None,
                      max_time: Optional[int] = None,
                      tags: Optional[List[str]] = None,
                      limit: int = 20,
                      offset: int = 0) -> List[Dict]:
        """Search recipes with filters"""
        conditions = ["is_deleted = 0"]
        params = []
        
        if query:
            conditions.append("id IN (SELECT rowid FROM recipes_fts WHERE recipes_fts MATCH ?)")
            params.append(query)
        
        if cuisine:
            conditions.append("cuisine = ?")
            params.append(cuisine)
        
        if difficulty:
            conditions.append("difficulty = ?")
            params.append(difficulty)
        
        if max_time:
            conditions.append("total_time_minutes <= ?")
            params.append(max_time)
        
        if tags:
            tag_placeholders = ','.join(['?'] * len(tags))
            conditions.append(f"""
                id IN (
                    SELECT recipe_id FROM recipe_tags 
                    WHERE tag_name IN ({tag_placeholders})
                    GROUP BY recipe_id
                    HAVING COUNT(DISTINCT tag_name) = ?
                )
            """)
            params.extend(tags)
            params.append(len(tags))
        
        where_clause = ' AND '.join(conditions)
        params.extend([limit, offset])
        
        with self.get_cursor() as cursor:
            cursor.execute(f"""
                SELECT * FROM recipes
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_recipes_by_user(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get recipes created by a user"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM recipes
                WHERE created_by = ? AND is_deleted = 0
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (user_id, limit, offset))
            return [dict(row) for row in cursor.fetchall()]
    
    # ========== RECIPE TAGS ==========
    
    def add_recipe_tag(self, recipe_id: int, tag_name: str) -> bool:
        """Add tag to recipe"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(
                    "INSERT OR IGNORE INTO recipe_tags (recipe_id, tag_name) VALUES (?, ?)",
                    (recipe_id, tag_name.lower())
                )
                return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            return False
    
    def get_recipe_tags(self, recipe_id: int) -> List[str]:
        """Get all tags for a recipe"""
        with self.get_cursor() as cursor:
            cursor.execute(
                "SELECT tag_name FROM recipe_tags WHERE recipe_id = ?",
                (recipe_id,)
            )
            return [row['tag_name'] for row in cursor.fetchall()]
    
    def remove_recipe_tag(self, recipe_id: int, tag_name: str) -> bool:
        """Remove tag from recipe"""
        with self.get_cursor() as cursor:
            cursor.execute(
                "DELETE FROM recipe_tags WHERE recipe_id = ? AND tag_name = ?",
                (recipe_id, tag_name.lower())
            )
            return cursor.rowcount > 0
    
    # ========== FAVORITES ==========
    
    def add_favorite(self, user_id: int, recipe_id: int) -> bool:
        """Add recipe to user favorites"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(
                    "INSERT INTO user_favorites (user_id, recipe_id) VALUES (?, ?)",
                    (user_id, recipe_id)
                )
                return True
        except sqlite3.IntegrityError:
            return False
    
    def remove_favorite(self, user_id: int, recipe_id: int) -> bool:
        """Remove recipe from favorites"""
        with self.get_cursor() as cursor:
            cursor.execute(
                "DELETE FROM user_favorites WHERE user_id = ? AND recipe_id = ?",
                (user_id, recipe_id)
            )
            return cursor.rowcount > 0
    
    def get_user_favorites(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get user's favorite recipes"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT r.* FROM recipes r
                JOIN user_favorites f ON r.id = f.recipe_id
                WHERE f.user_id = ? AND r.is_deleted = 0
                ORDER BY f.added_at DESC
                LIMIT ? OFFSET ?
            """, (user_id, limit, offset))
            return [dict(row) for row in cursor.fetchall()]
    
    def is_favorite(self, user_id: int, recipe_id: int) -> bool:
        """Check if recipe is in user's favorites"""
        with self.get_cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM user_favorites WHERE user_id = ? AND recipe_id = ?",
                (user_id, recipe_id)
            )
            return cursor.fetchone() is not None
    
    # ========== RATINGS ==========
    
    def add_or_update_rating(self, recipe_id: int, user_id: int, rating: int, review: Optional[str] = None) -> bool:
        """Add or update recipe rating"""
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO recipe_ratings (recipe_id, user_id, rating, review)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(recipe_id, user_id) DO UPDATE SET
                    rating = excluded.rating,
                    review = excluded.review,
                    updated_at = CURRENT_TIMESTAMP
            """, (recipe_id, user_id, rating, review))
            return True
    
    def get_recipe_ratings(self, recipe_id: int) -> Dict:
        """Get recipe rating statistics"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT
                    COUNT(*) as count,
                    AVG(rating) as average,
                    SUM(CASE WHEN rating = 5 THEN 1 ELSE 0 END) as five_star,
                    SUM(CASE WHEN rating = 4 THEN 1 ELSE 0 END) as four_star,
                    SUM(CASE WHEN rating = 3 THEN 1 ELSE 0 END) as three_star,
                    SUM(CASE WHEN rating = 2 THEN 1 ELSE 0 END) as two_star,
                    SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END) as one_star
                FROM recipe_ratings
                WHERE recipe_id = ?
            """, (recipe_id,))
            row = cursor.fetchone()
            return dict(row) if row else {}
    
    def get_recipe_reviews(self, recipe_id: int, limit: int = 20, offset: int = 0) -> List[Dict]:
        """Get recipe reviews with user info"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    rr.*, 
                    u.full_name as user_name,
                    u.email as user_email
                FROM recipe_ratings rr
                JOIN users u ON rr.user_id = u.id
                WHERE rr.recipe_id = ? AND rr.review IS NOT NULL
                ORDER BY rr.created_at DESC
                LIMIT ? OFFSET ?
            """, (recipe_id, limit, offset))
            return [dict(row) for row in cursor.fetchall()]
    
    # ========== PANTRY ==========
    
    def add_pantry_item(self, user_id: int, ingredient_name: str, 
                       quantity: Optional[float] = None,
                       unit: Optional[str] = None,
                       category: Optional[str] = None,
                       expiration_date: Optional[str] = None) -> int:
        """Add item to user's pantry"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO user_pantry (user_id, ingredient_name, quantity, unit, category, expiration_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, ingredient_name.lower(), quantity, unit, category, expiration_date))
            return cursor.lastrowid
    
    def get_user_pantry(self, user_id: int) -> List[Dict]:
        """Get all items in user's pantry"""
        with self.get_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM user_pantry WHERE user_id = ? ORDER BY ingredient_name",
                (user_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def update_pantry_item(self, item_id: int, **kwargs) -> bool:
        """Update pantry item"""
        allowed_fields = ['quantity', 'unit', 'category', 'expiration_date']
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not update_fields:
            return False
        
        set_clause = ', '.join([f"{field} = ?" for field in update_fields.keys()])
        values = list(update_fields.values()) + [item_id]
        
        with self.get_cursor() as cursor:
            cursor.execute(
                f"UPDATE user_pantry SET {set_clause} WHERE id = ?",
                values
            )
            return cursor.rowcount > 0
    
    def delete_pantry_item(self, item_id: int) -> bool:
        """Remove item from pantry"""
        with self.get_cursor() as cursor:
            cursor.execute("DELETE FROM user_pantry WHERE id = ?", (item_id,))
            return cursor.rowcount > 0
    
    # ========== MEAL PLANS ==========
    
    def create_meal_plan(self, user_id: int, name: str, start_date: str, 
                        end_date: str, meals_json: str, notes: Optional[str] = None) -> int:
        """Create a meal plan"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO meal_plans (user_id, name, start_date, end_date, meals_json, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, name, start_date, end_date, meals_json, notes))
            return cursor.lastrowid
    
    def get_meal_plan(self, meal_plan_id: int) -> Optional[Dict]:
        """Get meal plan by ID"""
        with self.get_cursor() as cursor:
            cursor.execute("SELECT * FROM meal_plans WHERE id = ?", (meal_plan_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_user_meal_plans(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Dict]:
        """Get user's meal plans"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM meal_plans
                WHERE user_id = ?
                ORDER BY start_date DESC
                LIMIT ? OFFSET ?
            """, (user_id, limit, offset))
            return [dict(row) for row in cursor.fetchall()]
    
    def update_meal_plan(self, meal_plan_id: int, **kwargs) -> bool:
        """Update meal plan"""
        allowed_fields = ['name', 'start_date', 'end_date', 'meals_json', 'notes']
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not update_fields:
            return False
        
        set_clause = ', '.join([f"{field} = ?" for field in update_fields.keys()])
        values = list(update_fields.values()) + [meal_plan_id]
        
        with self.get_cursor() as cursor:
            cursor.execute(
                f"UPDATE meal_plans SET {set_clause} WHERE id = ?",
                values
            )
            return cursor.rowcount > 0
    
    def delete_meal_plan(self, meal_plan_id: int) -> bool:
        """Delete meal plan"""
        with self.get_cursor() as cursor:
            cursor.execute("DELETE FROM meal_plans WHERE id = ?", (meal_plan_id,))
            return cursor.rowcount > 0
    
    # ========== SHOPPING LISTS ==========
    
    def create_shopping_list(self, user_id: int, name: str, items_json: str, 
                            meal_plan_id: Optional[int] = None) -> int:
        """Create a shopping list"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO shopping_lists (user_id, name, items_json, meal_plan_id)
                VALUES (?, ?, ?, ?)
            """, (user_id, name, items_json, meal_plan_id))
            return cursor.lastrowid
    
    def get_shopping_list(self, list_id: int) -> Optional[Dict]:
        """Get shopping list by ID"""
        with self.get_cursor() as cursor:
            cursor.execute("SELECT * FROM shopping_lists WHERE id = ?", (list_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_user_shopping_lists(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Dict]:
        """Get user's shopping lists"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM shopping_lists
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (user_id, limit, offset))
            return [dict(row) for row in cursor.fetchall()]
    
    def update_shopping_list(self, list_id: int, items_json: str) -> bool:
        """Update shopping list items"""
        with self.get_cursor() as cursor:
            cursor.execute(
                "UPDATE shopping_lists SET items_json = ? WHERE id = ?",
                (items_json, list_id)
            )
            return cursor.rowcount > 0
    
    def delete_shopping_list(self, list_id: int) -> bool:
        """Delete shopping list"""
        with self.get_cursor() as cursor:
            cursor.execute("DELETE FROM shopping_lists WHERE id = ?", (list_id,))
            return cursor.rowcount > 0
    
    # ========== TOKEN BLACKLIST ==========
    
    def blacklist_token(self, token_jti: str, user_id: int, expires_at: datetime) -> bool:
        """Add token to blacklist"""
        with self.get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO token_blacklist (token_jti, user_id, expires_at) VALUES (?, ?, ?)",
                (token_jti, user_id, expires_at.isoformat())
            )
            return True
    
    def is_token_blacklisted(self, token_jti: str) -> bool:
        """Check if token is blacklisted"""
        with self.get_cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM token_blacklist WHERE token_jti = ?",
                (token_jti,)
            )
            return cursor.fetchone() is not None
    
    def cleanup_expired_tokens(self) -> int:
        """Remove expired tokens from blacklist"""
        with self.get_cursor() as cursor:
            cursor.execute(
                "DELETE FROM token_blacklist WHERE expires_at < ?",
                (datetime.now().isoformat(),)
            )
            return cursor.rowcount
    
    # ========== USER API KEYS ==========
    
    def set_user_api_key(self, user_id: int, service_name: str, encrypted_key: str) -> bool:
        """Store encrypted API key for user"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO user_api_keys (user_id, service_name, encrypted_key)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, service_name) DO UPDATE SET
                    encrypted_key = excluded.encrypted_key,
                    updated_at = CURRENT_TIMESTAMP
            """, (user_id, service_name, encrypted_key))
            return True
    
    def get_user_api_key(self, user_id: int, service_name: str) -> Optional[str]:
        """Get encrypted API key for user"""
        with self.get_cursor() as cursor:
            cursor.execute(
                "SELECT encrypted_key FROM user_api_keys WHERE user_id = ? AND service_name = ? AND is_active = 1",
                (user_id, service_name)
            )
            row = cursor.fetchone()
            return row['encrypted_key'] if row else None
    
    # ========== UTILITY ==========
    
    def backup_database(self, backup_path: Optional[Path] = None) -> Path:
        """Create a backup of the database"""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.db_path.parent / f"backup_{timestamp}.db"
        
        shutil.copy2(self.db_path, backup_path)
        logger.info(f"Database backed up to: {backup_path}")
        return backup_path
    
    def vacuum(self):
        """Optimize database (VACUUM)"""
        with self._get_connection() as conn:
            conn.execute("VACUUM")
        logger.info("Database vacuumed successfully")
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        with self.get_cursor() as cursor:
            stats = {}
            
            # User count
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE is_active = 1")
            stats['users'] = cursor.fetchone()['count']
            
            # Recipe count
            cursor.execute("SELECT COUNT(*) as count FROM recipes WHERE is_deleted = 0")
            stats['recipes'] = cursor.fetchone()['count']
            
            # Meal plan count
            cursor.execute("SELECT COUNT(*) as count FROM meal_plans")
            stats['meal_plans'] = cursor.fetchone()['count']
            
            # Rating count
            cursor.execute("SELECT COUNT(*) as count FROM recipe_ratings")
            stats['ratings'] = cursor.fetchone()['count']
            
            # Database size
            stats['db_size_mb'] = self.db_path.stat().st_size / (1024 * 1024)
            
            return stats
    
    def close(self):
        """Close database connection"""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None


# Global database instance
_db_instance: Optional[DatabaseManager] = None


def get_db(db_path: str = "data/recipe_assistant.db") -> DatabaseManager:
    """Get or create database manager instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager(db_path)
    return _db_instance

