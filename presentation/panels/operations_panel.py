"""
Operations Panel Component
Handles CRUD operations (Create, Read, Update, Delete) for MongoDB documents.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QTextEdit, QLineEdit, QPushButton, QScrollArea, QSizePolicy
)
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import Qt
import qtawesome as fa


class OperationsPanel(QObject):
    """Operations panel component for CRUD operations."""
    
    # Signals
    insert_requested = Signal(str)  # Emits document data
    update_requested = Signal(str, str)  # Emits filter, update data
    delete_requested = Signal(str)  # Emits filter
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.widget = None
        self.insert_text = None
        self.update_filter = None
        self.update_data = None
        self.delete_filter = None
        self._create_operations_panel()
    
    def _create_operations_panel(self):
        """Create the operations panel widget."""
        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)
        layout.setSpacing(12)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Create scroll area for operations content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create content widget for scroll area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(12)
        content_layout.setContentsMargins(8, 8, 8, 8)
        
        # Insert document section
        self._create_insert_section(content_layout)
        
        # Update document section
        self._create_update_section(content_layout)
        
        # Delete document section
        self._create_delete_section(content_layout)
        
        # Set content widget for scroll area
        scroll_area.setWidget(content_widget)
        
        # Add scroll area to main layout
        layout.addWidget(scroll_area)
        
        # Set size policies
        self.widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    def _create_insert_section(self, parent_layout):
        """Create the insert document section."""
        insert_group = QGroupBox("Insert Document")
        insert_layout = QVBoxLayout(insert_group)
        insert_layout.setSpacing(8)
        
        self.insert_text = QTextEdit()
        self.insert_text.setPlaceholderText('{"name": "example", "value": 123}')
        self.insert_text.setMinimumHeight(80)
        self.insert_text.setMaximumHeight(120)
        self.insert_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        insert_layout.addWidget(self.insert_text)
        
        insert_button = QPushButton(fa.icon('fa6s.plus'), "Insert Document")
        insert_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        insert_button.setMinimumHeight(28)
        insert_button.setMinimumWidth(120)
        insert_button.clicked.connect(self._on_insert_clicked)
        insert_layout.addWidget(insert_button)
        
        parent_layout.addWidget(insert_group)
    
    def _create_update_section(self, parent_layout):
        """Create the update document section."""
        update_group = QGroupBox("Update Document")
        update_layout = QFormLayout(update_group)
        update_layout.setSpacing(8)
        
        self.update_filter = QLineEdit()
        self.update_filter.setPlaceholderText('{"_id": "document_id"}')
        self.update_filter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.update_filter.setMinimumHeight(28)
        update_layout.addRow("Filter:", self.update_filter)
        
        self.update_data = QTextEdit()
        self.update_data.setPlaceholderText('{"name": "updated_name"}')
        self.update_data.setMinimumHeight(60)
        self.update_data.setMaximumHeight(100)
        self.update_data.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        update_layout.addRow("Update Data:", self.update_data)
        
        update_button = QPushButton(fa.icon('fa6s.pen'), "Update Document")
        update_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        update_button.setMinimumHeight(28)
        update_button.setMinimumWidth(120)
        update_button.clicked.connect(self._on_update_clicked)
        update_layout.addRow("", update_button)
        
        parent_layout.addWidget(update_group)
    
    def _create_delete_section(self, parent_layout):
        """Create the delete document section."""
        delete_group = QGroupBox("Delete Document")
        delete_layout = QFormLayout(delete_group)
        delete_layout.setSpacing(8)
        
        self.delete_filter = QLineEdit()
        self.delete_filter.setPlaceholderText('{"_id": "document_id"}')
        self.delete_filter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.delete_filter.setMinimumHeight(28)
        delete_layout.addRow("Filter:", self.delete_filter)
        
        delete_button = QPushButton(fa.icon('fa6s.trash'), "Delete Document")
        delete_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        delete_button.setMinimumHeight(28)
        delete_button.setMinimumWidth(120)
        delete_button.clicked.connect(self._on_delete_clicked)
        delete_layout.addRow("", delete_button)
        
        parent_layout.addWidget(delete_group)
    
    def _on_insert_clicked(self):
        """Handle insert button click."""
        document_text = self.insert_text.toPlainText().strip()
        if document_text:
            self.insert_requested.emit(document_text)
    
    def _on_update_clicked(self):
        """Handle update button click."""
        filter_text = self.update_filter.text().strip()
        update_text = self.update_data.toPlainText().strip()
        
        if filter_text and update_text:
            self.update_requested.emit(filter_text, update_text)
    
    def _on_delete_clicked(self):
        """Handle delete button click."""
        filter_text = self.delete_filter.text().strip()
        if filter_text:
            self.delete_requested.emit(filter_text)
    
    def get_widget(self):
        """Get the operations panel widget."""
        return self.widget
    
    def clear_insert_form(self):
        """Clear the insert document form."""
        if self.insert_text:
            self.insert_text.clear()
    
    def clear_update_form(self):
        """Clear the update document form."""
        if self.update_filter:
            self.update_filter.clear()
        if self.update_data:
            self.update_data.clear()
    
    def clear_delete_form(self):
        """Clear the delete document form."""
        if self.delete_filter:
            self.delete_filter.clear()
    
    def clear_all_forms(self):
        """Clear all operation forms."""
        self.clear_insert_form()
        self.clear_update_form()
        self.clear_delete_form()
    
    def set_insert_placeholder(self, text: str):
        """Set the placeholder text for insert form."""
        if self.insert_text:
            self.insert_text.setPlaceholderText(text)
    
    def set_update_filter_placeholder(self, text: str):
        """Set the placeholder text for update filter."""
        if self.update_filter:
            self.update_filter.setPlaceholderText(text)
    
    def set_update_data_placeholder(self, text: str):
        """Set the placeholder text for update data."""
        if self.update_data:
            self.update_data.setPlaceholderText(text)
    
    def set_delete_filter_placeholder(self, text: str):
        """Set the placeholder text for delete filter."""
        if self.delete_filter:
            self.delete_filter.setPlaceholderText(text)
    
    def enable_operations(self, enabled: bool = True):
        """Enable or disable all operation forms."""
        if self.insert_text:
            self.insert_text.setEnabled(enabled)
        if self.update_filter:
            self.update_filter.setEnabled(enabled)
        if self.update_data:
            self.update_data.setEnabled(enabled)
        if self.delete_filter:
            self.delete_filter.setEnabled(enabled)
