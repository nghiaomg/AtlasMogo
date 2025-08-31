"""
Dialog Components
Custom dialogs for database operations and other functionality.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QTextEdit, QFormLayout, QMessageBox,
    QDialogButtonBox, QGroupBox, QSpinBox, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon
import qtawesome as fa

from .dialog_helper import DialogHelper
from .styles import BUTTON_STYLES
from .dialog_logger import log_dialog_creation, log_dialog_result


class CreateDatabaseDialog(QDialog):
    """Dialog for creating a new database."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Database")
        self.setModal(True)
        self.setFixedSize(400, 220)
        
        self.database_name = ""
        self.setup_ui()
        
        # Log dialog creation
        log_dialog_creation(self, "CreateDatabaseDialog")
        
    def setup_ui(self):
        """Setup the dialog UI."""
        # Apply consistent dialog styling
        DialogHelper.apply_dialog_style(self)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Title section
        title_layout = DialogHelper.create_title_section(
            "Create New Database",
            "Enter a name for the new database"
        )
        layout.addLayout(title_layout)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Database name input
        self.db_name_edit = QLineEdit()
        self.db_name_edit.setPlaceholderText("Enter database name")
        self.db_name_edit.textChanged.connect(self.validate_input)
        form_layout.addRow("Database Name:", self.db_name_edit)
        
        layout.addLayout(form_layout)
        
        # Info text
        info_label = QLabel("Note: Database will be created with a temporary collection that will be automatically removed.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #6b7280; font-size: 11px; font-style: italic; margin-top: 8px;")
        layout.addWidget(info_label)
        
        # Buttons
        button_layout, button_dict = DialogHelper.create_standard_button_layout(
            self,
            primary_text="Create Database",
            primary_role="ok",
            primary_icon="fa6s.plus",
            secondary_text="Cancel",
            secondary_role="cancel",
            secondary_icon="fa6s.times"
        )
        self.create_btn = button_dict['primary']  # Primary button
        layout.addLayout(button_layout)
        
        # Set focus to database name input
        self.db_name_edit.setFocus()
        
    def validate_input(self):
        """Validate the input fields."""
        db_name = self.db_name_edit.text().strip()
        self.create_btn.setEnabled(len(db_name) > 0 and not db_name.startswith('__'))
        
    def get_database_name(self):
        """Get the entered database name."""
        return self.db_name_edit.text().strip()
    
    def exec_(self):
        """Override exec_ to log dialog result."""
        result = super().exec_()
        log_dialog_result(self, result)
        return result


