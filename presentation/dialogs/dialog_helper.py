"""
Dialog Helper Module
Provides consistent button styling and layout for all dialogs in AtlasMogo.
"""

from PySide6.QtWidgets import QHBoxLayout, QPushButton, QLabel, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import qtawesome as fa

from ..styles.styles import BUTTON_STYLES, DIALOG_STYLE, COLORS
from .dialog_logger import bind_button, log_dialog_creation


class DialogHelper:
    """Helper class for creating consistent dialogs with proper button styling."""
    
    @staticmethod
    def create_button_layout(primary_text="", primary_icon="", primary_action=None,
                           destructive_text="", destructive_icon="", destructive_action=None,
                           secondary_text="Cancel", secondary_icon="fa6s.xmark", secondary_action=None,
                           show_primary=True, show_destructive=False, show_secondary=True):
        """
        Create a consistent button layout for dialogs.
        
        Args:
            primary_text: Text for primary action button (e.g., "OK", "Yes", "Create")
            primary_icon: Icon for primary action button
            primary_action: Function to call when primary button is clicked
            destructive_text: Text for destructive action button (e.g., "Delete", "Drop")
            destructive_icon: Icon for destructive action button
            destructive_action: Function to call when destructive button is clicked
            secondary_text: Text for secondary action button (e.g., "Cancel", "No")
            secondary_icon: Icon for secondary action button
            secondary_action: Function to call when secondary button is clicked
            show_primary: Whether to show the primary button
            show_destructive: Whether to show the destructive button
            show_secondary: Whether to show the secondary button
            
        Returns:
            tuple: (button_layout, button_dict) where button_dict contains named buttons
        """
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.setContentsMargins(0, 16, 0, 0)
        
        # Add stretch to push buttons to the right
        button_layout.addStretch()
        
        # Create buttons based on parameters
        buttons = []
        button_dict = {}
        
        # Primary button (leftmost)
        if show_primary and primary_text:
            primary_btn = QPushButton(primary_text)
            primary_btn.setStyleSheet(BUTTON_STYLES['dialog_primary'])
            if primary_icon:
                primary_btn.setIcon(fa.icon(primary_icon))
            if primary_action:
                primary_btn.clicked.connect(primary_action)
            # Set as default button for Enter key support
            primary_btn.setDefault(True)
            primary_btn.setAutoDefault(True)
            buttons.append(primary_btn)
            button_dict['primary'] = primary_btn
        
        # Destructive button (middle)
        if show_destructive and destructive_text:
            destructive_btn = QPushButton(destructive_text)
            destructive_btn.setStyleSheet(BUTTON_STYLES['dialog_destructive'])
            if destructive_icon:
                destructive_btn.setIcon(fa.icon(destructive_icon))
            if destructive_action:
                destructive_btn.clicked.connect(destructive_action)
            buttons.append(destructive_btn)
            button_dict['destructive'] = destructive_btn
        
        # Secondary button (rightmost)
        if show_secondary and secondary_text:
            secondary_btn = QPushButton(secondary_text)
            secondary_btn.setStyleSheet(BUTTON_STYLES['dialog_secondary'])
            if secondary_icon:
                secondary_btn.setIcon(fa.icon(secondary_icon))
            if secondary_action:
                secondary_btn.clicked.connect(secondary_action)
            buttons.append(secondary_btn)
            button_dict['secondary'] = secondary_btn
        
        # Add buttons to layout (in reverse order for proper positioning)
        for button in reversed(buttons):
            button_layout.addWidget(button)
        
        return button_layout, button_dict
    
    @staticmethod
    def create_title_section(title, subtitle="", warning_text=""):
        """
        Create a consistent title section for dialogs.
        
        Args:
            title: Main dialog title
            subtitle: Optional subtitle
            warning_text: Optional warning text (for destructive actions)
            
        Returns:
            QVBoxLayout: Layout containing the title section
        """
        title_layout = QVBoxLayout()
        title_layout.setSpacing(8)
        title_layout.setContentsMargins(0, 0, 0, 16)
        
        # Main title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {COLORS['text_primary']}; margin-bottom: 8px;")
        title_layout.addWidget(title_label)
        
        # Subtitle (if provided)
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setFont(QFont("Arial", 12))
            subtitle_label.setAlignment(Qt.AlignCenter)
            subtitle_label.setStyleSheet(f"color: {COLORS['text_secondary']}; margin-bottom: 4px;")
            subtitle_label.setWordWrap(True)
            title_layout.addWidget(subtitle_label)
        
        # Warning text (if provided)
        if warning_text:
            warning_label = QLabel(warning_text)
            warning_label.setFont(QFont("Arial", 11))
            warning_label.setAlignment(Qt.AlignCenter)
            warning_label.setStyleSheet(f"color: {COLORS['danger']}; font-weight: 500; margin-bottom: 8px;")
            warning_label.setWordWrap(True)
            title_layout.addWidget(warning_label)
        
        return title_layout
    
    @staticmethod
    def apply_dialog_style(dialog):
        """Apply consistent styling to a dialog."""
        dialog.setStyleSheet(DIALOG_STYLE)
    
    @staticmethod
    def create_standard_buttons(dialog, primary_text="OK", primary_action=None,
                              secondary_text="Cancel", secondary_action=None):
        """
        Create standard OK/Cancel buttons for simple dialogs.
        
        Args:
            dialog: The dialog widget
            primary_text: Text for primary button
            primary_action: Action for primary button
            secondary_text: Text for secondary button
            secondary_action: Action for secondary button
            
        Returns:
            tuple: (button_layout, button_dict)
        """
        if primary_action is None:
            primary_action = dialog.accept
        if secondary_action is None:
            secondary_action = dialog.reject
            
        return DialogHelper.create_button_layout(
            primary_text=primary_text,
            primary_icon="fa6s.check",
            primary_action=primary_action,
            secondary_text=secondary_text,
            secondary_icon="fa6s.xmark",
            secondary_action=secondary_action
        )
    
    @staticmethod
    def create_confirm_buttons(dialog, confirm_text="Yes", confirm_action=None,
                             cancel_text="No", cancel_action=None):
        """
        Create standard Yes/No buttons for confirmation dialogs.
        
        Args:
            dialog: The dialog widget
            confirm_text: Text for confirm button
            confirm_action: Action for confirm button
            cancel_text: Text for cancel button
            cancel_action: Action for cancel button
            
        Returns:
            tuple: (button_layout, button_dict)
        """
        if confirm_action is None:
            confirm_action = dialog.accept
        if cancel_action is None:
            cancel_action = dialog.reject
            
        return DialogHelper.create_button_layout(
            primary_text=confirm_text,
            primary_icon="fa6s.check-circle",
            primary_action=confirm_action,
            secondary_text=cancel_text,
            secondary_icon="fa6s.xmark",
            secondary_action=cancel_action
        )
    
    @staticmethod
    def create_destructive_buttons(dialog, destructive_text="Delete", destructive_action=None,
                                 cancel_text="Cancel", cancel_action=None):
        """
        Create buttons for destructive actions (Delete/Cancel).
        
        Args:
            dialog: The dialog widget
            destructive_text: Text for destructive button
            destructive_action: Action for destructive button
            cancel_text: Text for cancel button
            cancel_action: Action for cancel button
            
        Returns:
            tuple: (button_layout, button_dict)
        """
        if cancel_action is None:
            cancel_action = dialog.reject
            
        return DialogHelper.create_button_layout(
            destructive_text=destructive_text,
            destructive_icon="fa6s.trash",
            destructive_action=destructive_action,
            secondary_text=cancel_text,
            secondary_icon="fa6s.xmark",
            secondary_action=cancel_action,
            show_primary=False,
            show_destructive=True
        )
    
    @staticmethod
    def create_button_with_role(label, role, parent_dialog, icon=None):
        """
        Create a button with proper role-based action binding and logging.
        
        Args:
            label: Button text
            role: Button role ("ok", "cancel", "yes", "no", "destructive")
            parent_dialog: The parent dialog widget
            icon: Optional icon name
            
        Returns:
            QPushButton: Configured button with proper action binding and logging
        """
        btn = QPushButton(label)
        
        # Apply role-based styling
        if role == "ok" or role == "yes":
            btn.setStyleSheet(BUTTON_STYLES['dialog_primary'])
            btn.setDefault(True)
            btn.setAutoDefault(True)
        elif role == "cancel" or role == "no":
            btn.setStyleSheet(BUTTON_STYLES['dialog_secondary'])
            btn.setAutoDefault(False)
        elif role == "destructive":
            btn.setStyleSheet(BUTTON_STYLES['dialog_destructive'])
            btn.setDefault(True)
            btn.setAutoDefault(True)
        
        # Set icon if provided
        if icon:
            btn.setIcon(fa.icon(icon))
        
        # Bind button with logging
        bind_button(btn, None, parent_dialog, role)
        
        return btn
    
    @staticmethod
    def create_standard_button_layout(parent_dialog, primary_text="OK", primary_role="ok", primary_icon=None,
                                    secondary_text="Cancel", secondary_role="cancel", secondary_icon="fa6s.xmark"):
        """
        Create a standard button layout with proper action binding.
        
        Args:
            parent_dialog: The parent dialog widget
            primary_text: Text for primary button
            primary_role: Role for primary button ("ok", "yes", "destructive")
            primary_icon: Icon for primary button
            secondary_text: Text for secondary button
            secondary_role: Role for secondary button ("cancel", "no")
            secondary_icon: Icon for secondary button
            
        Returns:
            tuple: (button_layout, button_dict)
        """
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.setContentsMargins(0, 16, 0, 0)
        
        # Add stretch to push buttons to the right
        button_layout.addStretch()
        
        # Create buttons with proper role binding
        primary_btn = DialogHelper.create_button_with_role(
            primary_text, primary_role, parent_dialog, primary_icon
        )
        
        secondary_btn = DialogHelper.create_button_with_role(
            secondary_text, secondary_role, parent_dialog, secondary_icon
        )
        
        # Add buttons to layout (secondary first, then primary for proper positioning)
        button_layout.addWidget(secondary_btn)
        button_layout.addWidget(primary_btn)
        
        button_dict = {
            'primary': primary_btn,
            'secondary': secondary_btn
        }
        
        return button_layout, button_dict



