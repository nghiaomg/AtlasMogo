"""
Export Schema Dialog
Dialog for selecting export format and file location for database schema export.
"""

import os
from pathlib import Path
from typing import Optional, Tuple

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QFileDialog, QLineEdit, QGroupBox, QMessageBox,
    QProgressBar, QTextEdit
)
from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtGui import QFont

from data.schema_exporter import SchemaExporter
from presentation.dialogs.toast_notification import ToastManager


class SchemaExportWorker(QThread):
    """Worker thread for schema export operations."""
    
    progress_updated = Signal(str)
    export_completed = Signal(bool, str)
    
    def __init__(self, mongo_service, database_name: str, file_path: str, 
                 format_type: str, sample_size: int = 100):
        super().__init__()
        self.mongo_service = mongo_service
        self.database_name = database_name
        self.file_path = file_path
        self.format_type = format_type
        self.sample_size = sample_size
        self.exporter = SchemaExporter()
    
    def run(self):
        """Run the export operation in a separate thread."""
        try:
            self.progress_updated.emit("Analyzing database schema...")
            
            # Analyze database schema
            schema_data = self.mongo_service.analyze_database_schema(
                self.database_name, self.sample_size
            )
            
            if not schema_data:
                self.export_completed.emit(False, "No collections found or unable to analyze schema")
                return
            
            self.progress_updated.emit(f"Exporting to {self.format_type.upper()} format...")
            
            # Export schema
            success = self.exporter.export_schema(
                schema_data, self.file_path, self.database_name, self.format_type
            )
            
            if success:
                self.export_completed.emit(True, f"Schema exported successfully to {self.file_path}")
            else:
                self.export_completed.emit(False, "Failed to export schema")
                
        except Exception as e:
            self.export_completed.emit(False, f"Export error: {str(e)}")


