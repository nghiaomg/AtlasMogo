"""
Dialog Logging System
Provides comprehensive logging for all dialog button actions in AtlasMogo.
"""

import logging
import os
from datetime import datetime
from typing import Optional, Callable
from PySide6.QtWidgets import QPushButton, QDialog
from PySide6.QtCore import QObject


class DialogLogger:
    """Centralized logging system for AtlasMogo dialogs."""
    
    _logger = None
    
    @classmethod
    def get_logger(cls) -> logging.Logger:
        """Get or create the dialog logger."""
        if cls._logger is None:
            # Create logs directory if it doesn't exist
            os.makedirs("logs", exist_ok=True)
            
            # Create logger
            logger = logging.getLogger("AtlasMogo.Dialogs")
            logger.setLevel(logging.INFO)
            
            # Prevent duplicate handlers
            if not logger.handlers:
                # File handler for dialog-specific logs
                file_handler = logging.FileHandler("logs/dialogs.log", encoding='utf-8')
                file_handler.setLevel(logging.INFO)
                
                # Console handler for development
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.INFO)
                
                # Formatter
                formatter = logging.Formatter(
                    '[%(asctime)s] [%(name)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                file_handler.setFormatter(formatter)
                console_handler.setFormatter(formatter)
                
                logger.addHandler(file_handler)
                logger.addHandler(console_handler)
            
            cls._logger = logger
        
        return cls._logger
    
    @classmethod
    def log_button_created(cls, button: QPushButton, role: str, action: Optional[Callable] = None, dialog: Optional[QDialog] = None):
        """Log when a button is created."""
        logger = cls.get_logger()
        dialog_title = dialog.windowTitle() if dialog else "Unknown"
        action_name = action.__name__ if action else "None"
        
        logger.info(f"[DIALOG: {dialog_title}] [BUTTON: {button.text()}] → Created | Role: {role} | Action: {action_name}")
    
    @classmethod
    def log_button_clicked(cls, button: QPushButton, role: str, action: Optional[Callable] = None, dialog: Optional[QDialog] = None):
        """Log when a button is clicked."""
        logger = cls.get_logger()
        dialog_title = dialog.windowTitle() if dialog else "Unknown"
        action_name = action.__name__ if action else "None"
        
        logger.info(f"[DIALOG: {dialog_title}] [BUTTON: {button.text()}] → Clicked | Role: {role} | Action: {action_name}")
    
    @classmethod
    def log_action_success(cls, button: QPushButton, role: str, dialog: Optional[QDialog] = None, details: str = ""):
        """Log successful button action execution."""
        logger = cls.get_logger()
        dialog_title = dialog.windowTitle() if dialog else "Unknown"
        dialog_closed = not dialog.isVisible() if dialog else "Unknown"
        
        message = f"[DIALOG: {dialog_title}] [BUTTON: {button.text()}] → Status: SUCCESS | Dialog closed: {dialog_closed}"
        if details:
            message += f" | Details: {details}"
        
        logger.info(message)
    
    @classmethod
    def log_action_failed(cls, button: QPushButton, role: str, error: Exception, dialog: Optional[QDialog] = None):
        """Log failed button action execution."""
        logger = cls.get_logger()
        dialog_title = dialog.windowTitle() if dialog else "Unknown"
        
        logger.error(
            f"[DIALOG: {dialog_title}] [BUTTON: {button.text()}] → Status: FAILED | Error: {str(error)}",
            exc_info=True
        )


def bind_button(button: QPushButton, action: Optional[Callable], dialog: QDialog, role: str, 
                custom_action_name: Optional[str] = None) -> QPushButton:
    """
    Bind a button to an action with comprehensive logging.
    
    Args:
        button: The QPushButton to bind
        action: The action function to execute (can be None for accept/reject only)
        dialog: The parent dialog
        role: Button role ("ok", "cancel", "yes", "no", "destructive", "primary", "secondary")
        custom_action_name: Optional custom name for the action (for logging)
        
    Returns:
        QPushButton: The button with logging wrapper attached
    """
    logger = DialogLogger.get_logger()
    
    # Log button creation
    DialogLogger.log_button_created(button, role, action, dialog)
    
    def wrapped_action():
        """Wrapped action with comprehensive logging."""
        # Log button click
        DialogLogger.log_button_clicked(button, role, action, dialog)
        
        try:
            # Execute custom action if provided
            if action:
                action_name = custom_action_name or action.__name__ or "custom_action"
                logger.info(f"[DIALOG: {dialog.windowTitle()}] [BUTTON: {button.text()}] → Executing action: {action_name}")
                action()
            
            # Execute dialog action based on role
            if role in ("ok", "yes", "primary", "destructive"):
                logger.info(f"[DIALOG: {dialog.windowTitle()}] [BUTTON: {button.text()}] → Calling dialog.accept()")
                dialog.accept()
            elif role in ("cancel", "no", "reject", "secondary"):
                logger.info(f"[DIALOG: {dialog.windowTitle()}] [BUTTON: {button.text()}] → Calling dialog.reject()")
                dialog.reject()
            
            # Log success
            DialogLogger.log_action_success(button, role, dialog)
            
        except Exception as e:
            # Log failure
            DialogLogger.log_action_failed(button, role, e, dialog)
            raise  # Re-raise the exception for proper error handling
    
    # Connect the wrapped action
    button.clicked.connect(wrapped_action)
    
    return button


def log_dialog_creation(dialog: QDialog, dialog_type: str):
    """Log when a dialog is created."""
    logger = DialogLogger.get_logger()
    logger.info(f"[DIALOG: {dialog.windowTitle()}] → Created | Type: {dialog_type}")


def log_dialog_result(dialog: QDialog, result: int):
    """Log dialog result when it closes."""
    logger = DialogLogger.get_logger()
    result_text = "Accepted" if result == QDialog.Accepted else "Rejected"
    logger.info(f"[DIALOG: {dialog.windowTitle()}] → Result: {result_text} ({result})")
