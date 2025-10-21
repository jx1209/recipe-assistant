"""
authentication system tests
tests for password hashing, jwt tokens, and auth handler
"""

import pytest
from datetime import timedelta
from jose import jwt, JWTError

from src.auth.auth_handler import AuthHandler
from src.config.settings import get_settings


@pytest.mark.unit
@pytest.mark.auth
class TestPasswordHashing:
    """test password hashing functionality"""
    
    def test_password_hash_creation(self, auth_handler: AuthHandler):
        """test creating a password hash"""
        password = "SecurePassword123!"
        hashed = auth_handler.get_password_hash(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  #bcrypt prefix
    
    def test_password_verification_success(self, auth_handler: AuthHandler):
        """test verifying correct password"""
        password = "SecurePassword123!"
        hashed = auth_handler.get_password_hash(password)
        
        assert auth_handler.verify_password(password, hashed) is True
    
    def test_password_verification_failure(self, auth_handler: AuthHandler):
        """test verifying incorrect password"""
        password = "SecurePassword123!"
        wrong_password = "WrongPassword456!"
        hashed = auth_handler.get_password_hash(password)
        
        assert auth_handler.verify_password(wrong_password, hashed) is False
    
    def test_same_password_different_hashes(self, auth_handler: AuthHandler):
        """test that same password generates different hashes (salt)"""
        password = "SecurePassword123!"
        hash1 = auth_handler.get_password_hash(password)
        hash2 = auth_handler.get_password_hash(password)
        
        assert hash1 != hash2
        assert auth_handler.verify_password(password, hash1) is True
        assert auth_handler.verify_password(password, hash2) is True


@pytest.mark.unit
@pytest.mark.auth
class TestJWTTokens:
    """test jwt token creation and validation"""
    
    def test_create_access_token(self, auth_handler: AuthHandler):
        """test creating an access token"""
        data = {"sub": "test@example.com"}
        token = auth_handler.create_access_token(data=data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_refresh_token(self, auth_handler: AuthHandler):
        """test creating a refresh token"""
        data = {"sub": "test@example.com"}
        token = auth_handler.create_refresh_token(data=data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_decode_valid_token(self, auth_handler: AuthHandler):
        """test decoding a valid token"""
        email = "test@example.com"
        token = auth_handler.create_access_token(data={"sub": email})
        
        decoded_email = auth_handler.verify_token(token)
        
        assert decoded_email == email
    
    def test_decode_expired_token(self, auth_handler: AuthHandler):
        """test decoding an expired token"""
        email = "test@example.com"
        token = auth_handler.create_access_token(
            data={"sub": email},
            expires_delta=timedelta(seconds=-1)  #already expired
        )
        
        with pytest.raises(Exception):  #should raise jwt error
            auth_handler.verify_token(token)
    
    def test_decode_invalid_token(self, auth_handler: AuthHandler):
        """test decoding an invalid token"""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(Exception):
            auth_handler.verify_token(invalid_token)
    
    def test_token_contains_correct_data(self, auth_handler: AuthHandler):
        """test that token contains correct payload data"""
        email = "test@example.com"
        settings = get_settings()
        token = auth_handler.create_access_token(data={"sub": email})
        
        #decode without verification for testing
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        assert payload["sub"] == email
        assert "exp" in payload  #expiration time
    
    def test_custom_expiration_time(self, auth_handler: AuthHandler):
        """test creating token with custom expiration"""
        email = "test@example.com"
        custom_expiry = timedelta(hours=1)
        token = auth_handler.create_access_token(
            data={"sub": email},
            expires_delta=custom_expiry
        )
        
        assert token is not None
        decoded_email = auth_handler.verify_token(token)
        assert decoded_email == email


@pytest.mark.unit
@pytest.mark.auth
class TestTokenBlacklist:
    """test token blacklisting functionality"""
    
    def test_add_token_to_blacklist(self, auth_handler: AuthHandler):
        """test adding a token to blacklist"""
        token = auth_handler.create_access_token(data={"sub": "test@example.com"})
        
        auth_handler.blacklist_token(token)
        
        assert auth_handler.is_token_blacklisted(token) is True
    
    def test_token_not_in_blacklist(self, auth_handler: AuthHandler):
        """test checking token not in blacklist"""
        token = auth_handler.create_access_token(data={"sub": "test@example.com"})
        
        assert auth_handler.is_token_blacklisted(token) is False
    
    def test_verify_blacklisted_token(self, auth_handler: AuthHandler):
        """test verifying a blacklisted token raises error"""
        email = "test@example.com"
        token = auth_handler.create_access_token(data={"sub": email})
        
        #blacklist the token
        auth_handler.blacklist_token(token)
        
        #try to verify it
        with pytest.raises(Exception):
            auth_handler.verify_token(token)


@pytest.mark.unit
@pytest.mark.auth
class TestAuthHandler:
    """test auth handler integration"""
    
    def test_auth_handler_initialization(self):
        """test creating auth handler"""
        handler = AuthHandler()
        assert handler is not None
    
    def test_full_auth_flow(self, auth_handler: AuthHandler):
        """test complete authentication flow"""
        #user registers with password
        password = "SecurePassword123!"
        hashed_password = auth_handler.get_password_hash(password)
        
        #user logs in
        assert auth_handler.verify_password(password, hashed_password) is True
        
        #create access token
        email = "test@example.com"
        access_token = auth_handler.create_access_token(data={"sub": email})
        
        #verify token
        decoded_email = auth_handler.verify_token(access_token)
        assert decoded_email == email
        
        #logout (blacklist token)
        auth_handler.blacklist_token(access_token)
        
        #token should now be invalid
        with pytest.raises(Exception):
            auth_handler.verify_token(access_token)

