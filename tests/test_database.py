"""
database manager tests
tests for database operations, crud, transactions
"""

import pytest
from pathlib import Path

from src.database.db_manager import DatabaseManager


@pytest.mark.unit
@pytest.mark.database
class TestDatabaseInitialization:
    """test database initialization"""
    
    @pytest.mark.asyncio
    async def test_database_creation(self, test_db: DatabaseManager):
        """test database is created successfully"""
        assert test_db is not None
        assert Path(test_db.db_path).exists()
    
    @pytest.mark.asyncio
    async def test_database_tables_exist(self, test_db: DatabaseManager):
        """test that all required tables are created"""
        expected_tables = [
            'users', 'recipes', 'recipe_ingredients', 'recipe_instructions',
            'meal_plans', 'meal_plan_items', 'shopping_lists', 'shopping_list_items',
            'pantry_items', 'recipe_ratings', 'user_favorites'
        ]
        
        existing_tables = await test_db.get_tables()
        
        for table in expected_tables:
            assert table in existing_tables, f"table {table} not found in database"
    
    @pytest.mark.asyncio
    async def test_database_stats(self, test_db: DatabaseManager):
        """test getting database statistics"""
        stats = test_db.get_stats()
        
        assert stats is not None
        assert 'users' in stats
        assert 'recipes' in stats
        assert stats['users'] == 0  #fresh database


@pytest.mark.unit
@pytest.mark.database
class TestUserCRUD:
    """test user crud operations"""
    
    @pytest.mark.asyncio
    async def test_create_user(self, test_db: DatabaseManager):
        """test creating a new user"""
        user_id = await test_db.create_user(
            email="test@example.com",
            password_hash="hashed_password",
            full_name="Test User"
        )
        
        assert user_id is not None
        assert user_id > 0
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, test_db: DatabaseManager):
        """test retrieving user by id"""
        #create user
        user_id = await test_db.create_user(
            email="test@example.com",
            password_hash="hashed_password",
            full_name="Test User"
        )
        
        #retrieve user
        user = await test_db.get_user_by_id(user_id)
        
        assert user is not None
        assert user['id'] == user_id
        assert user['email'] == "test@example.com"
        assert user['full_name'] == "Test User"
    
    @pytest.mark.asyncio
    async def test_get_user_by_email(self, test_db: DatabaseManager):
        """test retrieving user by email"""
        #create user
        await test_db.create_user(
            email="test@example.com",
            password_hash="hashed_password",
            full_name="Test User"
        )
        
        #retrieve user
        user = await test_db.get_user_by_email("test@example.com")
        
        assert user is not None
        assert user['email'] == "test@example.com"
        assert user['full_name'] == "Test User"
    
    @pytest.mark.asyncio
    async def test_update_user(self, test_db: DatabaseManager):
        """test updating user information"""
        #create user
        user_id = await test_db.create_user(
            email="test@example.com",
            password_hash="hashed_password",
            full_name="Test User"
        )
        
        #update user
        await test_db.update_user(
            user_id=user_id,
            full_name="Updated User"
        )
        
        #verify update
        user = await test_db.get_user_by_id(user_id)
        assert user['full_name'] == "Updated User"
    
    @pytest.mark.asyncio
    async def test_delete_user(self, test_db: DatabaseManager):
        """test deleting a user"""
        #create user
        user_id = await test_db.create_user(
            email="test@example.com",
            password_hash="hashed_password",
            full_name="Test User"
        )
        
        #delete user
        await test_db.delete_user(user_id)
        
        #verify deletion
        user = await test_db.get_user_by_id(user_id)
        assert user is None
    
    @pytest.mark.asyncio
    async def test_duplicate_email_constraint(self, test_db: DatabaseManager):
        """test that duplicate emails are prevented"""
        #create first user
        await test_db.create_user(
            email="test@example.com",
            password_hash="hashed_password",
            full_name="Test User"
        )
        
        #try to create duplicate
        with pytest.raises(Exception):  #should raise integrity error
            await test_db.create_user(
                email="test@example.com",
                password_hash="hashed_password2",
                full_name="Another User"
            )


@pytest.mark.unit
@pytest.mark.database
class TestDatabaseTransactions:
    """test database transaction handling"""
    
    @pytest.mark.asyncio
    async def test_transaction_commit(self, test_db: DatabaseManager):
        """test committing a transaction"""
        async with test_db.transaction():
            user_id = await test_db.create_user(
                email="test@example.com",
                password_hash="hashed_password",
                full_name="Test User"
            )
        
        #verify user was saved
        user = await test_db.get_user_by_id(user_id)
        assert user is not None
    
    @pytest.mark.asyncio
    async def test_transaction_rollback(self, test_db: DatabaseManager):
        """test rolling back a transaction on error"""
        try:
            async with test_db.transaction():
                user_id = await test_db.create_user(
                    email="test@example.com",
                    password_hash="hashed_password",
                    full_name="Test User"
                )
                #force an error
                raise Exception("Simulated error")
        except Exception:
            pass
        
        #verify user was not saved
        user = await test_db.get_user_by_email("test@example.com")
        assert user is None


@pytest.mark.unit
@pytest.mark.database  
class TestDatabaseConnection:
    """test database connection handling"""
    
    def test_database_close(self, db_sync: DatabaseManager):
        """test closing database connection"""
        db_sync.close()
        #should not raise error
    
    @pytest.mark.asyncio
    async def test_multiple_operations(self, test_db: DatabaseManager):
        """test performing multiple database operations"""
        #create multiple users
        user1_id = await test_db.create_user(
            email="user1@example.com",
            password_hash="hash1",
            full_name="User 1"
        )
        
        user2_id = await test_db.create_user(
            email="user2@example.com",
            password_hash="hash2",
            full_name="User 2"
        )
        
        #verify both exist
        user1 = await test_db.get_user_by_id(user1_id)
        user2 = await test_db.get_user_by_id(user2_id)
        
        assert user1 is not None
        assert user2 is not None
        assert user1['email'] != user2['email']


