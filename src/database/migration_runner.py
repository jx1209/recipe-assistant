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
        cursor.execute("SELECT migration_name FROM schema_migrations ORDER BY migration_name")
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

