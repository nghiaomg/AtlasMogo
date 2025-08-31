"""
Custom Message Box Helper
Provides consistent button styling for all message boxes in AtlasMogo.
Replaces default QMessageBox with custom styled buttons.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QMessageBox, QDialogButtonBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import qtawesome as fa

from .styles import BUTTON_STYLES, DIALOG_STYLE, COLORS


class CustomMessageBox(QDialog):
    """Custom message box with standardized button styling."""
    
    def __init__(self, parent=None, title="Message", message="", 
                 buttons=None, icon=None, is_destructive=False):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 200)
        
        self.title = title
        self.message = message
        self.buttons = buttons or []
        self.icon = icon
        self.is_destructive = is_destructive
        self.result = None
        self.default_result = None  # Store default result for when dialog is cancelled
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the message box UI."""
        # Apply consistent dialog styling
        self.setStyleSheet(DIALOG_STYLE)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Title section
        title_layout = QVBoxLayout()
        title_layout.setSpacing(8)
        
        # Main title
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {COLORS['text_primary']}; margin-bottom: 8px;")
        title_layout.addWidget(title_label)
        
        # Message
        message_label = QLabel(self.message)
        message_label.setFont(QFont("Arial", 12))
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet(f"color: {COLORS['text_secondary']}; margin-bottom: 16px;")
        message_label.setWordWrap(True)
        title_layout.addWidget(message_label)
        
        layout.addLayout(title_layout)
        
        # Buttons
        if self.buttons:
            button_layout = QHBoxLayout()
            button_layout.setSpacing(12)
            button_layout.setContentsMargins(0, 16, 0, 0)
            
            # Add stretch to push buttons to the right
            button_layout.addStretch()
            
            # Create buttons based on the buttons list
            for button_info in reversed(self.buttons):  # Reverse for proper positioning
                text = button_info.get('text', '')
                role = button_info.get('role', 'secondary')
                action = button_info.get('action', None)
                
                btn = QPushButton(text)
                
                # Apply role-based styling
                if role == 'primary':
                    btn.setStyleSheet(BUTTON_STYLES['dialog_primary'])
                    if self.icon:
                        btn.setIcon(fa.icon(self.icon))
                elif role == 'destructive':
                    btn.setStyleSheet(BUTTON_STYLES['dialog_destructive'])
                    btn.setIcon(fa.icon('fa6s.trash'))
                elif role == 'neutral':
                    btn.setStyleSheet(BUTTON_STYLES['dialog_neutral'])
                    if self.icon:
                        btn.setIcon(fa.icon(self.icon))
                else:  # secondary
                    btn.setStyleSheet(BUTTON_STYLES['dialog_secondary'])
                    btn.setIcon(fa.icon('fa6s.xmark'))
                
                if action:
                    btn.clicked.connect(action)
                else:
                    btn.clicked.connect(lambda checked, b=btn: self.button_clicked(b))
                
                button_layout.addWidget(btn)
            
            layout.addLayout(button_layout)
    
    def button_clicked(self, button):
        """Handle button click and set result."""
        self.result = button.text()
        self.accept()
    
    def rejectEvent(self, event):
        """Handle dialog rejection (Escape key, X button)."""
        # Set default result when dialog is cancelled
        if self.result is None:
            # For Yes/No dialogs, default to "No"
            if any(btn.get('text') in ['Yes', 'No'] for btn in self.buttons):
                self.result = 'No'
            # For Delete/Cancel dialogs, default to "Cancel"
            elif any(btn.get('text') in ['Delete', 'Cancel'] for btn in self.buttons):
                self.result = 'Cancel'
            # For other dialogs, use the last button (usually Cancel/No)
            elif self.buttons:
                self.result = self.buttons[-1]['text']
        
        super().rejectEvent(event)
    
    def get_result(self):
        """Get the clicked button result."""
        return self.result


