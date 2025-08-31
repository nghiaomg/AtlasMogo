"""
Configuration module for AtlasMogo.
Contains application settings, MongoDB connection defaults, and logging configuration.
"""

from .settings import Settings
from .logging_config import LoggingConfig

__all__ = ['Settings', 'LoggingConfig']
