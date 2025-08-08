"""
Session Logger
Provides centralized logging across the Recipe Assistant system.
"""

import logging
from logging.handlers import RotatingFileHandler
import os
from typing import Optional

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

class SessionLogger:
    def __init__(
        self,
        name: str = "RecipeAssistant",
        log_file: str = "session.log",
        max_bytes: int = 1_000_000,
        backup_count: int = 5,
        level: int = logging.INFO
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False  # Avoid duplicate logs

        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        file_handler = RotatingFileHandler(
            os.path.join(LOG_DIR, log_file),
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)

        # Console handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(level)

        # Avoid adding handlers twice
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(stream_handler)

    def info(self, message: str, tag: Optional[str] = None):
        self.logger.info(self._format(message, tag))

    def warning(self, message: str, tag: Optional[str] = None):
        self.logger.warning(self._format(message, tag))

    def error(self, message: str, tag: Optional[str] = None):
        self.logger.error(self._format(message, tag))

    def debug(self, message: str, tag: Optional[str] = None):
        self.logger.debug(self._format(message, tag))

    def _format(self, message: str, tag: Optional[str] = None) -> str:
        return f"[{tag}] {message}" if tag else message
