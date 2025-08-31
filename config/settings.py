"""
Application settings and configuration for AtlasMogo.
Centralizes all configuration values for easy maintenance.
"""

import os
from pathlib import Path
from typing import Dict, Any


class Settings:
    """Application settings and configuration."""
    
    # Application Info
    APP_NAME = "AtlasMogo"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "MongoDB Management Tool"
    
    # Window Settings
    DEFAULT_WINDOW_WIDTH = 1200
    DEFAULT_WINDOW_HEIGHT = 800
    MIN_WINDOW_WIDTH = 800
    MIN_WINDOW_HEIGHT = 600
    TASKBAR_HEIGHT = 40
    
    # MongoDB Defaults
    DEFAULT_MONGODB_URI = "mongodb://localhost:27017"
    DEFAULT_CONNECTION_TIMEOUT = 5000
    DEFAULT_SERVER_SELECTION_TIMEOUT = 3000
    DEFAULT_MAX_POOL_SIZE = 10
    
    # UI Settings
    DEFAULT_SPLITTER_LEFT_RATIO = 0.35
    DEFAULT_SPLITTER_RIGHT_RATIO = 0.65
    MIN_LEFT_PANEL_WIDTH = 300
    MIN_RIGHT_PANEL_WIDTH = 400
    
    # Document Settings
    DEFAULT_DOCUMENT_LIMIT = 50
    MAX_DOCUMENT_LIMIT = 10000
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = "logs/atlasmogo.log"
    MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # File Paths
    BASE_DIR = Path(__file__).parent.parent
    LOGS_DIR = BASE_DIR / "logs"
    CONFIG_DIR = BASE_DIR / "config"
    
    # Theme Settings
    THEME_COLORS = {
        "primary": "#007bff",
        "secondary": "#6c757d",
        "success": "#28a745",
        "danger": "#dc3545",
        "warning": "#ffc107",
        "info": "#17a2b8",
        "light": "#f8f9fa",
        "dark": "#343a40"
    }
    
    # MongoDB System Databases (to exclude from user view)
    SYSTEM_DATABASES = ['admin', 'local', 'config']
    
    @classmethod
    def get_mongodb_config(cls) -> Dict[str, Any]:
        """Get MongoDB connection configuration."""
        return {
            "uri": os.getenv("MONGODB_URI", cls.DEFAULT_MONGODB_URI),
            "timeout": int(os.getenv("MONGODB_TIMEOUT", cls.DEFAULT_CONNECTION_TIMEOUT)),
            "server_selection_timeout": int(os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT", cls.DEFAULT_SERVER_SELECTION_TIMEOUT)),
            "max_pool_size": int(os.getenv("MONGODB_MAX_POOL_SIZE", cls.DEFAULT_MAX_POOL_SIZE))
        }
    
    @classmethod
    def get_window_config(cls) -> Dict[str, Any]:
        """Get window configuration."""
        return {
            "width": int(os.getenv("WINDOW_WIDTH", cls.DEFAULT_WINDOW_WIDTH)),
            "height": int(os.getenv("WINDOW_HEIGHT", cls.DEFAULT_WINDOW_HEIGHT)),
            "min_width": cls.MIN_WINDOW_WIDTH,
            "min_height": cls.MIN_WINDOW_HEIGHT
        }
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure required directories exist."""
        cls.LOGS_DIR.mkdir(exist_ok=True)
        cls.CONFIG_DIR.mkdir(exist_ok=True)
