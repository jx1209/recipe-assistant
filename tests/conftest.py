"""
pytest configuration and fixtures
shared fixtures for all tests
"""

import pytest
import asyncio
import os
import sys
from pathlib import Path
from typing import Generator, AsyncGenerator
import tempfile
import shutil

#add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.db_manager import DatabaseManager
from src.auth.auth_handler import AuthHandler
from src.config.settings import Settings, get_settings


#test database configuration
TEST_DB_PATH = "tests/test_data/test_recipe_assistant.db"
TEST_ENV_PATH = "tests/.env.test"


@pytest.fixture(scope="session")
def event_loop():
    """create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """create test settings"""
    #set test environment variables
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["DEBUG"] = "true"
    os.environ["DATABASE_URL"] = TEST_DB_PATH
    os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only-not-production-use"
    os.environ["SESSION_SECRET_KEY"] = "test-session-key-for-testing-only-not-production"
    
    settings = get_settings()
    return settings


@pytest.fixture(scope="function")
async def test_db(test_settings) -> AsyncGenerator[DatabaseManager, None]:
    """create a fresh test database for each test"""
    #ensure test directory exists
    Path(TEST_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    
    #remove existing test database
    if Path(TEST_DB_PATH).exists():
        Path(TEST_DB_PATH).unlink()
    
    #create database manager
    db_manager = DatabaseManager(db_path=TEST_DB_PATH)
    
    #initialize database with schema
    await db_manager.initialize()
    
    yield db_manager
    
    #cleanup
    db_manager.close()
    
    #remove test database
    if Path(TEST_DB_PATH).exists():
        Path(TEST_DB_PATH).unlink()


@pytest.fixture(scope="function")
def db_sync(test_settings) -> Generator[DatabaseManager, None, None]:
    """create a synchronous test database for non-async tests"""
    #ensure test directory exists
    Path(TEST_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    
    #remove existing test database
    if Path(TEST_DB_PATH).exists():
        Path(TEST_DB_PATH).unlink()
    
    #create database manager
    db_manager = DatabaseManager(db_path=TEST_DB_PATH)
    
    #initialize database (synchronously)
    import asyncio
    asyncio.run(db_manager.initialize())
    
    yield db_manager
    
    #cleanup
    db_manager.close()
    
    #remove test database
    if Path(TEST_DB_PATH).exists():
        Path(TEST_DB_PATH).unlink()


@pytest.fixture(scope="function")
def auth_handler() -> AuthHandler:
    """create auth handler instance"""
    return AuthHandler()


@pytest.fixture(scope="function")
def sample_user_data() -> dict:
    """sample user registration data"""
    return {
        "email": "test@example.com",
        "password": "TestPass123!",
        "full_name": "Test User"
    }


@pytest.fixture(scope="function")
def sample_user_credentials() -> dict:
    """sample user login credentials"""
    return {
        "email": "test@example.com",
        "password": "TestPass123!"
    }


@pytest.fixture(scope="function")
async def registered_user(test_db: DatabaseManager, sample_user_data: dict, auth_handler: AuthHandler) -> dict:
    """create a registered user in the database"""
    #hash password
    hashed_password = auth_handler.get_password_hash(sample_user_data["password"])
    
    #insert user
    user_id = await test_db.create_user(
        email=sample_user_data["email"],
        password_hash=hashed_password,
        full_name=sample_user_data.get("full_name")
    )
    
    #get user from database
    user = await test_db.get_user_by_id(user_id)
    
    return {
        "id": user["id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "password": sample_user_data["password"]  #store plain password for login tests
    }


@pytest.fixture(scope="function")
def valid_access_token(auth_handler: AuthHandler, sample_user_data: dict) -> str:
    """create a valid access token"""
    return auth_handler.create_access_token(
        data={"sub": sample_user_data["email"]}
    )


@pytest.fixture(scope="function")
def expired_access_token(auth_handler: AuthHandler, sample_user_data: dict) -> str:
    """create an expired access token"""
    from datetime import timedelta
    return auth_handler.create_access_token(
        data={"sub": sample_user_data["email"]},
        expires_delta=timedelta(seconds=-1)  #already expired
    )


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """setup and teardown for entire test session"""
    #setup
    test_data_dir = Path("tests/test_data")
    test_data_dir.mkdir(parents=True, exist_ok=True)
    
    yield
    
    #teardown
    if test_data_dir.exists():
        shutil.rmtree(test_data_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def temp_directory() -> Generator[Path, None, None]:
    """create a temporary directory for tests"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

