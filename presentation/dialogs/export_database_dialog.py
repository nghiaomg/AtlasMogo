"""
Export Database Dialog
Dialog for exporting an entire database to JSON, BSON, or a compressed ZIP.
"""

import os
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QFileDialog, QLineEdit, QGroupBox, QMessageBox,
    QProgressBar, QCheckBox
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont

from data.database_exporter import DatabaseExporter
from presentation.dialogs.toast_notification import ToastManager


class DatabaseExportWorker(QThread):
    """Worker thread for database export operations."""
    
    export_completed = Signal(bool, str)
    
    def __init__(self, mongo_service, database_name: str, output_path: str, 
                 export_format: str, use_compression: bool):
        super().__init__()
        self.exporter = DatabaseExporter(mongo_service, database_name)
        self.output_path = output_path
        self.export_format = export_format
        self.use_compression = use_compression
    
    def run(self):
        """Run the export operation in a separate thread."""
        try:
            success, message = self.exporter.export_database(
                self.output_path, self.export_format, self.use_compression
            )
            self.export_completed.emit(success, message)
        except Exception as e:
            self.export_completed.emit(False, f"An unexpected error occurred: {e}")


class ExportDatabaseDialog(QDialog):
    """Dialog for exporting a full database."""
    
    def __init__(self, parent, mongo_service, database_name: str):
        super().__init__(parent)
        self.mongo_service = mongo_service
        self.database_name = database_name
        self.export_worker = None

        self.setWindowTitle("Export Database")
        self.setModal(True)
        self.resize(500, 350)

        self.setup_ui()
        self.setup_connections()
        self.update_ui_for_export_type()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Database Info
        db_label = QLabel(f"Database: {self.database_name}")
        font = QFont()
        font.setBold(True)
        db_label.setFont(font)
        layout.addWidget(db_label)

        # Export Options
        options_group = QGroupBox("Export Options")
        options_layout = QVBoxLayout(options_group)

        # Format
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItem("JSON", "json")
        self.format_combo.addItem("BSON", "bson")
        format_layout.addWidget(self.format_combo)
        options_layout.addLayout(format_layout)

        # Compression
        self.compress_check = QCheckBox("Compress output to a single ZIP file")
        self.compress_check.setChecked(True)
        options_layout.addWidget(self.compress_check)
        layout.addWidget(options_group)

        # Output Destination
        dest_group = QGroupBox("Destination")
        dest_layout = QVBoxLayout(dest_group)
        dest_file_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Select destination...")
        dest_file_layout.addWidget(self.path_edit)
        self.browse_button = QPushButton("Browse...")
        dest_file_layout.addWidget(self.browse_button)
        dest_layout.addLayout(dest_file_layout)
        layout.addWidget(dest_group)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.export_button = QPushButton("Export")
        self.export_button.setDefault(True)
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

    def setup_connections(self):
        self.browse_button.clicked.connect(self.browse_destination)
        self.export_button.clicked.connect(self.start_export)
        self.cancel_button.clicked.connect(self.reject)
        self.compress_check.stateChanged.connect(self.update_ui_for_export_type)

    def update_ui_for_export_type(self):
        if self.compress_check.isChecked():
            self.path_edit.setPlaceholderText("Select destination ZIP file...")
        else:
            self.path_edit.setPlaceholderText("Select destination folder...")
        self.path_edit.setText("")

    def browse_destination(self):
        default_dir = os.path.expanduser("~/Documents")
        default_filename = f"{self.database_name}_{datetime.now().strftime('%Y%m%d')}"

        if self.compress_check.isChecked():
            file_filter = "ZIP Archives (*.zip)"
            default_path = os.path.join(default_dir, f"{default_filename}.zip")
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Exported Database", default_path, file_filter
            )
            if file_path:
                self.path_edit.setText(file_path)
        else:
            dir_path = QFileDialog.getExistingDirectory(
                self, "Select Export Directory", default_dir
            )
            if dir_path:
                # Suggest a subfolder for the export
                final_path = os.path.join(dir_path, default_filename)
                self.path_edit.setText(final_path)

    def start_export(self):
        output_path = self.path_edit.text().strip()
        if not output_path:
            QMessageBox.warning(self, "Input Error", "Please select a destination.")
            return

        if os.path.exists(output_path):
            reply = QMessageBox.question(
                self, "Confirm Overwrite",
                f"The destination '{os.path.basename(output_path)}' already exists. Overwrite?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        self.set_ui_enabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate

        export_format = self.format_combo.currentData()
        use_compression = self.compress_check.isChecked()

        self.export_worker = DatabaseExportWorker(
            self.mongo_service, self.database_name, output_path, 
            export_format, use_compression
        )
        self.export_worker.export_completed.connect(self.export_finished)
        self.export_worker.start()

    def export_finished(self, success: bool, message: str):
        self.progress_bar.setRange(0, 1) # Stop indeterminate animation
        self.progress_bar.setValue(1)
        self.set_ui_enabled(True)

        toast_manager = ToastManager()
        if success:
            toast_manager.show_success(message, self.parent())
            QTimer.singleShot(1000, self.accept)
        else:
            toast_manager.show_error(message, self.parent(), duration=5000)
            QMessageBox.critical(self, "Export Failed", message)

    def set_ui_enabled(self, enabled: bool):
        self.format_combo.setEnabled(enabled)
        self.compress_check.setEnabled(enabled)
        self.path_edit.setEnabled(enabled)
        self.browse_button.setEnabled(enabled)
        self.export_button.setEnabled(enabled)

    def closeEvent(self, event):
        if self.export_worker and self.export_worker.isRunning():
            reply = QMessageBox.question(
                self, "Export in Progress",
                "An export is currently in progress. Are you sure you want to cancel?",
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

