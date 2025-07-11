"""
Global Configuration Management
Centralized configuration for the Recipe Assistant application
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class APIConfig:
    """API configuration settings"""
    spoonacular_key: Optional[str] = None
    edamam_app_id: Optional[str] = None
    edamam_app_key: Optional[str] = None
    
    # Rate limiting
    max_requests_per_minute: int = 50
    request_timeout: int = 10
    retry_attempts: int = 3
    
    def __post_init__(self):
        self.spoonacular_key = os.getenv('SPOONACULAR_API_KEY')
        self.edamam_app_id = os.getenv('EDAMAM_APP_ID')
        self.edamam_app_key = os.getenv('EDAMAM_APP_KEY')
    
    @property
    def has_spoonacular(self) -> bool:
        return bool(self.spoonacular_key)
    
    @property
    def has_edamam(self) -> bool:
        return bool(self.edamam_app_id and self.edamam_app_key)
    
    @property
    def available_apis(self) -> list:
        apis = ['themealdb']  # (free)
        if self.has_spoonacular:
            apis.append('spoonacular')
        if self.has_edamam:
            apis.append('edamam')
        return apis

@dataclass
class DatabaseConfig:
    """Database configuration"""
    sqlite_file: str = "data/recipes.db"
    json_backup_file: str = "data/recipes.json"
    backup_directory: str = "data/backups"

    enable_cache: bool = True
    cache_size: int = 1000
    cache_ttl_seconds: int = 3600
    
    auto_backup: bool = True
    backup_interval_hours: int = 24
    cleanup_old_backups_days: int = 30

@dataclass
class WebConfig:
    """Web application configuration"""
    host: str = "127.0.0.1"
    port: int = 5000
    debug: bool = True
    secret_key: str = "dev-secret-key-change-in-production"
    
    upload_folder: str = "static/uploads"
    max_file_size_mb: int = 16
    allowed_extensions: tuple = ('png', 'jpg', 'jpeg', 'gif', 'webp')
    
    def __post_init__(self):
        self.debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
        self.secret_key = os.getenv('SECRET_KEY', self.secret_key)
        self.host = os.getenv('FLASK_HOST', self.host)
        self.port = int(os.getenv('FLASK_PORT', self.port))

@dataclass
class AIConfig:
    """AI and ML configuration"""
    enable_recommendations: bool = True
    enable_image_recognition: bool = False
    enable_recipe_generation: bool = False
    
    min_similarity_threshold: float = 0.3
    max_recommendations: int = 10
    learning_rate: float = 0.01

    image_model_path: str = "models/ingredient_classifier.pkl"
    confidence_threshold: float = 0.7

@dataclass
class UserConfig:
    """User management configuration"""
    enable_user_accounts: bool = False
    enable_social_features: bool = False
    default_dietary_restrictions: list = None
    #max_saved_recipes: int = 100

    session_timeout_hours: int = 24
    remember_me_days: int = 30
    
    def __post_init__(self):
        if self.default_dietary_restrictions is None:
            self.default_dietary_restrictions = []

class Config:
    """Main configuration class"""
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.project_root = Path(__file__).parent.parent
        
        self.api = APIConfig()
        self.database = DatabaseConfig()
        self.web = WebConfig()
        self.ai = AIConfig()
        self.user = UserConfig()
    
        self._apply_environment_settings()
        
        self._create_directories()

    def _apply_environment_settings(self):
        """Apply environment-specific configuration"""
        if self.environment == "production":
            self.web.debug = False
            self.database.enable_cache = True
            self.database.cache_size = 5000
            self.api.max_requests_per_minute = 100
        
        elif self.environment == "testing":
            self.database.sqlite_file = ":memory:"
            self.database.enable_cache = False
            self.web.debug = True
            self.ai.enable_recommendations = False
        
        elif self.environment == "development":
            self.web.debug = True
            self.database.enable_cache = True
            self.ai.enable_recommendations = True
    
    def _create_directories(self):
        """Create necessary directories"""
        directories = [
            Path(self.database.backup_directory),
            Path(self.web.upload_folder),
            Path("data"),
            Path("logs"),
            Path("models")
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_database_url(self) -> str:
        """Get database connection URL"""
        if self.database.sqlite_file == ":memory:":
            return "sqlite:///:memory:"
        return f"sqlite:///{self.database.sqlite_file}"
    
    def get_log_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        log_level = "DEBUG" if self.web.debug else "INFO"
        
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
                },
                'detailed': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s [%(filename)s:%(lineno)d]: %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'level': log_level,
                    'class': 'logging.StreamHandler',
                    'formatter': 'standard'
                },
                'file': {
                    'level': 'INFO',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': 'logs/recipe_assistant.log',
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 5,
                    'formatter': 'detailed'
                }
            },
            'loggers': {
                '': {
                    'handlers': ['console', 'file'],
                    'level': log_level,
                    'propagate': False
                }
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'environment': self.environment,
            'api': {
                'available_apis': self.api.available_apis,
                'has_spoonacular': self.api.has_spoonacular,
                'has_edamam': self.api.has_edamam,
                'max_requests_per_minute': self.api.max_requests_per_minute
            },
            'database': {
                'sqlite_file': self.database.sqlite_file,
                'enable_cache': self.database.enable_cache,
                'cache_size': self.database.cache_size
            },
            'web': {
                'host': self.web.host,
                'port': self.web.port,
                'debug': self.web.debug
            },
            'ai': {
                'enable_recommendations': self.ai.enable_recommendations,
                'enable_image_recognition': self.ai.enable_image_recognition
            }
        }
    
    def validate(self) -> list[str]:
        """Validate configuration and return any errors"""
        errors = []
    
        if not self.api.available_apis:
            errors.append("No recipe APIs available - consider adding API keys")
        
        if self.database.cache_size < 0:
            errors.append("Database cache size must be non-negative")

        if not (1024 <= self.web.port <= 65535):
            errors.append("Web port must be between 1024 and 65535")

        if not Path(self.database.backup_directory).exists():
            errors.append(f"Backup directory does not exist: {self.database.backup_directory}")
        
        return errors

development_config = Config("development")
production_config = Config("production")
testing_config = Config("testing")

current_environment = os.getenv('ENVIRONMENT', 'development').lower()
config_map = {
    'development': development_config,
    'production': production_config,
    'testing': testing_config
}

config = config_map.get(current_environment, development_config)

def get_config(environment: str = None) -> Config:
    """Get configuration for specific environment"""
    if environment is None:
        return config
    return config_map.get(environment.lower(), development_config)

def is_production() -> bool:
    """Check if running in production"""
    return config.environment == "production"

def is_development() -> bool:
    """Check if running in development"""
    return config.environment == "development"

def has_api_keys() -> bool:
    """Check if any API keys are configured"""
    return len(config.api.available_apis) > 1 