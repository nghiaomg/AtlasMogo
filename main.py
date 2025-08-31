#!/usr/bin/env python3
"""
AtlasMogo - MongoDB Management Tool
Main entry point for the application.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging and configuration
from config.logging_config import LoggingConfig
from config.settings import Settings

# Ensure required directories exist
Settings.ensure_directories()

# Setup logging
LoggingConfig.setup_logging()

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from presentation.main_window import MainWindow


def main():
    """Main entry point for AtlasMogo application."""
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName(Settings.APP_NAME)
    app.setApplicationVersion(Settings.APP_VERSION)
    app.setOrganizationName(Settings.APP_NAME)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show main window
    main_window = MainWindow()
    main_window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
