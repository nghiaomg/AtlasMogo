"""
Import Database Dialog
Dialog for importing a full database from JSON/BSON/ZIP with overwrite control.
"""

import os
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QLineEdit, QGroupBox, QMessageBox, QProgressBar, QTableWidget, QTableWidgetItem,
    QHeaderView, QCheckBox
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer

from data.database_importer import DatabaseImporter
from presentation.dialogs.toast_notification import ToastManager


class DatabaseImportWorker(QThread):
    import_completed = Signal(bool, str)

    def __init__(self, mongo_service, database_name: str, source_path: str, overwrite_policy: dict[str, bool]):
        super().__init__()
        self.importer = DatabaseImporter(mongo_service, database_name)
        self.source_path = source_path
        self.overwrite_policy = overwrite_policy

    def run(self):
        try:
            success, message = self.importer.import_database(self.source_path, self.overwrite_policy)
            self.import_completed.emit(success, message)
        except Exception as e:
            self.import_completed.emit(False, f"An unexpected error occurred: {e}")


class ImportDatabaseDialog(QDialog):
    def __init__(self, parent, mongo_service, database_name: str):
        super().__init__(parent)
        self.mongo_service = mongo_service
        self.database_name = database_name
        self.import_worker = None

        self.setWindowTitle("Import Database")
        self.setModal(True)
        self.resize(640, 420)

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Source path
        src_group = QGroupBox("Source")
        src_layout = QHBoxLayout(src_group)
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Select a JSON/BSON/ZIP file or a folder...")
        browse_btn = QPushButton("Browse...")
        src_layout.addWidget(self.path_edit)
        src_layout.addWidget(browse_btn)
        layout.addWidget(src_group)

        self._browse_btn = browse_btn

        # Overwrite table (appears after selecting a source)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Collection", "Overwrite if exists"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.setVisible(False)
        layout.addWidget(self.table)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.import_btn = QPushButton("Import")
        self.cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(self.import_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def _connect_signals(self):
        self._browse_btn.clicked.connect(self._choose_source)
        self.import_btn.clicked.connect(self._start_import)
        self.cancel_btn.clicked.connect(self.reject)

    def _choose_source(self):
        # Allow both file and directory
        files_filter = "Supported Files (*.json *.bson *.zip);;All Files (*)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Select file (or Cancel to pick folder)", os.path.expanduser("~/Documents"), files_filter)
        if file_path:
            self.path_edit.setText(file_path)
            self._prepare_overwrite_table(Path(file_path).parent)
            return
        # If user cancels, allow directory
        dir_path = QFileDialog.getExistingDirectory(self, "Select folder", os.path.expanduser("~/Documents"))
        if dir_path:
            self.path_edit.setText(dir_path)
            self._prepare_overwrite_table(dir_path)

    def _prepare_overwrite_table(self, directory: str | Path):
        # Simple scan: list plausible collection files (*.json/*.bson)
        self.table.setRowCount(0)
        found = []
        for p in Path(directory).rglob('*'):
            if p.is_file() and p.suffix.lower() in ('.json', '.bson'):
                found.append(p.stem)
        # Unique collection names
        collections = sorted(set(found))
        self.table.setVisible(bool(collections))
        self.table.setRowCount(len(collections))
        for row, name in enumerate(collections):
            self.table.setItem(row, 0, QTableWidgetItem(name))
            chk = QCheckBox()
            self.table.setCellWidget(row, 1, chk)

    def _start_import(self):
        src = self.path_edit.text().strip()
        if not src:
            QMessageBox.warning(self, "Input Error", "Please select a source file or folder.")
            return
        overwrite = {}
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text()
            chk = self.table.cellWidget(row, 1)
            overwrite[name] = bool(chk.isChecked())

        self._set_enabled(False)
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)

        self.import_worker = DatabaseImportWorker(self.mongo_service, self.database_name, src, overwrite)
        self.import_worker.import_completed.connect(self._on_import_finished)
        self.import_worker.start()

    def _on_import_finished(self, success: bool, message: str):
        self.progress.setRange(0, 1)
        self.progress.setValue(1)
        self._set_enabled(True)

        tm = ToastManager()
        if success:
            tm.show_success(message, self.parent())
            QTimer.singleShot(1000, self.accept)
        else:
            tm.show_error(message, self.parent(), duration=6000)
            QMessageBox.critical(self, "Import Failed", message)

    def _set_enabled(self, enabled: bool):
        for w in (self._browse_btn, self.import_btn, self.path_edit):
            w.setEnabled(enabled)

    def closeEvent(self, event):
        if self.import_worker and self.import_worker.isRunning():
            reply = QMessageBox.question(
                self, "Import in Progress",
                "An import is currently in progress. Are you sure you want to cancel?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.import_worker.terminate()
                self.import_worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
