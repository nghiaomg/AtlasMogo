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
from ..styles.styles import BUTTON_STYLES
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
        
        # Info text - Updated to reflect the actual implementation
        info_label = QLabel("Note: Database will be created with an initialization collection to ensure visibility.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #6b7280; font-size: 11px; font-style: italic; margin-top: 8px;")
        layout.addWidget(info_label)
        
        # Buttons - Use create_standard_buttons for proper accept/reject binding
        button_layout, button_dict = DialogHelper.create_standard_buttons(
            self,
            primary_text="Create Database",
            primary_action=self.accept_dialog,
            secondary_text="Cancel"
        )
        self.create_btn = button_dict['primary']  # Primary button (blue full background)
        self.cancel_btn = button_dict['secondary']  # Secondary button (outlined)
        layout.addLayout(button_layout)
        
        # Set focus to database name input
        self.db_name_edit.setFocus()
        
        # Initial validation
        self.validate_input()
        
    def validate_input(self):
        """Validate the input fields."""
        db_name = self.db_name_edit.text().strip()
        is_valid = len(db_name) > 0 and not db_name.startswith('__')
        self.create_btn.setEnabled(is_valid)
        
        # Log validation result
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Database name validation: '{db_name}' -> Valid: {is_valid}")
        
    def accept_dialog(self):
        """Handle dialog acceptance with validation."""
        db_name = self.db_name_edit.text().strip()
        
        # Final validation before accepting
        if not db_name:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Validation Error", "Please enter a database name.")
            return
            
        if db_name.startswith('__'):
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Validation Error", "Database names cannot start with '__'.")
            return
        
        # Store the validated name and accept
        self.database_name = db_name
        
        # Log successful acceptance
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[DIALOG: Create Database] → Confirmed with database: {db_name}")
        
        self.accept()
        
    def get_database_name(self):
        """Get the entered database name."""
        return self.database_name
    
    def exec_(self):
        """Override exec_ to log dialog result."""
        result = super().exec_()
        
        # Log the result
        if result == QDialog.Accepted:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"[DIALOG: Create Database] → Accepted with database: '{self.database_name}'")
        else:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"[DIALOG: Create Database] → Cancelled by user")
        
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
            secondary_icon="fa6s.xmark"
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
                secondary_icon="fa6s.xmark"
            )
        else:
            button_layout, button_dict = DialogHelper.create_standard_button_layout(
                self,
                primary_text=self.confirm_text,
                primary_role="yes",
                primary_icon="fa6s.check",
                secondary_text=self.cancel_text,
                secondary_role="no",
                secondary_icon="fa6s.xmark"
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
            secondary_icon="fa6s.xmark"
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
            secondary_icon="fa6s.xmark"
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
            primary_icon="fa6s.check",
            secondary_text="Cancel",
            secondary_role="cancel",
            secondary_icon="fa6s.xmark"
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
            secondary_icon="fa6s.xmark"
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


class DocumentViewerDialog(QDialog):
    """Dialog for viewing a document in a formatted way."""
    
    def __init__(self, document: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("View Document")
        self.setModal(True)
        self.setFixedSize(600, 500)
        
        self.document = document
        self.setup_ui()
        
        # Log dialog creation
        log_dialog_creation(self, "DocumentViewerDialog")
        
    def setup_ui(self):
        """Setup the dialog UI."""
        # Apply consistent dialog styling
        DialogHelper.apply_dialog_style(self)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Title section
        title_layout = DialogHelper.create_title_section(
            "View Document",
            "Document details and content"
        )
        layout.addLayout(title_layout)
        
        # Document ID info
        doc_id = self.document.get("_id", "No ID")
        id_label = QLabel(f"Document ID: {doc_id}")
        id_label.setStyleSheet("color: #6b7280; font-size: 12px; margin-bottom: 8px;")
        layout.addWidget(id_label)
        
        # Document content
        content_group = QGroupBox("Document Content")
        content_layout = QVBoxLayout(content_group)
        
        self.document_text = QTextEdit()
        self.document_text.setReadOnly(True)
        self.document_text.setFont(QFont("Consolas", 10))
        
        # Format and display the document
        import json
        try:
            formatted_json = json.dumps(self.document, indent=2, default=str)
            self.document_text.setPlainText(formatted_json)
        except Exception as e:
            self.document_text.setPlainText(f"Error formatting document: {str(e)}\n\nRaw document: {str(self.document)}")
        
        content_layout.addWidget(self.document_text)
        layout.addWidget(content_group)
        
        # Buttons
        button_layout, button_dict = DialogHelper.create_standard_button_layout(
            self,
            primary_text="Close",
            primary_role="ok",
            primary_icon="fa6s.xmark",
            secondary_text="",
            secondary_role="",
            secondary_icon=""
        )
        self.close_btn = button_dict['primary']  # Primary button
        layout.addLayout(button_layout)
        
    def exec_(self):
        """Override exec_ to log dialog result."""
        result = super().exec_()
        log_dialog_result(self, result)
        return result


class EditDocumentDialog(QDialog):
    """Dialog for editing a document."""
    
    def __init__(self, document: dict, database_name: str, collection_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Document")
        self.setModal(True)
        self.setFixedSize(700, 600)
        
        self.original_document = document
        self.database_name = database_name
        self.collection_name = collection_name
        self.edited_document = None
        self.setup_ui()
        
        # Log dialog creation
        log_dialog_creation(self, "EditDocumentDialog")
        
    def setup_ui(self):
        """Setup the dialog UI."""
        # Apply consistent dialog styling
        DialogHelper.apply_dialog_style(self)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Title section
        title_layout = DialogHelper.create_title_section(
            "Edit Document",
            f"Edit document in {self.database_name}/{self.collection_name}"
        )
        layout.addLayout(title_layout)
        
        # Document ID info
        doc_id = self.original_document.get("_id", "No ID")
        id_label = QLabel(f"Document ID: {doc_id}")
        id_label.setStyleSheet("color: #6b7280; font-size: 12px; margin-bottom: 8px;")
        layout.addWidget(id_label)
        
        # Document content editor
        content_group = QGroupBox("Document Content (JSON)")
        content_layout = QVBoxLayout(content_group)
        
        self.document_text = QTextEdit()
        self.document_text.setFont(QFont("Consolas", 10))
        
        # Pre-fill with the original document
        import json
        try:
            formatted_json = json.dumps(self.original_document, indent=2, default=str)
            self.document_text.setPlainText(formatted_json)
        except Exception as e:
            self.document_text.setPlainText(f"Error formatting document: {str(e)}\n\nRaw document: {str(self.original_document)}")
        
        content_layout.addWidget(self.document_text)
        layout.addWidget(content_group)
        
        # Validation info
        self.validation_label = QLabel("")
        self.validation_label.setStyleSheet("color: #6b7280; font-size: 11px; font-style: italic;")
        layout.addWidget(self.validation_label)
        
        # Connect text change to validation
        self.document_text.textChanged.connect(self.validate_json)
        
        # Buttons
        button_layout, button_dict = DialogHelper.create_standard_button_layout(
            self,
            primary_text="Save Changes",
            primary_role="ok",
            primary_icon="fa6s.check",
            secondary_text="Cancel",
            secondary_role="cancel",
            secondary_icon="fa6s.xmark"
        )
        self.save_btn = button_dict['primary']  # Primary button
        self.cancel_btn = button_dict['secondary']  # Secondary button
        layout.addLayout(button_layout)
        
        # Initial validation
        self.validate_json()
        
    def validate_json(self):
        """Validate the JSON input."""
        try:
            text = self.document_text.toPlainText().strip()
            if not text:
                self.validation_label.setText("Empty document")
                self.validation_label.setStyleSheet("color: #dc3545; font-size: 11px; font-style: italic;")
                self.save_btn.setEnabled(False)
                return
            
            import json
            parsed = json.loads(text)
            if not isinstance(parsed, dict):
                self.validation_label.setText("Document must be a JSON object")
                self.validation_label.setStyleSheet("color: #dc3545; font-size: 11px; font-style: italic;")
                self.save_btn.setEnabled(False)
                return
            
            self.validation_label.setText("Valid JSON document")
            self.validation_label.setStyleSheet("color: #28a745; font-size: 11px; font-style: italic;")
            self.save_btn.setEnabled(True)
            
        except json.JSONDecodeError as e:
            self.validation_label.setText(f"Invalid JSON: {str(e)}")
            self.validation_label.setStyleSheet("color: #dc3545; font-size: 11px; font-style: italic;")
            self.save_btn.setEnabled(False)
        except Exception as e:
            self.validation_label.setText(f"Error: {str(e)}")
            self.validation_label.setStyleSheet("color: #dc3545; font-size: 11px; font-style: italic;")
            self.save_btn.setEnabled(False)
    
    def get_document(self):
        """Get the edited document."""
        try:
            text = self.document_text.toPlainText().strip()
            if not text:
                return None
            
            import json
            parsed = json.loads(text)
            if not isinstance(parsed, dict):
                return None
            
            return parsed
        except Exception:
            return None
    
    def exec_(self):
        """Override exec_ to log dialog result."""
        result = super().exec_()
        log_dialog_result(self, result)
        return result


class ConnectionDialog(QDialog):
    """Dialog for configuring MongoDB connection."""
    
    def __init__(self, parent=None, connection_string=""):
        super().__init__(parent)
        self.setWindowTitle("MongoDB Connection")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        self.connection_string = connection_string
        self.setup_ui()
        
        # Log dialog creation
        log_dialog_creation(self, "ConnectionDialog")
        
    def setup_ui(self):
        """Setup the dialog UI."""
        # Apply consistent dialog styling
        DialogHelper.apply_dialog_style(self)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Title section
        title_layout = DialogHelper.create_title_section(
            "MongoDB Connection",
            "Configure connection to MongoDB server"
        )
        layout.addLayout(title_layout)
        
        # Connection form
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Connection string input
        self.connection_edit = QLineEdit()
        self.connection_edit.setPlaceholderText("mongodb://localhost:27017")
        self.connection_edit.setText(self.connection_string)
        form_layout.addRow("Connection String:", self.connection_edit)
        
        # Connection options
        options_group = QGroupBox("Connection Options")
        options_layout = QFormLayout(options_group)
        
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 60)
        self.timeout_spin.setValue(30)
        self.timeout_spin.setSuffix(" seconds")
        options_layout.addRow("Timeout:", self.timeout_spin)
        
        self.retry_writes = QCheckBox("Enable retry writes")
        self.retry_writes.setChecked(True)
        options_layout.addRow("", self.retry_writes)
        
        layout.addLayout(form_layout)
        layout.addWidget(options_group)
        
        # Test connection button
        test_layout = QHBoxLayout()
        test_layout.addStretch()
        
        self.test_btn = QPushButton("Test Connection")
        self.test_btn.setIcon(fa.icon('fa6s.play'))
        self.test_btn.clicked.connect(self.test_connection)
        test_layout.addWidget(self.test_btn)
        
        layout.addLayout(test_layout)
        
        # Buttons
        button_layout, button_dict = DialogHelper.create_standard_button_layout(
            self,
            primary_text="Connect",
            primary_role="ok",
            primary_icon="fa6s.plug",
            secondary_text="Cancel",
            secondary_role="cancel",
            secondary_icon="fa6s.xmark"
        )
        self.connect_btn = button_dict['primary']  # Primary button
        self.cancel_btn = button_dict['secondary']  # Secondary button
        layout.addLayout(button_layout)
        
        # Set focus to connection string input
        self.connection_edit.setFocus()
        
    def test_connection(self):
        """Test the MongoDB connection."""
        import logging
        logger = logging.getLogger(__name__)
        
        connection_string = self.connection_edit.text().strip()
        if not connection_string:
            MessageBoxHelper.warning(self, "Warning", "Please enter a connection string.")
            return
        
        logger.info(f"Testing connection to: {connection_string}")
        
        try:
            from pymongo import MongoClient
            from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
            
            # Create a test client with timeout
            timeout_ms = self.timeout_spin.value() * 1000
            client = MongoClient(connection_string, serverSelectionTimeoutMS=timeout_ms)
            
            # Test the connection
            client.admin.command('ping')
            
            # Get server info
            server_info = client.server_info()
            version = server_info.get('version', 'Unknown')
            
            logger.info(f"Connection test successful - MongoDB version: {version}")
            MessageBoxHelper.success(
                self,
                "Connection Test Successful",
                f"Successfully connected to MongoDB server!\n\n"
                f"Server Version: {version}\n"
                f"Connection String: {connection_string}"
            )
            
            client.close()
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Connection test failed: {e}")
            MessageBoxHelper.critical(
                self,
                "Connection Test Failed",
                f"Failed to connect to MongoDB server.\n\n"
                f"Error: {str(e)}\n\n"
                f"Please check:\n"
                f"• Connection string is correct\n"
                f"• MongoDB server is running\n"
                f"• Network connectivity\n"
                f"• Firewall settings"
            )
        except Exception as e:
            logger.error(f"Unexpected error during connection test: {e}")
            MessageBoxHelper.critical(
                self,
                "Connection Test Error",
                f"Unexpected error during connection test.\n\n"
                f"Error: {str(e)}"
            )
    
    def get_connection_string(self):
        """Get the connection string."""
        return self.connection_edit.text().strip()
    
    def get_connection_options(self):
        """Get the connection options."""
        return {
            'timeout': self.timeout_spin.value(),
            'retry_writes': self.retry_writes.isChecked()
        }
    
    def exec_(self):
        """Override exec_ to log dialog result."""
        result = super().exec_()
        log_dialog_result(self, result)
        return result


class InsertDocumentDialog(QDialog):
    """Dialog for inserting a new document."""
    
    def __init__(self, database_name: str, collection_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Insert Document")
        self.setModal(True)
        self.setFixedSize(700, 600)
        
        self.database_name = database_name
        self.collection_name = collection_name
        self.inserted_document = None
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
            "Insert Document",
            f"Insert new document into {self.database_name}/{self.collection_name}"
        )
        layout.addLayout(title_layout)
        
        # Document content editor
        content_group = QGroupBox("Document Content (JSON)")
        content_layout = QVBoxLayout(content_group)
        
        self.document_text = QTextEdit()
        self.document_text.setFont(QFont("Consolas", 10))
        
        # Pre-fill with a sample document
        sample_document = {
            "name": "Sample Document",
            "description": "This is a sample document",
            "created_at": "2024-01-01T00:00:00Z",
            "tags": ["sample", "document"],
            "metadata": {
                "version": 1,
                "active": True
            }
        }
        
        import json
        try:
            formatted_json = json.dumps(sample_document, indent=2)
            self.document_text.setPlainText(formatted_json)
        except Exception as e:
            self.document_text.setPlainText('{\n  "name": "Sample Document",\n  "description": "This is a sample document"\n}')
        
        content_layout.addWidget(self.document_text)
        layout.addWidget(content_group)
        
        # Validation info
        self.validation_label = QLabel("")
        self.validation_label.setStyleSheet("color: #6b7280; font-size: 11px; font-style: italic;")
        layout.addWidget(self.validation_label)
        
        # Connect text change to validation
        self.document_text.textChanged.connect(self.validate_json)
        
        # Buttons
        button_layout, button_dict = DialogHelper.create_standard_button_layout(
            self,
            primary_text="Insert Document",
            primary_role="ok",
            primary_icon="fa6s.plus",
            secondary_text="Cancel",
            secondary_role="cancel",
            secondary_icon="fa6s.xmark"
        )
        self.insert_btn = button_dict['primary']  # Primary button
        self.cancel_btn = button_dict['secondary']  # Secondary button
        layout.addLayout(button_layout)
        
        # Initial validation
        self.validate_json()
        
    def validate_json(self):
        """Validate the JSON input."""
        try:
            text = self.document_text.toPlainText().strip()
            if not text:
                self.validation_label.setText("Empty document")
                self.validation_label.setStyleSheet("color: #dc3545; font-size: 11px; font-style: italic;")
                self.insert_btn.setEnabled(False)
                return
            
            import json
            parsed = json.loads(text)
            if not isinstance(parsed, dict):
                self.validation_label.setText("Document must be a JSON object")
                self.validation_label.setStyleSheet("color: #dc3545; font-size: 11px; font-style: italic;")
                self.insert_btn.setEnabled(False)
                return
            
            self.validation_label.setText("Valid JSON document")
            self.validation_label.setStyleSheet("color: #28a745; font-size: 11px; font-style: italic;")
            self.insert_btn.setEnabled(True)
            
        except json.JSONDecodeError as e:
            self.validation_label.setText(f"Invalid JSON: {str(e)}")
            self.validation_label.setStyleSheet("color: #dc3545; font-size: 11px; font-style: italic;")
            self.insert_btn.setEnabled(False)
        except Exception as e:
            self.validation_label.setText(f"Error: {str(e)}")
            self.validation_label.setStyleSheet("color: #dc3545; font-size: 11px; font-style: italic;")
            self.insert_btn.setEnabled(False)
    
    def get_document(self):
        """Get the document to insert."""
        try:
            text = self.document_text.toPlainText().strip()
            if not text:
                return None
            
            import json
            parsed = json.loads(text)
            if not isinstance(parsed, dict):
                return None
            
            return parsed
        except Exception:
            return None
    
    def exec_(self):
        """Override exec_ to log dialog result."""
        result = super().exec_()
        log_dialog_result(self, result)
        return result
