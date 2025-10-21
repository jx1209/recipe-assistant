"""
api authentication endpoint tests
tests for registration, login, and user management endpoints
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.database.db_manager import DatabaseManager
from src.auth.auth_handler import AuthHandler


@pytest.fixture(scope="function")
def client(test_db: DatabaseManager):
    """create test client"""
    #override database dependency
    from src.api.main import app
    return TestClient(app)


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.auth
class TestRegistrationEndpoint:
    """test user registration endpoint"""
    
    def test_register_new_user_success(self, client: TestClient):
        """test successful user registration"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "full_name": "New User"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_register_duplicate_email(self, client: TestClient):
        """test registration with duplicate email"""
        #register first user
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "SecurePass123!",
                "full_name": "First User"
            }
        )
        
        #try to register again with same email
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "DifferentPass456!",
                "full_name": "Second User"
            }
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_invalid_email(self, client: TestClient):
        """test registration with invalid email format"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "SecurePass123!",
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == 422
    
    def test_register_weak_password(self, client: TestClient):
        """test registration with weak password"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "weak",
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == 422
    
    def test_register_missing_fields(self, client: TestClient):
        """test registration with missing required fields"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com"
                #missing password
            }
        )
        
        assert response.status_code == 422


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.auth
class TestLoginEndpoint:
    """test user login endpoint"""
    
    def test_login_success(self, client: TestClient):
        """test successful login"""
        #register user
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@example.com",
                "password": "SecurePass123!",
                "full_name": "Login User"
            }
        )
        
        #login
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "login@example.com",
                "password": "SecurePass123!"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client: TestClient):
        """test login with wrong password"""
        #register user
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "user@example.com",
                "password": "CorrectPass123!",
                "full_name": "Test User"
            }
        )
        
        #login with wrong password
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "user@example.com",
                "password": "WrongPass456!"
            }
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, client: TestClient):
        """test login with non-existent email"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "SomePass123!"
            }
        )
        
        assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.auth
class TestProtectedEndpoints:
    """test protected endpoints requiring authentication"""
    
    def test_get_current_user_success(self, client: TestClient):
        """test getting current user profile with valid token"""
        #register and get token
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "profile@example.com",
                "password": "SecurePass123!",
                "full_name": "Profile User"
            }
        )
        access_token = register_response.json()["access_token"]
        
        #get profile
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "profile@example.com"
        assert data["full_name"] == "Profile User"
    
    def test_get_current_user_no_token(self, client: TestClient):
        """test getting profile without token"""
        response = client.get("/api/v1/users/me")
        
        assert response.status_code == 401
    
    def test_get_current_user_invalid_token(self, client: TestClient):
        """test getting profile with invalid token"""
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid-token"}
        )
        
        assert response.status_code == 401
    
    def test_update_user_profile(self, client: TestClient):
        """test updating user profile"""
        #register and get token
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "update@example.com",
                "password": "SecurePass123!",
                "full_name": "Original Name"
            }
        )
        access_token = register_response.json()["access_token"]
        
        #update profile
        response = client.put(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"full_name": "Updated Name"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.auth
class TestTokenRefresh:
    """test token refresh functionality"""
    
    def test_refresh_token_success(self, client: TestClient):
        """test refreshing access token"""
        #register and get tokens
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "refresh@example.com",
                "password": "SecurePass123!",
                "full_name": "Refresh User"
            }
        )
        refresh_token = register_response.json()["refresh_token"]
        
        #refresh token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_refresh_invalid_token(self, client: TestClient):
        """test refreshing with invalid token"""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid-refresh-token"}
        )
        
        assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.auth
class TestLogout:
    """test logout functionality"""
    
    def test_logout_success(self, client: TestClient):
        """test logging out (blacklisting token)"""
        #register and get token
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "logout@example.com",
                "password": "SecurePass123!",
                "full_name": "Logout User"
            }
        )
        access_token = register_response.json()["access_token"]
        
        #logout
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 200
        assert "successfully" in response.json()["message"].lower()
        
        #try to use token after logout
        profile_response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert profile_response.status_code == 401

