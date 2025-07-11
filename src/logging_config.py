"""
Logging Configuration
Centralized logging setup for the Recipe Assistant application
"""

import os
import sys
import logging
import logging.config
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import json


class LogFormatter(logging.Formatter):
    """Custom formatter with color support for console output"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def __init__(self, use_colors: bool = True, include_location: bool = False):
        self.use_colors = use_colors and sys.stdout.isatty()
        self.include_location = include_location
        
        if self.include_location:
            fmt = '%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s'
        else:
            fmt = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
            
        super().__init__(fmt, datefmt='%Y-%m-%d %H:%M:%S')
    
    def format(self, record):
        if self.use_colors:
            # Add color to level name
            level_color = self.COLORS.get(record.levelname, '')
            reset_color = self.COLORS['RESET']
            
            # Store original levelname
            original_levelname = record.levelname
            # Add colors
            record.levelname = f"{level_color}{record.levelname}{reset_color}"
            
            # Format the message
            formatted = super().format(record)
            
            # Restore original levelname
            record.levelname = original_levelname
            
            return formatted
        else:
            return super().format(record)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging in production"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created',
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'getMessage', 'exc_info',
                          'exc_text', 'stack_info']:
                log_entry[key] = value
        
        return json.dumps(log_entry)


class LoggingConfig:
    """Centralized logging configuration"""
    
    def __init__(self, 
                 app_name: str = "recipe_assistant",
                 log_level: str = "INFO",
                 log_dir: Optional[str] = None,
                 enable_console: bool = True,
                 enable_file: bool = True,
                 enable_json: bool = False,
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5):
        
        self.app_name = app_name
        self.log_level = log_level.upper()
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.enable_json = enable_json
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        
        # Set up log directory
        if log_dir:
            self.log_dir = Path(log_dir)
        else:
            self.log_dir = Path.cwd() / "logs"
        
        self.log_dir.mkdir(exist_ok=True)
        
        # Log file paths
        self.app_log_file = self.log_dir / f"{app_name}.log"
        self.error_log_file = self.log_dir / f"{app_name}_error.log"
        self.access_log_file = self.log_dir / f"{app_name}_access.log"
    
    def get_config(self) -> Dict[str, Any]:
        """Generate logging configuration dictionary"""
        
        config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    '()': LogFormatter,
                    'use_colors': False,
                    'include_location': False
                },
                'detailed': {
                    '()': LogFormatter,
                    'use_colors': False,
                    'include_location': True
                },
                'console': {
                    '()': LogFormatter,
                    'use_colors': True,
                    'include_location': False
                },
                'json': {
                    '()': JSONFormatter,
                }
            },
            'handlers': {},
            'loggers': {
                # Root logger
                '': {
                    'handlers': [],
                    'level': self.log_level,
                    'propagate': False
                },
                # App specific loggers
                'recipe_assistant': {
                    'handlers': [],
                    'level': self.log_level,
                    'propagate': False
                },
                'meal_planner': {
                    'handlers': [],
                    'level': self.log_level,
                    'propagate': False
                },
                'nutrition': {
                    'handlers': [],
                    'level': self.log_level,
                    'propagate': False
                },
                'api': {
                    'handlers': [],
                    'level': self.log_level,
                    'propagate': False
                },
                'database': {
                    'handlers': [],
                    'level': self.log_level,
                    'propagate': False
                },
                # Third-party loggers
                'uvicorn': {
                    'handlers': [],
                    'level': 'INFO',
                    'propagate': False
                },
                'uvicorn.access': {
                    'handlers': [],
                    'level': 'INFO',
                    'propagate': False
                },
                'sqlalchemy.engine': {
                    'handlers': [],
                    'level': 'WARNING',  # Reduce SQL query noise
                    'propagate': False
                },
                'httpx': {
                    'handlers': [],
                    'level': 'WARNING',
                    'propagate': False
                }
            }
        }
        
        handlers = []
        
        # Console handler
        if self.enable_console:
            config['handlers']['console'] = {
                'class': 'logging.StreamHandler',
                'formatter': 'console',
                'stream': 'ext://sys.stdout'
            }
            handlers.append('console')
        
        # File handlers
        if self.enable_file:
            # Main application log
            config['handlers']['file'] = {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'json' if self.enable_json else 'detailed',
                'filename': str(self.app_log_file),
                'maxBytes': self.max_file_size,
                'backupCount': self.backup_count,
                'encoding': 'utf-8'
            }
            handlers.append('file')
            
            # Error log (ERROR and above only)
            config['handlers']['error_file'] = {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'json' if self.enable_json else 'detailed',
                'filename': str(self.error_log_file),
                'maxBytes': self.max_file_size,
                'backupCount': self.backup_count,
                'level': 'ERROR',
                'encoding': 'utf-8'
            }
            handlers.append('error_file')
            
            # Access log for API requests
            config['handlers']['access_file'] = {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'standard',
                'filename': str(self.access_log_file),
                'maxBytes': self.max_file_size,
                'backupCount': self.backup_count,
                'encoding': 'utf-8'
            }
        
        # Assign handlers to all loggers
        for logger_name in config['loggers']:
            if logger_name == 'uvicorn.access' and self.enable_file:
                config['loggers'][logger_name]['handlers'] = ['access_file']
            else:
                config['loggers'][logger_name]['handlers'] = handlers
        
        return config