class ExportSchemaDialog(QDialog):
    """Dialog for exporting database schema to various formats."""
    
    def __init__(self, parent=None, mongo_service=None, database_name: str = ""):
        super().__init__(parent)
        self.mongo_service = mongo_service
        self.database_name = database_name
        self.export_worker = None
        
        self.setWindowTitle("Export Database Schema")
        self.setModal(True)
        self.resize(500, 400)
        
        self.setup_ui()
        self.setup_connections()
        
        # Initialize with default values
        if self.database_name:
            self.database_label.setText(f"Database: {self.database_name}")
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Database info
        self.database_label = QLabel("Database: Not selected")
        font = QFont()
        font.setBold(True)
        self.database_label.setFont(font)
        layout.addWidget(self.database_label)
        
        # Export format selection
        format_group = QGroupBox("Export Format")
        format_layout = QVBoxLayout(format_group)
        
        format_selection_layout = QHBoxLayout()
        format_selection_layout.addWidget(QLabel("Format:"))
        
        self.format_combo = QComboBox()
        self.format_combo.addItem("JSON (.json)", "json")
        self.format_combo.addItem("YAML (.yaml)", "yaml")
        self.format_combo.addItem("Markdown (.md)", "markdown")
        format_selection_layout.addWidget(self.format_combo)
        
        format_layout.addLayout(format_selection_layout)
        
        # Format description
        self.format_description = QLabel()
        self.format_description.setWordWrap(True)
        self.format_description.setStyleSheet("color: #666; font-size: 11px;")
        format_layout.addWidget(self.format_description)
        
        layout.addWidget(format_group)
        
        # File selection
        file_group = QGroupBox("Output File")
        file_layout = QVBoxLayout(file_group)
        
        file_selection_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Select output file location...")
        file_selection_layout.addWidget(self.file_path_edit)
        
        self.browse_button = QPushButton("Browse...")
        file_selection_layout.addWidget(self.browse_button)
        
        file_layout.addLayout(file_selection_layout)
        layout.addWidget(file_group)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)
        
        sample_layout = QHBoxLayout()
        sample_layout.addWidget(QLabel("Sample size per collection:"))
        
        self.sample_combo = QComboBox()
        self.sample_combo.addItem("50 documents", 50)
        self.sample_combo.addItem("100 documents", 100)
        self.sample_combo.addItem("200 documents", 200)
        self.sample_combo.addItem("500 documents", 500)
        self.sample_combo.setCurrentIndex(1)  # Default to 100
        sample_layout.addWidget(self.sample_combo)
        
        options_layout.addLayout(sample_layout)
        layout.addWidget(options_group)
        
        # Progress area
        self.progress_group = QGroupBox("Export Progress")
        progress_layout = QVBoxLayout(self.progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_text = QTextEdit()
        self.progress_text.setMaximumHeight(100)
        self.progress_text.setVisible(False)
        progress_layout.addWidget(self.progress_text)
        
        layout.addWidget(self.progress_group)
        self.progress_group.setVisible(False)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.export_button = QPushButton("Export Schema")
        self.export_button.setDefault(True)
        button_layout.addWidget(self.export_button)
        
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Update format description initially
        self.update_format_description()
    
    def setup_connections(self):
        """Set up signal connections."""
        self.format_combo.currentTextChanged.connect(self.update_format_description)
        self.format_combo.currentTextChanged.connect(self.update_file_extension)
        self.browse_button.clicked.connect(self.browse_file)
        self.export_button.clicked.connect(self.start_export)
        self.cancel_button.clicked.connect(self.reject)
    
    def update_format_description(self):
        """Update the format description based on selected format."""
        format_data = self.format_combo.currentData()
        descriptions = {
            "json": "Export as structured JSON data. Good for programmatic access and data interchange.",
            "yaml": "Export as human-readable YAML format. Easy to read and edit manually.",
            "markdown": "Export as formatted documentation with tables and code blocks. Perfect for documentation."
        }
        
        description = descriptions.get(format_data, "")
        self.format_description.setText(description)
    
    def update_file_extension(self):
        """Update file extension when format changes."""
        current_path = self.file_path_edit.text()
        if current_path:
            path = Path(current_path)
            format_data = self.format_combo.currentData()
            extensions = {"json": ".json", "yaml": ".yaml", "markdown": ".md"}
            new_extension = extensions.get(format_data, ".json")
            
            # Replace extension
            new_path = path.with_suffix(new_extension)
            self.file_path_edit.setText(str(new_path))
    
    def browse_file(self):
        """Open file dialog to select output file."""
        format_data = self.format_combo.currentData()
        
        # Set up file dialog filters
        filters = {
            "json": "JSON Files (*.json);;All Files (*)",
            "yaml": "YAML Files (*.yaml *.yml);;All Files (*)",
            "markdown": "Markdown Files (*.md);;All Files (*)"
        }
        
        file_filter = filters.get(format_data, "All Files (*)")
        
        # Suggest default filename
        default_name = f"{self.database_name}_schema" if self.database_name else "database_schema"
        extensions = {"json": ".json", "yaml": ".yaml", "markdown": ".md"}
        default_extension = extensions.get(format_data, ".json")
        default_filename = f"{default_name}{default_extension}"
        
        # Get user's documents directory
        documents_dir = os.path.expanduser("~/Documents")
        default_path = os.path.join(documents_dir, default_filename)
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Schema Export", default_path, file_filter
        )
        
        if file_path:
            self.file_path_edit.setText(file_path)
    
    def validate_inputs(self) -> Tuple[bool, str]:
        """Validate user inputs before export."""
        if not self.database_name:
            return False, "No database selected"
        
        if not self.file_path_edit.text().strip():
            return False, "Please select an output file location"
        
        file_path = self.file_path_edit.text().strip()
        
        # Check if directory exists
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            return False, f"Directory does not exist: {directory}"
        
        # Check if file already exists
        if os.path.exists(file_path):
            reply = QMessageBox.question(
                self, "File Exists", 
                f"The file '{file_path}' already exists. Do you want to overwrite it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return False, "Export cancelled"
        
        return True, ""
    
    def start_export(self):
        """Start the schema export process."""
        # Validate inputs
        valid, error_message = self.validate_inputs()
        if not valid:
            QMessageBox.warning(self, "Validation Error", error_message)
            return
        
        # Disable UI during export
        self.export_button.setEnabled(False)
        self.browse_button.setEnabled(False)
        self.format_combo.setEnabled(False)
        self.sample_combo.setEnabled(False)
        
        # Show progress
        self.progress_group.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_text.setVisible(True)
        self.progress_text.clear()
        
        # Get export parameters
        file_path = self.file_path_edit.text().strip()
        format_type = self.format_combo.currentData()
        sample_size = self.sample_combo.currentData()
        
        # Start export worker
        self.export_worker = SchemaExportWorker(
            self.mongo_service, self.database_name, file_path, format_type, sample_size
        )
        self.export_worker.progress_updated.connect(self.update_progress)
        self.export_worker.export_completed.connect(self.export_finished)
        self.export_worker.start()
    
    def update_progress(self, message: str):
        """Update progress display."""
        self.progress_text.append(message)
        # Auto-scroll to bottom
        cursor = self.progress_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.progress_text.setTextCursor(cursor)
    
    def export_finished(self, success: bool, message: str):
        """Handle export completion."""
        # Re-enable UI
        self.export_button.setEnabled(True)
        self.browse_button.setEnabled(True)
        self.format_combo.setEnabled(True)
        self.sample_combo.setEnabled(True)
        
        # Hide progress
        self.progress_bar.setVisible(False)
        
        # Update progress text
        self.update_progress(message)
        
        if success:
            # Show success toast
            if self.parent():
                toast_manager = ToastManager()
                toast_manager.show_success(f"Schema exported successfully to {Path(self.file_path_edit.text()).name}", self.parent())
            
            # Close dialog after a short delay
            QTimer.singleShot(1500, self.accept)
        else:
            # Show error message
            QMessageBox.critical(self, "Export Error", message)
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        if self.export_worker and self.export_worker.isRunning():
            reply = QMessageBox.question(
                self, "Export in Progress", 
                "Export is currently in progress. Do you want to cancel it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.export_worker.terminate()
                self.export_worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
    
    def get_export_info(self) -> Optional[dict]:
        """Get export information if dialog was accepted."""
        if self.result() == QDialog.DialogCode.Accepted:
            return {
                "database_name": self.database_name,
                "file_path": self.file_path_edit.text().strip(),
                "format_type": self.format_combo.currentData(),
                "sample_size": self.sample_combo.currentData()
            }
        return None
