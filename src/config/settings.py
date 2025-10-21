"""
Application settings and configuration
Manages environment-based configuration for development, staging, and production
"""

import os
import secrets
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Recipe Assistant API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # Server
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    WORKERS: int = Field(default=1, env="WORKERS")
    
    # Database
    DATABASE_URL: str = Field(
        default="data/recipe_assistant.db",
        env="DATABASE_URL"
    )
    DATABASE_BACKUP_ENABLED: bool = True
    DATABASE_BACKUP_INTERVAL_HOURS: int = 24
    
    # JWT Authentication
    JWT_SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        env="JWT_SECRET_KEY"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Security
    BCRYPT_ROUNDS: int = 12
    PASSWORD_MIN_LENGTH: int = 8
    SESSION_SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        env="SESSION_SECRET_KEY"
    )
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
        ],
        env="CORS_ORIGINS"
    )
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_IMAGE_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "webp", "gif"]
    ALLOWED_DOCUMENT_EXTENSIONS: List[str] = ["pdf", "txt"]
    UPLOAD_DIR: str = "data/uploads"
    
    # AI Integration
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    AI_ENABLED: bool = Field(default=False, env="AI_ENABLED")
    AI_MAX_TOKENS: int = 2000
    AI_TEMPERATURE: float = 0.7
    
    # Recipe Scraping
    SCRAPING_TIMEOUT_SECONDS: int = 30
    SCRAPING_MAX_RETRIES: int = 3
    SCRAPING_USER_AGENT: str = "RecipeAssistant/1.0"
    
    # Caching
    CACHE_ENABLED: bool = False
    REDIS_URL: Optional[str] = Field(default=None, env="REDIS_URL")
    CACHE_TTL_SECONDS: int = 3600
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = "json"
    LOG_FILE: str = "logs/recipe_assistant.log"
    LOG_MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    # Email (Optional - for password reset, etc.)
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: Optional[int] = Field(default=587, env="SMTP_PORT")
    SMTP_USERNAME: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    SMTP_FROM_EMAIL: Optional[str] = Field(default=None, env="SMTP_FROM_EMAIL")
    EMAIL_ENABLED: bool = False
    
    # External Services
    USDA_API_KEY: Optional[str] = Field(default=None, env="USDA_API_KEY")
    NUTRITION_API_ENABLED: bool = False
    
    # Features Flags
    FEATURE_AI_GENERATION: bool = False
    FEATURE_MEAL_PLANNING: bool = True
    FEATURE_SHOPPING_LISTS: bool = True
    FEATURE_NUTRITION_TRACKING: bool = True
    FEATURE_RECOMMENDATIONS: bool = True
    FEATURE_SOCIAL_SHARING: bool = False
    
    # Frontend URLs (for CORS and links)
    FRONTEND_URL: str = Field(default="http://localhost:3000", env="FRONTEND_URL")
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v = v.upper()
        if v not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return v
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        """Validate environment"""
        valid_envs = ["development", "staging", "production", "testing"]
        v = v.lower()
        if v not in valid_envs:
            raise ValueError(f"Environment must be one of: {', '.join(valid_envs)}")
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing"""
        return self.ENVIRONMENT == "testing"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

