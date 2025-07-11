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
        super().__init__(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
#        if self.include_location:
#            fmt = '%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s'
#        else:
#            fmt = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
            
#        super().__init__(fmt, datefmt='%Y-%m-%d %H:%M:%S')
    
    def format(self, record):
        if self.use_colors:
            level_color = self.COLORS.get(record.levelname, '')
            reset_color = self.COLORS['RESET']
            record.levelname = f"{level_color}{record.levelname}{reset_color}"
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

def setup_logging(
    app_name="recipe_assistant",
    log_level=None,
    log_dir=None,
    console=True,
    file_logging=True,
    json_format=None
):

    env = os.getenv('ENVIRONMENT', 'development').lower()
    is_dev = env == 'development'
    
    if log_level is None:
        log_level = 'DEBUG' if is_dev else 'INFO'
    if json_format is None:
        json_format = not is_dev
    if log_dir is None:
        log_dir = os.getenv('LOG_DIR', 'logs')
    
    log_level = os.getenv('LOG_LEVEL', log_level).upper()
    if os.getenv('DISABLE_CONSOLE_LOGGING', '').lower() in ('true', '1'):
        console = False
    if os.getenv('DISABLE_FILE_LOGGING', '').lower() in ('true', '1'):
        file_logging = False
    
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'detailed': {
                'format': '%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'console': {
                'format': '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'json': {
                '()': JSONFormatter
            }
        },
        'handlers': {},
        'loggers': {
            '': {
                'level': log_level,
                'handlers': [],
                'propagate': False
            },
            'recipe_assistant': {
                'level': log_level,
                'handlers': [],
                'propagate': False
            },
            'uvicorn':{
                'level': log_level,
                'handlers': [],
                'propagate': False
            },
            'uvicorn.access': {
                'level': 'INFO',
                'handlers': [],
                'propagate': False
            },
            'uvicorn.error': {
                'level': 'ERROR',
                'handlers': [],
                'propagate': False
            },
            'sqlalchemy.engine': {
                'level': 'WARNING',
                'handlers': [],
                'propagate': False
            }
        }
    }

    handlers = []
    
    if console:
        config['handlers']['console'] = {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
            'stream': 'ext://sys.stdout'
        }
        handlers.append('console')
    
    if file_logging:
        formatter = 'json' if json_format else 'detailed'
        
        config['handlers']['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': formatter,
            'filename': str(log_path / f'{app_name}.log'),
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'encoding': 'utf-8'
        }
        
        config['handlers']['error'] = {
            'class': 'logging.handlers.RotatingFileHandler', 
            'formatter': formatter,
            'filename': str(log_path / f'{app_name}_error.log'),
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 5,
            'level': 'ERROR',
            'encoding': 'utf-8'
        }
        
        config['handlers']['access'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard', 
            'filename': str(log_path / f'{app_name}_access.log'),
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 5,
            'encoding': 'utf-8'
        }
        
        handlers.extend(['file', 'error'])
    
    # Assign handlers
    for logger_name in config['loggers']:
        if logger_name == 'uvicorn.access' and file_logging:
            config['loggers'][logger_name]['handlers'] = ['access']
        else:
            config['loggers'][logger_name]['handlers'] = handlers
    
    logging.config.dictConfig(config)
    
    logger = logging.getLogger(f'{app_name}.config')
    logger.info(f"Logging configured - Level: {log_level}, Dir: {log_dir}")

def get_logger(name):
    return logging.getLogger(name)


def log_performance(func):
    """Decorator to log function execution time"""
    import time
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start
            if duration > 1.0:  # Only log slow operations
                logger.info(f"{func.__name__} took {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start
            logger.error(f"{func.__name__} failed after {duration:.2f}s: {e}")
            raise
    return wrapper


class RequestLogger:
    """Context manager for request-specific logging"""
    
    def __init__(self, logger, request_id=None, user_id=None):
        self.logger = logger
        self.context = {
            'request_id': request_id,
            'user_id': user_id
        }
    
    def info(self, msg, **kwargs):
        self._log('info', msg, **kwargs)
    
    def debug(self, msg, **kwargs):
        self._log('debug', msg, **kwargs)
    
    def warning(self, msg, **kwargs):
        self._log('warning', msg, **kwargs)
    
    def error(self, msg, **kwargs):
        self._log('error', msg, **kwargs)
    
    def _log(self, level, msg, **kwargs):
        extra = kwargs.get('extra', {})
        extra.update(self.context)
        kwargs['extra'] = extra
        getattr(self.logger, level)(msg, **kwargs)