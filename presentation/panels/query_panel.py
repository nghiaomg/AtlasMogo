"""
Query Panel Component
Handles MongoDB query execution and results display.
"""

from __future__ import annotations

import qtawesome as fa
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import (
    QFormLayout, QGroupBox, QHBoxLayout, QLabel, QPushButton, QSizePolicy,
    QSpinBox, QTextEdit, QVBoxLayout, QWidget
)


class QueryPanel(QObject):
    """Query panel component for MongoDB query execution."""
    
    # Signals
    query_executed = Signal(str, int)  # Emits query filter, limit
    
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.parent = parent
        self.widget: QWidget | None = None
        self.query_filter: QTextEdit | None = None
        self.query_limit: QSpinBox | None = None
        self.query_results: QTextEdit | None = None
        self._create_query_panel()
    
    def _create_query_panel(self) -> None:
        """Create the query panel widget."""
        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)
        layout.setSpacing(12)
        layout.setContentsMargins(4, 4, 4, 4)
        
        self._create_query_input_section(layout)
        self._create_results_section(layout)
    
    def _create_query_input_section(self, parent_layout: QVBoxLayout) -> None:
        """Create the query input section."""
        query_group = QGroupBox("Query Documents")
        query_form_layout = QFormLayout(query_group)
        query_form_layout.setSpacing(8)
        
        # Query filter input
        self.query_filter = QTextEdit()
        self.query_filter.setPlaceholderText('{"field": "value"}')
        self.query_filter.setMinimumHeight(60)
        self.query_filter.setMaximumHeight(100)
        self.query_filter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        query_form_layout.addRow("Query Filter:", self.query_filter)
        
        # Limit input
        limit_layout = QHBoxLayout()
        limit_layout.setSpacing(8)
        
        limit_label = QLabel("Limit:")
        limit_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        limit_label.setMinimumHeight(24)
        
        self.query_limit = QSpinBox()
        self.query_limit.setRange(1, 10000)
        self.query_limit.setValue(100)
        self.query_limit.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.query_limit.setMinimumHeight(24)
        
        limit_layout.addWidget(limit_label)
        limit_layout.addWidget(self.query_limit)
        limit_layout.addStretch()
        query_form_layout.addRow("", limit_layout)
        
        # Execute button
        execute_button = QPushButton(fa.icon('fa6s.play'), "Execute Query")
        execute_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        execute_button.setMinimumHeight(28)
        execute_button.setMinimumWidth(120)
        execute_button.clicked.connect(self._on_execute_clicked)
        query_form_layout.addRow("", execute_button)
        
        parent_layout.addWidget(query_group)
    
    def _create_results_section(self, parent_layout: QVBoxLayout) -> None:
        """Create the query results section."""
        results_group = QGroupBox("Query Results")
        results_layout = QVBoxLayout(results_group)
        results_layout.setSpacing(8)
        
        self.query_results = QTextEdit()
        self.query_results.setReadOnly(True)
        self.query_results.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.query_results.setMinimumHeight(200)
        results_layout.addWidget(self.query_results)
        
        parent_layout.addWidget(results_group)
    
    def _on_execute_clicked(self) -> None:
        """Handle execute query button click."""
        query_text = self.query_filter.toPlainText().strip()
        limit = self.query_limit.value()
        
        if query_text:
            self.query_executed.emit(query_text, limit)
        else:
            # Execute with empty filter (get all documents)
            self.query_executed.emit("", limit)
    
    def get_widget(self) -> QWidget | None:
        """Get the query panel widget."""
        return self.widget
    
    def get_query_filter(self) -> str:
        """Get the current query filter text."""
        if self.query_filter:
            return self.query_filter.toPlainText().strip()
        return ""
    
    def get_query_limit(self) -> int:
        """Get the current query limit value."""
        if self.query_limit:
            return self.query_limit.value()
        return 100
    
    def set_query_filter(self, text: str) -> None:
        """Set the query filter text."""
        if self.query_filter:
            self.query_filter.setPlainText(text)
    
    def set_query_limit(self, limit: int) -> None:
        """Set the query limit value."""
        if self.query_limit:
            self.query_limit.setValue(limit)
    
    def set_query_results(self, results: str) -> None:
        """Set the query results text."""
        if self.query_results:
            self.query_results.setPlainText(results)
    
    def clear_query_filter(self) -> None:
        """Clear the query filter text."""
        if self.query_filter:
            self.query_filter.clear()
    
    def clear_query_results(self) -> None:
        """Clear the query results."""
        if self.query_results:
            self.query_results.clear()
    
    def set_query_placeholder(self, text: str) -> None:
        """Set the placeholder text for query filter."""
        if self.query_filter:
            self.query_filter.setPlaceholderText(text)
    
    def set_results_placeholder(self, text: str) -> None:
        """Set the placeholder text for query results."""
        if self.query_results:
            self.query_results.setPlaceholderText(text)
    
    def enable_query_execution(self, enabled: bool = True) -> None:
        """Enable or disable query execution."""
        if self.query_filter:
            self.query_filter.setEnabled(enabled)
        if self.query_limit:
            self.query_limit.setEnabled(enabled)
    
    def set_query_filter_readonly(self, readonly: bool = True) -> None:
        """Set the query filter to read-only mode."""
        if self.query_filter:
            self.query_filter.setReadOnly(readonly)
    
    def set_results_readonly(self, readonly: bool = True) -> None:
        """Set the results area to read-only mode."""
        if self.query_results:
            self.query_results.setReadOnly(readonly)