class CreateCollectionDialog(QDialog):
    """Dialog for creating a new collection."""
    
    def __init__(self, parent=None, database_name=""):
        super().__init__(parent)
        self.setWindowTitle("Create Collection")
        self.setModal(True)
        self.setFixedSize(400, 220)
        
        self.database_name = database_name
        self.collection_name = ""
        self.setup_ui()
        
        # Log dialog creation
        log_dialog_creation(self, "CreateCollectionDialog")
        
    def setup_ui(self):
        """Setup the dialog UI."""
        # Apply consistent dialog styling
        DialogHelper.apply_dialog_style(self)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Title section
        title_layout = DialogHelper.create_title_section(
            "Create New Collection",
            "Enter a name for the new collection"
        )
        layout.addLayout(title_layout)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Database name (read-only if provided)
        if self.database_name:
            db_label = QLabel(self.database_name)
            db_label.setStyleSheet("background-color: #f9fafb; padding: 8px 12px; border: 1px solid #e5e7eb; border-radius: 4px; color: #374151;")
            form_layout.addRow("Database:", db_label)
        else:
            self.db_combo = QComboBox()
            self.db_combo.setEditable(True)
            self.db_combo.setPlaceholderText("Select or enter database name")
            form_layout.addRow("Database:", self.db_combo)
        
        # Collection name input
        self.collection_name_edit = QLineEdit()
        self.collection_name_edit.setPlaceholderText("Enter collection name")
        self.collection_name_edit.textChanged.connect(self.validate_input)
        form_layout.addRow("Collection Name:", self.collection_name_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout, button_dict = DialogHelper.create_standard_button_layout(
            self,
            primary_text="Create Collection",
            primary_role="ok",
            primary_icon="fa6s.folder-plus",
            secondary_text="Cancel",
            secondary_role="cancel",
            secondary_icon="fa6s.times"
        )
        self.create_btn = button_dict['primary']  # Primary button
        layout.addLayout(button_layout)
        
        # Set focus to collection name input
        self.collection_name_edit.setFocus()
        
    def validate_input(self):
        """Validate the input fields."""
        collection_name = self.collection_name_edit.text().strip()
        self.create_btn.setEnabled(len(collection_name) > 0 and not collection_name.startswith('__'))
        
    def get_database_name(self):
        """Get the database name."""
        if self.database_name:
            return self.database_name
        return self.db_combo.currentText().strip()
        
    def get_collection_name(self):
        """Get the entered collection name."""
        return self.collection_name_edit.text().strip()
    
    def exec_(self):
        """Override exec_ to log dialog result."""
        result = super().exec_()
        log_dialog_result(self, result)
        return result


class ConfirmationDialog(QDialog):
    """Generic confirmation dialog with consistent styling."""
    
    def __init__(self, parent=None, title="Confirm Action", message="Are you sure you want to proceed?",
                 confirm_text="Yes", cancel_text="No", is_destructive=False):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 200)
        
        self.title = title
        self.message = message
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        self.is_destructive = is_destructive
        
        self.setup_ui()
        
        # Log dialog creation
        log_dialog_creation(self, "ConfirmationDialog")
        
    def setup_ui(self):
        """Setup the dialog UI."""
        # Apply consistent dialog styling
        DialogHelper.apply_dialog_style(self)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Title section with warning if destructive
        warning_text = "This action cannot be undone." if self.is_destructive else ""
        title_layout = DialogHelper.create_title_section(
            self.title,
            self.message,
            warning_text
        )
        layout.addLayout(title_layout)
        
        # Buttons
        if self.is_destructive:
            button_layout, button_dict = DialogHelper.create_standard_button_layout(
                self,
                primary_text=self.confirm_text,
                primary_role="destructive",
                primary_icon="fa6s.trash",
                secondary_text=self.cancel_text,
                secondary_role="cancel",
                secondary_icon="fa6s.times"
            )
        else:
            button_layout, button_dict = DialogHelper.create_standard_button_layout(
                self,
                primary_text=self.confirm_text,
                primary_role="yes",
                primary_icon="fa6s.check",
                secondary_text=self.cancel_text,
                secondary_role="no",
                secondary_icon="fa6s.times"
            )
        
        layout.addLayout(button_layout)
    
    def exec_(self):
        """Override exec_ to log dialog result."""
        result = super().exec_()
        log_dialog_result(self, result)
        return result
        
    @staticmethod
    def confirm_delete(parent, item_name, item_type="item"):
        """Show a confirmation dialog for deleting an item."""
        dialog = ConfirmationDialog(
            parent=parent,
            title=f"Delete {item_type.title()}",
            message=f"Are you sure you want to delete '{item_name}'?",
            confirm_text="Delete",
            cancel_text="Cancel",
            is_destructive=True
        )
        result = dialog.exec_()
        return result == QDialog.Accepted
    
    @staticmethod
    def confirm_drop(parent, item_name, item_type="item"):
        """Show a confirmation dialog for dropping an item."""
        dialog = ConfirmationDialog(
            parent=parent,
            title=f"Drop {item_type.title()}",
            message=f"Are you sure you want to drop '{item_name}'? This will permanently remove all data.",
            confirm_text="Drop",
            cancel_text="Cancel",
            is_destructive=True
        )
        result = dialog.exec_()
        return result == QDialog.Accepted


