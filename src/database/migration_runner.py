"""
Database migration runner
Applies SQL migrations to the database
"""

import sqlite3
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


class MigrationRunner:
    """Runs database migrations"""
    
    def __init__(self, db_connection: sqlite3.Connection):
        self.conn = db_connection
        self.migrations_dir = Path(__file__).parent / "migrations"
        self._ensure_migrations_table()
    
    def _ensure_migrations_table(self):
        """Create migrations tracking table if it doesn't exist"""
        cursor = self.conn.cursor()
        
        # Check if table exists and what columns it has
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'")
        table_exists = cursor.fetchone() is not None
        
        if table_exists:
            # Check if it has the old 'version' column or new 'migration_name' column
            cursor.execute("PRAGMA table_info(schema_migrations)")
            columns = {row[1] for row in cursor.fetchall()}
            
            if 'version' in columns and 'migration_name' not in columns:
                # Old schema - add migration_name column or use version
                # We'll just use version as migration_name
                pass
            elif 'migration_name' not in columns:
                # Create new structure
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        migration_name TEXT UNIQUE NOT NULL,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                self.conn.commit()
        else:
            # Create fresh table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    migration_name TEXT UNIQUE NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.commit()
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of already applied migrations"""
        cursor = self.conn.cursor()
        
        # Check which column exists
        cursor.execute("PRAGMA table_info(schema_migrations)")
        columns = {row[1] for row in cursor.fetchall()}
        
        if 'migration_name' in columns:
            cursor.execute("SELECT migration_name FROM schema_migrations ORDER BY migration_name")
        elif 'version' in columns:
            # Fallback to old schema
            cursor.execute("SELECT version FROM schema_migrations ORDER BY version")
        else:
            return []
        
        return [row[0] for row in cursor.fetchall()]
    
    def get_pending_migrations(self) -> List[Path]:
        """Get list of migration files that haven't been applied"""
        if not self.migrations_dir.exists():
            self.migrations_dir.mkdir(parents=True, exist_ok=True)
            return []
        
        applied = set(self.get_applied_migrations())
        
        # Get all .sql files in migrations directory
        all_migrations = sorted(self.migrations_dir.glob("*.sql"))
        
        # Filter out already applied migrations
        pending = [m for m in all_migrations if m.name not in applied]
        
        return pending
    
    def apply_migration(self, migration_file: Path) -> bool:
        """
        Apply a single migration
        
        Args:
            migration_file: Path to migration SQL file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Applying migration: {migration_file.name}")
            
            # Read migration SQL
            with open(migration_file, 'r', encoding='utf-8') as f:
                migration_sql = f.read()
            
            # Execute migration
            self.conn.executescript(migration_sql)
            
            # Record migration as applied
            self.conn.execute(
                "INSERT INTO schema_migrations (migration_name) VALUES (?)",
                (migration_file.name,)
            )
            
            self.conn.commit()
            
            logger.info(f"Successfully applied migration: {migration_file.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error applying migration {migration_file.name}: {e}")
            self.conn.rollback()
            return False
    
    def run_pending_migrations(self) -> int:
        """
        Run all pending migrations
        
        Returns:
            Number of migrations applied
        """
        pending = self.get_pending_migrations()
        
        if not pending:
            logger.info("No pending migrations")
            return 0
        
        logger.info(f"Found {len(pending)} pending migration(s)")
        
        applied_count = 0
        for migration_file in pending:
            if self.apply_migration(migration_file):
                applied_count += 1
            else:
                logger.error(f"Migration failed: {migration_file.name}. Stopping migration process.")
                break
        
        logger.info(f"Applied {applied_count} migration(s)")
        return applied_count

