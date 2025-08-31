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
from PySide6.QtGui import QIcon
from presentation.windows.main_window import MainWindow


def _set_application_icon(app):
    """Set the global application icon."""
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Try multiple paths for the icon file
    icon_paths = [
        "resources/icons/icon.ico",  # Relative to current directory
        os.path.join(os.getcwd(), "resources", "icons", "icon.ico"),  # Relative to working directory
    ]
    
    # For PyInstaller bundled app
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_path = sys._MEIPASS
        icon_paths.insert(0, os.path.join(base_path, "resources", "icons", "icon.ico"))
    
    icon_set = False
    for icon_path in icon_paths:
        if os.path.exists(icon_path):
            try:
                app.setWindowIcon(QIcon(icon_path))
                logger.info(f"Global app icon loaded from {icon_path}")
                icon_set = True
                break
            except Exception as e:
                logger.warning(f"Failed to load global icon from {icon_path}: {e}")
                continue
    
    if not icon_set:
        logger.error("Could not load global application icon from any of the expected paths")


def main():
    """Main entry point for AtlasMogo application."""
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName(Settings.APP_NAME)
    app.setApplicationVersion(Settings.APP_VERSION)
    app.setOrganizationName(Settings.APP_NAME)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Set global application icon
    _set_application_icon(app)
    
    # Create and show main window
    main_window = MainWindow()
    main_window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