class MessageBoxHelper:
    """Helper class for creating consistent message boxes."""
    
    @staticmethod
    def information(parent, title, message, icon="fa6s.info"):
        """Show an information message box."""
        buttons = [
            {'text': 'OK', 'role': 'primary'}
        ]
        
        dialog = CustomMessageBox(parent, title, message, buttons, icon)
        dialog.exec_()
        return dialog.get_result()
    
    @staticmethod
    def warning(parent, title, message, icon="fa6s.exclamation"):
        """Show a warning message box."""
        buttons = [
            {'text': 'OK', 'role': 'primary'}
        ]
        
        dialog = CustomMessageBox(parent, title, message, buttons, icon)
        dialog.exec_()
        return dialog.get_result()
    
    @staticmethod
    def critical(parent, title, message, icon="fa6s.triangle"):
        """Show a critical error message box."""
        buttons = [
            {'text': 'OK', 'role': 'destructive'}
        ]
        
        dialog = CustomMessageBox(parent, title, message, buttons, icon)
        dialog.exec_()
        return dialog.get_result()
    
    @staticmethod
    def question(parent, title, message, default_button="No", icon="fa6s.question"):
        """Show a question message box with Yes/No buttons."""
        if default_button == "Yes":
            buttons = [
                {'text': 'Yes', 'role': 'primary'},
                {'text': 'No', 'role': 'secondary'}
            ]
        else:
            buttons = [
                {'text': 'No', 'role': 'secondary'},
                {'text': 'Yes', 'role': 'primary'}
            ]
        
        dialog = CustomMessageBox(parent, title, message, buttons, icon)
        # Set default result based on default_button
        dialog.default_result = default_button
        dialog.result = default_button  # Initialize with default
        
        result = dialog.exec_()
        
        # If dialog was rejected (cancelled), return the opposite of default
        if result == QDialog.Rejected:
            return default_button == "Yes"
        
        return dialog.get_result() == 'Yes'
    
    @staticmethod
    def confirm_delete(parent, title, message, icon="fa6s.trash"):
        """Show a confirmation dialog for deleting an item."""
        buttons = [
            {'text': 'Delete', 'role': 'destructive'},
            {'text': 'Cancel', 'role': 'secondary'}
        ]
        
        dialog = CustomMessageBox(parent, title, message, buttons, icon)
        dialog.exec_()
        return dialog.get_result() == 'Delete'
    
    @staticmethod
    def test_connection(parent, title, message, icon="fa6s.play"):
        """Show a test connection result message box."""
        buttons = [
            {'text': 'OK', 'role': 'neutral'}
        ]
        
        dialog = CustomMessageBox(parent, title, message, buttons, icon)
        dialog.exec_()
        return dialog.get_result()
    
    @staticmethod
    def success(parent, title, message, icon="fa6s.check"):
        """Show a success message box."""
        buttons = [
            {'text': 'OK', 'role': 'primary'}
        ]
        
        dialog = CustomMessageBox(parent, title, message, buttons, icon)
        dialog.exec_()
        return dialog.get_result()


# Convenience functions for backward compatibility
def show_information(parent, title, message):
    """Show an information message box."""
    return MessageBoxHelper.information(parent, title, message)

def show_warning(parent, title, message):
    """Show a warning message box."""
    return MessageBoxHelper.warning(parent, title, message)

def show_critical(parent, title, message):
    """Show a critical error message box."""
    return MessageBoxHelper.critical(parent, title, message)

def show_question(parent, title, message, default_button="No"):
    """Show a question message box."""
    return MessageBoxHelper.question(parent, title, message, default_button)

def show_confirm_delete(parent, title, message):
    """Show a confirmation dialog for deleting an item."""
    return MessageBoxHelper.confirm_delete(parent, title, message)

def show_test_connection(parent, title, message):
    """Show a test connection result message box."""
    return MessageBoxHelper.test_connection(parent, title, message)

def show_success(parent, title, message):
    """Show a success message box."""
    return MessageBoxHelper.success(parent, title, message)