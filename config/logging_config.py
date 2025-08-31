"""
Logging configuration for AtlasMogo.
Provides centralized logging setup and configuration.
"""

import logging
import logging.handlers
from pathlib import Path
from .settings import Settings


class LoggingConfig:
    """Logging configuration and setup."""
    
    @staticmethod
    def setup_logging() -> None:
        """Setup application logging."""
        # Ensure logs directory exists
        Settings.ensure_directories()
        
        # Create logger
        logger = logging.getLogger()
        logger.setLevel(getattr(logging, Settings.LOG_LEVEL))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(Settings.LOG_FORMAT)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler with rotation
        log_file = Settings.LOGS_DIR / "atlasmogo.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=Settings.MAX_LOG_SIZE,
            backupCount=Settings.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Set specific logger levels
        logging.getLogger('pymongo').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        
        logger.info(f"Logging initialized. Log file: {log_file}")
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get a logger instance for the specified module."""
        return logging.getLogger(name)
    
    @staticmethod
    def set_log_level(level: str) -> None:
        """Set the application log level."""
        try:
            log_level = getattr(logging, level.upper())
            logging.getLogger().setLevel(log_level)
            logging.info(f"Log level set to: {level.upper()}")
        except AttributeError:
            logging.warning(f"Invalid log level: {level}. Using INFO instead.")
            logging.getLogger().setLevel(logging.INFO)