class RenameDialog(QDialog):
    """Generic rename dialog with consistent styling."""
    
    def __init__(self, parent=None, title="Rename", current_name="", item_type="item"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 200)
        
        self.current_name = current_name
        self.item_type = item_type
        self.setup_ui()
        
        # Log dialog creation
        log_dialog_creation(self, "RenameDialog")
        
    def setup_ui(self):
        """Setup the dialog UI."""
        # Apply consistent dialog styling
        DialogHelper.apply_dialog_style(self)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Title section
        title_layout = DialogHelper.create_title_section(
            f"Rename {self.item_type.title()}",
            f"Enter a new name for '{self.current_name}'"
        )
        layout.addLayout(title_layout)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Name input
        self.name_edit = QLineEdit()
        self.name_edit.setText(self.current_name)
        self.name_edit.setPlaceholderText(f"Enter new {self.item_type} name")
        self.name_edit.textChanged.connect(self.validate_input)
        self.name_edit.selectAll()  # Select all text for easy editing
        form_layout.addRow(f"New {self.item_type.title()} Name:", self.name_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout, button_dict = DialogHelper.create_standard_button_layout(
            self,
            primary_text="Rename",
            primary_role="ok",
            primary_icon="fa6s.pen",
            secondary_text="Cancel",
            secondary_role="cancel",
            secondary_icon="fa6s.times"
        )
        self.rename_btn = button_dict['primary']  # Primary button
        layout.addLayout(button_layout)
        
        # Set focus to name input
        self.name_edit.setFocus()
        
    def validate_input(self):
        """Validate the input fields."""
        new_name = self.name_edit.text().strip()
        is_valid = len(new_name) > 0 and new_name != self.current_name and not new_name.startswith('__')
        self.rename_btn.setEnabled(is_valid)
        
    def get_new_name(self):
        """Get the new name entered by the user."""
        return self.name_edit.text().strip()
    
    def exec_(self):
        """Override exec_ to log dialog result."""
        result = super().exec_()
        log_dialog_result(self, result)
        return result


class InsertDocumentDialog(QDialog):
    """Dialog for inserting a new document."""
    
    def __init__(self, parent=None, database_name="", collection_name=""):
        super().__init__(parent)
        self.setWindowTitle("Insert Document")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        self.database_name = database_name
        self.collection_name = collection_name
        self.document_json = ""
        self.setup_ui()
        
        # Log dialog creation
        log_dialog_creation(self, "InsertDocumentDialog")
        
    def setup_ui(self):
        """Setup the dialog UI."""
        # Apply consistent dialog styling
        DialogHelper.apply_dialog_style(self)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Title section
        title_layout = DialogHelper.create_title_section(
            "Insert New Document",
            "Enter JSON document to insert"
        )
        layout.addLayout(title_layout)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Database and collection info
        if self.database_name:
            db_label = QLabel(self.database_name)
            db_label.setStyleSheet("background-color: #f9fafb; padding: 8px 12px; border: 1px solid #e5e7eb; border-radius: 4px; color: #374151;")
            form_layout.addRow("Database:", db_label)
            
        if self.collection_name:
            coll_label = QLabel(self.collection_name)
            coll_label.setStyleSheet("background-color: #f9fafb; padding: 8px 12px; border: 1px solid #e5e7eb; border-radius: 4px; color: #374151;")
            form_layout.addRow("Collection:", coll_label)
        
        layout.addLayout(form_layout)
        
        # Document JSON input
        doc_label = QLabel("Document (JSON format):")
        doc_label.setStyleSheet("font-weight: 500; margin-top: 8px;")
        layout.addWidget(doc_label)
        
        self.document_edit = QTextEdit()
        self.document_edit.setPlaceholderText('{"name": "John Doe", "age": 30, "email": "john@example.com"}')
        self.document_edit.textChanged.connect(self.validate_input)
        self.document_edit.setMinimumHeight(120)
        layout.addWidget(self.document_edit)
        
        # Example button
        example_btn = QPushButton("Insert Example")
        example_btn.setStyleSheet(BUTTON_STYLES['dialog_secondary'])
        example_btn.clicked.connect(self.insert_example)
        layout.addWidget(example_btn)
        
        # Buttons
        button_layout, button_dict = DialogHelper.create_standard_button_layout(
            self,
            primary_text="Insert Document",
            primary_role="ok",
            primary_icon="fa6s.plus",
            secondary_text="Cancel",
            secondary_role="cancel",
            secondary_icon="fa6s.times"
        )
        self.insert_btn = button_dict['primary']  # Primary button
        layout.addLayout(button_layout)
        
    def validate_input(self):
        """Validate the JSON input."""
        try:
            import json
            text = self.document_edit.toPlainText().strip()
            if text:
                json.loads(text)
                self.insert_btn.setEnabled(True)
            else:
                self.insert_btn.setEnabled(False)
        except json.JSONDecodeError:
            self.insert_btn.setEnabled(False)
            
    def insert_example(self):
        """Insert an example document."""
        example = '''{
  "name": "John Doe",
  "age": 30,
  "email": "john@example.com",
  "city": "New York",
  "active": true
}'''
        self.document_edit.setPlainText(example)
        
    def get_document_json(self):
        """Get the document JSON string."""
        return self.document_edit.toPlainText().strip()
    
    def exec_(self):
        """Override exec_ to log dialog result."""
        result = super().exec_()
        log_dialog_result(self, result)
        return result


class QueryBuilderDialog(QDialog):
    """Dialog for building and executing MongoDB queries."""
    
    def __init__(self, parent=None, database_name="", collection_name=""):
        super().__init__(parent)
        self.setWindowTitle("Query Builder")
        self.setModal(True)
        self.setFixedSize(600, 500)
        
        self.database_name = database_name
        self.collection_name = collection_name
        self.query_json = ""
        self.limit = 100
        self.setup_ui()
        
        # Log dialog creation
        log_dialog_creation(self, "QueryBuilderDialog")
        
    def setup_ui(self):
        """Setup the dialog UI."""
        # Apply consistent dialog styling
        DialogHelper.apply_dialog_style(self)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Title section
        title_layout = DialogHelper.create_title_section(
            "MongoDB Query Builder",
            "Build and execute custom queries"
        )
        layout.addLayout(title_layout)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Database and collection info
        if self.database_name:
            db_label = QLabel(self.database_name)
            db_label.setStyleSheet("background-color: #f9fafb; padding: 8px 12px; border: 1px solid #e5e7eb; border-radius: 4px; color: #374151;")
            form_layout.addRow("Database:", db_label)
            
        if self.collection_name:
            coll_label = QLabel(self.collection_name)
            coll_label.setStyleSheet("background-color: #f9fafb; padding: 8px 12px; border: 1px solid #e5e7eb; border-radius: 4px; color: #374151;")
            form_layout.addRow("Collection:", coll_label)
        
        layout.addLayout(form_layout)
        
        # Query input
        query_label = QLabel("Query Filter (JSON format):")
        query_label.setStyleSheet("font-weight: 500; margin-top: 8px;")
        layout.addWidget(query_label)
        
        self.query_edit = QTextEdit()
        self.query_edit.setPlaceholderText('{"age": {"$gte": 25}, "city": "New York"}')
        self.query_edit.textChanged.connect(self.validate_input)
        self.query_edit.setMinimumHeight(100)
        layout.addWidget(self.query_edit)
        
        # Limit input
        limit_layout = QHBoxLayout()
        limit_layout.addWidget(QLabel("Limit:"))
        self.limit_spin = QSpinBox()
        self.limit_spin.setRange(1, 10000)
        self.limit_spin.setValue(100)
        self.limit_spin.valueChanged.connect(lambda v: setattr(self, 'limit', v))
        limit_layout.addWidget(self.limit_spin)
        limit_layout.addStretch()
        layout.addLayout(limit_layout)
        
        # Example buttons
        example_layout = QHBoxLayout()
        example_layout.setSpacing(8)
        
        example1_btn = QPushButton("Age >= 25")
        example1_btn.setStyleSheet(BUTTON_STYLES['dialog_secondary'])
        example1_btn.clicked.connect(lambda: self.insert_example('{"age": {"$gte": 25}}'))
        
        example2_btn = QPushButton("Name starts with 'J'")
        example2_btn.setStyleSheet(BUTTON_STYLES['dialog_secondary'])
        example2_btn.clicked.connect(lambda: self.insert_example('{"name": {"$regex": "^J"}}'))
        
        example3_btn = QPushButton("Active users")
        example3_btn.setStyleSheet(BUTTON_STYLES['dialog_secondary'])
        example3_btn.clicked.connect(lambda: self.insert_example('{"active": true}'))
        
        example_layout.addWidget(example1_btn)
        example_layout.addWidget(example2_btn)
        example_layout.addWidget(example3_btn)
        example_layout.addStretch()
        layout.addLayout(example_layout)
        
        # Buttons
        button_layout, button_dict = DialogHelper.create_standard_button_layout(
            self,
            primary_text="Execute Query",
            primary_role="ok",
            primary_icon="fa6s.magnifying-glass",
            secondary_text="Cancel",
            secondary_role="cancel",
            secondary_icon="fa6s.times"
        )
        self.execute_btn = button_dict['primary']  # Primary button
        layout.addLayout(button_layout)
        
    def validate_input(self):
        """Validate the JSON input."""
        try:
            import json
            text = self.query_edit.toPlainText().strip()
            if text:
                json.loads(text)
                self.execute_btn.setEnabled(True)
            else:
                self.execute_btn.setEnabled(True)  # Empty query is valid
        except json.JSONDecodeError:
            self.execute_btn.setEnabled(False)
            
    def insert_example(self, example):
        """Insert an example query."""
        self.query_edit.setPlainText(example)
        
    def get_query_json(self):
        """Get the query JSON string."""
        text = self.query_edit.toPlainText().strip()
        return text if text else "{}"
        
    def get_limit(self):
        """Get the limit value."""
        return self.limit_spin.value()
    
    def exec_(self):
        """Override exec_ to log dialog result."""
        result = super().exec_()
        log_dialog_result(self, result)
        return result


class SettingsDialog(QDialog):
    """Dialog for application settings."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        self.setup_ui()
        
        # Log dialog creation
        log_dialog_creation(self, "SettingsDialog")
        
    def setup_ui(self):
        """Setup the dialog UI."""
        # Apply consistent dialog styling
        DialogHelper.apply_dialog_style(self)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Title section
        title_layout = DialogHelper.create_title_section(
            "Application Settings",
            "Configure AtlasMogo preferences"
        )
        layout.addLayout(title_layout)
        
        # MongoDB Settings Group
        mongo_group = QGroupBox("MongoDB Settings")
        mongo_layout = QFormLayout()
        mongo_layout.setSpacing(12)
        
        self.default_uri_edit = QLineEdit()
        self.default_uri_edit.setPlaceholderText("mongodb://localhost:27017")
        mongo_layout.addRow("Default Connection URI:", self.default_uri_edit)
        
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1000, 30000)
        self.timeout_spin.setValue(5000)
        self.timeout_spin.setSuffix(" ms")
        mongo_layout.addRow("Connection Timeout:", self.timeout_spin)
        
        mongo_group.setLayout(mongo_layout)
        layout.addWidget(mongo_group)
        
        # UI Settings Group
        ui_group = QGroupBox("UI Settings")
        ui_layout = QFormLayout()
        ui_layout.setSpacing(12)
        
        self.auto_refresh_check = QCheckBox()
        self.auto_refresh_check.setChecked(True)
        ui_layout.addRow("Auto-refresh after operations:", self.auto_refresh_check)
        
        self.confirm_delete_check = QCheckBox()
        self.confirm_delete_check.setChecked(True)
        ui_layout.addRow("Confirm before delete:", self.confirm_delete_check)
        
        ui_group.setLayout(ui_layout)
        layout.addWidget(ui_group)
        
        # Buttons
        button_layout, button_dict = DialogHelper.create_standard_button_layout(
            self,
            primary_text="Save Settings",
            primary_role="ok",
            primary_icon="fa6s.save",
            secondary_text="Cancel",
            secondary_role="cancel",
            secondary_icon="fa6s.times"
        )
        layout.addLayout(button_layout)
        
    def get_settings(self):
        """Get the current settings."""
        return {
            'default_uri': self.default_uri_edit.text().strip(),
            'timeout': self.timeout_spin.value(),
            'auto_refresh': self.auto_refresh_check.isChecked(),
            'confirm_delete': self.confirm_delete_check.isChecked()
        }
    
    def exec_(self):
        """Override exec_ to log dialog result."""
        result = super().exec_()
        log_dialog_result(self, result)
        return result


class ExportDataDialog(QDialog):
    """Dialog for exporting data."""
    
    def __init__(self, parent=None, database_name="", collection_name=""):
        super().__init__(parent)
        self.setWindowTitle("Export Data")
        self.setModal(True)
        self.setFixedSize(500, 300)
        
        self.database_name = database_name
        self.collection_name = collection_name
        self.export_format = "json"
        self.export_path = ""
        self.setup_ui()
        
        # Log dialog creation
        log_dialog_creation(self, "ExportDataDialog")
        
    def setup_ui(self):
        """Setup the dialog UI."""
        # Apply consistent dialog styling
        DialogHelper.apply_dialog_style(self)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Title section
        title_layout = DialogHelper.create_title_section(
            "Export Data",
            "Export collection data to file"
        )
        layout.addLayout(title_layout)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Database and collection info
        if self.database_name:
            db_label = QLabel(self.database_name)
            db_label.setStyleSheet("background-color: #f9fafb; padding: 8px 12px; border: 1px solid #e5e7eb; border-radius: 4px; color: #374151;")
            form_layout.addRow("Database:", db_label)
            
        if self.collection_name:
            coll_label = QLabel(self.collection_name)
            coll_label.setStyleSheet("background-color: #f9fafb; padding: 8px 12px; border: 1px solid #e5e7eb; border-radius: 4px; color: #374151;")
            form_layout.addRow("Collection:", coll_label)
        
        # Export format
        self.format_combo = QComboBox()
        self.format_combo.addItems(["JSON", "CSV", "XML"])
        self.format_combo.currentTextChanged.connect(lambda t: setattr(self, 'export_format', t.lower()))
        form_layout.addRow("Export Format:", self.format_combo)
        
        # Export path
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Enter export file path")
        form_layout.addRow("Export Path:", self.path_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout, button_dict = DialogHelper.create_standard_button_layout(
            self,
            primary_text="Export Data",
            primary_role="ok",
            primary_icon="fa6s.download",
            secondary_text="Cancel",
            secondary_role="cancel",
            secondary_icon="fa6s.times"
        )
        self.export_btn = button_dict['primary']  # Primary button
        layout.addLayout(button_layout)
        
    def get_export_info(self):
        """Get the export information."""
        return {
            'format': self.export_format,
            'path': self.path_edit.text().strip()
        }
    
    def exec_(self):
        """Override exec_ to log dialog result."""
        result = super().exec_()
        log_dialog_result(self, result)
        return result
