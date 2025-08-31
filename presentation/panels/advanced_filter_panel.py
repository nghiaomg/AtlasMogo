"""
Advanced Filter Panel Component
Provides enhanced filtering capabilities for MongoDB documents with both basic and advanced modes.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional, Tuple

import qtawesome as fa
from PySide6.QtCore import QObject, QTimer, Signal, Qt
from PySide6.QtGui import QFont, QTextCharFormat, QSyntaxHighlighter, QColor, QPalette
from PySide6.QtWidgets import (
    QComboBox, QCompleter, QFormLayout, QGroupBox, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QSizePolicy, QSpinBox, QTabWidget, QTextEdit,
    QVBoxLayout, QWidget, QCheckBox, QFrame, QScrollArea, QToolButton,
    QMessageBox, QApplication
)

from ..styles.styles import BUTTON_STYLES, COLORS


class JSONSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for JSON text with error highlighting."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.error_line = -1
        self.error_message = ""
        
        # Define formats
        self.key_format = QTextCharFormat()
        self.key_format.setForeground(QColor("#0366d6"))
        self.key_format.setFontWeight(QFont.Bold)
        
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#032f62"))
        
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#005cc5"))
        
        self.operator_format = QTextCharFormat()
        self.operator_format.setForeground(QColor("#d73a49"))
        self.operator_format.setFontWeight(QFont.Bold)
        
        self.error_format = QTextCharFormat()
        self.error_format.setBackground(QColor("#ffebee"))
        self.error_format.setForeground(QColor("#c62828"))
        
    def highlightBlock(self, text: str):
        """Highlight a block of text."""
        # Reset formatting
        self.setFormat(0, len(text), QTextCharFormat())
        
        # Highlight keys (quoted strings followed by colon)
        import re
        key_pattern = r'"([^"]+)"\s*:'
        for match in re.finditer(key_pattern, text):
            self.setFormat(match.start(1), match.end(1) - match.start(1), self.key_format)
            
        # Highlight string values
        string_pattern = r':\s*"([^"]*)"'
        for match in re.finditer(string_pattern, text):
            self.setFormat(match.start(1), match.end(1) - match.start(1), self.string_format)
            
        # Highlight numbers
        number_pattern = r':\s*(\d+(?:\.\d+)?)'
        for match in re.finditer(number_pattern, text):
            self.setFormat(match.start(1), match.end(1) - match.start(1), self.number_format)
            
        # Highlight operators
        operator_pattern = r'\$[a-zA-Z]+'
        for match in re.finditer(operator_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.operator_format)
            
        # Highlight error line if specified
        if self.error_line >= 0:
            line_number = self.currentBlock().blockNumber()
            if line_number == self.error_line:
                self.setFormat(0, len(text), self.error_format)
    
    def set_error(self, line: int, message: str):
        """Set error highlighting for a specific line."""
        if self.error_line != line or self.error_message != message:
            self.error_line = line
            self.error_message = message
            # Use a timer to prevent recursion
            QTimer.singleShot(0, self.rehighlight)
    
    def clear_error(self):
        """Clear error highlighting."""
        if self.error_line != -1 or self.error_message:
            self.error_line = -1
            self.error_message = ""
            # Use a timer to prevent recursion
            QTimer.singleShot(0, self.rehighlight)


class AdvancedFilterPanel(QObject):
    """Advanced filter panel component with basic and advanced modes."""
    
    # Signals
    filter_applied = Signal(str, int)  # Emits filter JSON, limit
    filter_reset = Signal()
    
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.parent = parent
        self.widget: QWidget | None = None
        
        # UI Components
        self.mode_tabs: QTabWidget | None = None
        self.basic_widget: QWidget | None = None
        self.advanced_widget: QWidget | None = None
        
        # Basic mode components
        self.field_combo: QComboBox | None = None
        self.operator_combo: QComboBox | None = None
        self.value_input: QLineEdit | None = None
        self.add_filter_btn: QPushButton | None = None
        self.active_filters_frame: QFrame | None = None
        
        # Advanced mode components
        self.json_editor: QTextEdit | None = None
        self.syntax_highlighter: JSONSyntaxHighlighter | None = None
        
        # Common components
        self.limit_spinbox: QSpinBox | None = None
        self.apply_btn: QPushButton | None = None
        self.reset_btn: QPushButton | None = None
        
        # Data
        self.available_fields: List[str] = []
        self.active_filters: List[Dict[str, Any]] = []
        self.field_values_cache: Dict[str, List[str]] = {}
        
        # Setup
        self._create_filter_panel()
        self._setup_autocomplete()
        
        # Logging
        self.logger = logging.getLogger(__name__)
    
    def _create_filter_panel(self) -> None:
        """Create the main filter panel widget."""
        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)
        layout.setSpacing(16)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Create mode tabs
        self._create_mode_tabs(layout)
        
        # Create common controls
        self._create_common_controls(layout)
        
        # Create quick templates
        self._create_quick_templates(layout)
    
    def _create_mode_tabs(self, parent_layout: QVBoxLayout) -> None:
        """Create the mode selection tabs."""
        self.mode_tabs = QTabWidget()
        self.mode_tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        # Basic mode tab
        self.basic_widget = self._create_basic_mode()
        self.mode_tabs.addTab(self.basic_widget, "Basic Mode")
        
        # Advanced mode tab
        self.advanced_widget = self._create_advanced_mode()
        self.mode_tabs.addTab(self.advanced_widget, "Advanced Mode")
        
        parent_layout.addWidget(self.mode_tabs)
    
    def _create_basic_mode(self) -> QWidget:
        """Create the basic filtering mode widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Filter input section
        filter_group = QGroupBox("Add Filter")
        filter_layout = QFormLayout(filter_group)
        filter_layout.setSpacing(8)
        
        # Field selection
        self.field_combo = QComboBox()
        self.field_combo.setEditable(True)
        self.field_combo.setPlaceholderText("Select or type field name")
        self.field_combo.setMinimumHeight(28)
        filter_layout.addRow("Field:", self.field_combo)
        
        # Operator selection
        self.operator_combo = QComboBox()
        self.operator_combo.addItems([
            "equals", "not equals", "contains", "starts with", "ends with",
            "greater than", "less than", "greater than or equal", "less than or equal",
            "in list", "not in list", "exists", "regex"
        ])
        self.operator_combo.setMinimumHeight(28)
        filter_layout.addRow("Operator:", self.operator_combo)
        
        # Value input
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Enter value or leave empty for 'exists'")
        self.value_input.setMinimumHeight(28)
        filter_layout.addRow("Value:", self.value_input)
        
        # Add filter button
        self.add_filter_btn = QPushButton(fa.icon('fa6s.plus'), "Add Filter")
        self.add_filter_btn.setStyleSheet(BUTTON_STYLES['dialog_primary'])
        self.add_filter_btn.setMinimumHeight(28)
        self.add_filter_btn.clicked.connect(self._add_basic_filter)
        filter_layout.addRow("", self.add_filter_btn)
        
        layout.addWidget(filter_group)
        
        # Active filters display
        active_group = QGroupBox("Active Filters")
        active_layout = QVBoxLayout(active_group)
        
        self.active_filters_frame = QFrame()
        self.active_filters_frame.setFrameStyle(QFrame.StyledPanel)
        self.active_filters_frame.setStyleSheet(f"""
            QFrame {{
                border: 1px solid {COLORS['border_light']};
                border-radius: 6px;
                background-color: {COLORS['bg_secondary']};
                padding: 8px;
            }}
        """)
        
        self._update_active_filters_display()
        active_layout.addWidget(self.active_filters_frame)
        
        layout.addWidget(active_group)
        layout.addStretch()
        
        return widget
    
    def _create_advanced_mode(self) -> QWidget:
        """Create the advanced JSON editing mode widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # JSON Editor
        editor_group = QGroupBox("JSON Filter Editor")
        editor_layout = QVBoxLayout(editor_group)
        
        # Help text
        help_label = QLabel(
            "Enter MongoDB query filter in JSON format. Examples:\n"
            '• {"name": "John"} - Find documents where name equals "John"\n'
            '• {"age": {"$gt": 18}} - Find documents where age > 18\n'
            '• {"status": {"$in": ["active", "pending"]}} - Find documents with status in list'
        )
        help_label.setWordWrap(True)
        help_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        editor_layout.addWidget(help_label)
        
        # JSON editor
        self.json_editor = QTextEdit()
        self.json_editor.setPlaceholderText('{"field": "value"}')
        self.json_editor.setMinimumHeight(120)
        self.json_editor.setFont(QFont("Consolas", 10))
        self.json_editor.textChanged.connect(self._validate_json)
        
        # Setup syntax highlighter
        self.syntax_highlighter = JSONSyntaxHighlighter(self.json_editor.document())
        
        editor_layout.addWidget(self.json_editor)
        
        layout.addWidget(editor_group)
        layout.addStretch()
        
        return widget
    
    def _create_common_controls(self, parent_layout: QVBoxLayout) -> None:
        """Create common controls for both modes."""
        controls_group = QGroupBox("Query Settings")
        controls_layout = QFormLayout(controls_group)
        controls_layout.setSpacing(8)
        
        # Limit input
        limit_layout = QHBoxLayout()
        limit_layout.setSpacing(8)
        
        limit_label = QLabel("Limit:")
        limit_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        limit_label.setMinimumHeight(24)
        
        self.limit_spinbox = QSpinBox()
        self.limit_spinbox.setRange(1, 10000)
        self.limit_spinbox.setValue(100)
        self.limit_spinbox.setMinimumHeight(24)
        
        limit_layout.addWidget(limit_label)
        limit_layout.addWidget(self.limit_spinbox)
        limit_layout.addStretch()
        controls_layout.addRow("", limit_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        self.apply_btn = QPushButton(fa.icon('fa6s.play'), "Apply Filter")
        self.apply_btn.setStyleSheet(BUTTON_STYLES['dialog_primary'])
        self.apply_btn.setMinimumHeight(28)
        self.apply_btn.clicked.connect(self._apply_filter)
        
        self.reset_btn = QPushButton(fa.icon('fa6s.rotate'), "Reset Filter")
        self.reset_btn.setStyleSheet(BUTTON_STYLES['dialog_secondary'])
        self.reset_btn.setMinimumHeight(28)
        self.reset_btn.clicked.connect(self._reset_filter)
        
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addStretch()
        
        controls_layout.addRow("", button_layout)
        
        parent_layout.addWidget(controls_group)
    
    def _create_quick_templates(self, parent_layout: QVBoxLayout) -> None:
        """Create quick filter templates."""
        templates_group = QGroupBox("Quick Templates")
        templates_layout = QVBoxLayout(templates_group)
        templates_layout.setSpacing(8)
        
        # Template buttons
        templates_btn_layout = QHBoxLayout()
        
        # Find by ID template
        id_btn = QPushButton("Find by ID")
        id_btn.setStyleSheet(BUTTON_STYLES['dialog_neutral'])
        id_btn.setMinimumHeight(24)
        id_btn.clicked.connect(lambda: self._apply_template('{"_id": "document_id"}'))
        
        # Find by Date Range template
        date_btn = QPushButton("Find by Date Range")
        date_btn.setStyleSheet(BUTTON_STYLES['dialog_neutral'])
        date_btn.setMinimumHeight(24)
        date_btn.clicked.connect(lambda: self._apply_template('{"created_at": {"$gte": "2024-01-01", "$lte": "2024-12-31"}}'))
        
        # Find by Status template
        status_btn = QPushButton("Find by Status")
        status_btn.setStyleSheet(BUTTON_STYLES['dialog_neutral'])
        status_btn.setMinimumHeight(24)
        status_btn.clicked.connect(lambda: self._apply_template('{"status": "active"}'))
        
        # Find Empty Fields template
        empty_btn = QPushButton("Find Empty Fields")
        empty_btn.setStyleSheet(BUTTON_STYLES['dialog_neutral'])
        empty_btn.setMinimumHeight(24)
        empty_btn.clicked.connect(lambda: self._apply_template('{"field_name": {"$exists": true, "$in": [null, "", []]}}'))
        
        templates_btn_layout.addWidget(id_btn)
        templates_btn_layout.addWidget(date_btn)
        templates_btn_layout.addWidget(status_btn)
        templates_btn_layout.addWidget(empty_btn)
        templates_btn_layout.addStretch()
        
        templates_layout.addLayout(templates_btn_layout)
        parent_layout.addWidget(templates_group)
    
    def _setup_autocomplete(self) -> None:
        """Setup autocomplete for field names and values."""
        if self.field_combo:
            # Field name autocomplete
            self.field_combo.setCompleter(QCompleter(self.available_fields))
            
            # Connect field selection to value suggestions
            self.field_combo.currentTextChanged.connect(self._on_field_changed)
    
    def _on_field_changed(self, field_name: str) -> None:
        """Handle field selection change to update value suggestions."""
        if field_name and field_name in self.field_values_cache:
            # Update value input with suggestions
            values = self.field_values_cache[field_name]
            if values:
                # Create a completer for the values
                completer = QCompleter(values)
                self.value_input.setCompleter(completer)
    
    def _add_basic_filter(self) -> None:
        """Add a basic filter from the form."""
        field = self.field_combo.currentText().strip()
        operator = self.operator_combo.currentText()
        value = self.value_input.text().strip()
        
        if not field:
            QMessageBox.warning(self.widget, "Validation Error", "Please enter a field name.")
            return
        
        # Convert operator to MongoDB syntax
        mongo_operator = self._convert_operator_to_mongo(operator, value)
        
        # Create filter
        if mongo_operator:
            filter_dict = {field: mongo_operator}
            self.active_filters.append(filter_dict)
            self._update_active_filters_display()
            
            # Clear inputs
            self.value_input.clear()
            
            self.logger.info(f"Added basic filter: {field} {operator} {value}")
        else:
            QMessageBox.warning(self.widget, "Validation Error", f"Invalid operator combination: {operator}")
    
    def _convert_operator_to_mongo(self, operator: str, value: str) -> Any:
        """Convert human-readable operator to MongoDB syntax."""
        if operator == "equals":
            return value if value else None
        elif operator == "not equals":
            return {"$ne": value} if value else {"$ne": None}
        elif operator == "contains":
            return {"$regex": value, "$options": "i"} if value else None
        elif operator == "starts with":
            return {"$regex": f"^{value}", "$options": "i"} if value else None
        elif operator == "ends with":
            return {"$regex": f"{value}$", "$options": "i"} if value else None
        elif operator == "greater than":
            return {"$gt": float(value)} if value and value.replace('.', '').isdigit() else None
        elif operator == "less than":
            return {"$lt": float(value)} if value and value.replace('.', '').isdigit() else None
        elif operator == "greater than or equal":
            return {"$gte": float(value)} if value and value.replace('.', '').isdigit() else None
        elif operator == "less than or equal":
            return {"$lte": float(value)} if value and value.replace('.', '').isdigit() else None
        elif operator == "in list":
            if value:
                values = [v.strip() for v in value.split(',')]
                return {"$in": values}
            return None
        elif operator == "not in list":
            if value:
                values = [v.strip() for v in value.split(',')]
                return {"$nin": values}
            return None
        elif operator == "exists":
            return {"$exists": True}
        elif operator == "regex":
            return {"$regex": value, "$options": "i"} if value else None
        
        return None
    
    def _update_active_filters_display(self) -> None:
        """Update the display of active filters."""
        if not self.active_filters_frame:
            return
        
        # Clear existing widgets and layout
        for child in self.active_filters_frame.children():
            if isinstance(child, QWidget):
                child.deleteLater()
        
        # Get the existing layout or create a new one
        existing_layout = self.active_filters_frame.layout()
        if existing_layout:
            # Clear the existing layout
            while existing_layout.count():
                item = existing_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        else:
            # Create new layout if none exists
            existing_layout = QVBoxLayout(self.active_filters_frame)
            existing_layout.setSpacing(4)
        
        if not self.active_filters:
            no_filters_label = QLabel("No active filters")
            no_filters_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-style: italic;")
            existing_layout.addWidget(no_filters_label)
        else:
            for i, filter_dict in enumerate(self.active_filters):
                filter_widget = self._create_filter_item_widget(filter_dict, i)
                existing_layout.addWidget(filter_widget)
    
    def _create_filter_item_widget(self, filter_dict: Dict[str, Any], index: int) -> QWidget:
        """Create a widget to display a single filter item."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(8)
        
        # Filter text
        filter_text = json.dumps(filter_dict, indent=0)
        filter_label = QLabel(filter_text)
        filter_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-family: monospace;")
        layout.addWidget(filter_label)
        
        # Remove button
        remove_btn = QToolButton()
        remove_btn.setIcon(fa.icon('fa6s.xmark', color=COLORS['danger']))
        remove_btn.setToolTip("Remove filter")
        remove_btn.clicked.connect(lambda: self._remove_filter(index))
        layout.addWidget(remove_btn)
        
        layout.addStretch()
        return widget
    
    def _remove_filter(self, index: int) -> None:
        """Remove a filter at the specified index."""
        if 0 <= index < len(self.active_filters):
            removed_filter = self.active_filters.pop(index)
            self._update_active_filters_display()
            self.logger.info(f"Removed filter: {removed_filter}")
    
    def _validate_json(self) -> None:
        """Validate JSON input in advanced mode."""
        if not self.json_editor or not self.syntax_highlighter:
            return
        
        text = self.json_editor.toPlainText().strip()
        if not text:
            self.syntax_highlighter.clear_error()
            return
        
        try:
            json.loads(text)
            self.syntax_highlighter.clear_error()
        except json.JSONDecodeError as e:
            # Find the line with the error
            lines = text.split('\n')
            error_line = e.lineno - 1 if e.lineno > 0 else 0
            error_message = str(e)
            
            # Use a timer to prevent recursion
            QTimer.singleShot(0, lambda: self.syntax_highlighter.set_error(error_line, error_message))
    
    def _apply_template(self, template: str) -> None:
        """Apply a quick template filter."""
        if self.mode_tabs.currentIndex() == 1:  # Advanced mode
            if self.json_editor:
                self.json_editor.setPlainText(template)
        else:  # Basic mode
            # Parse template and add to basic filters
            try:
                filter_dict = json.loads(template)
                for field, value in filter_dict.items():
                    self.field_combo.setCurrentText(field)
                    if isinstance(value, dict):
                        # Handle complex operators
                        operator_text = self._get_operator_for_value(value)
                        self.operator_combo.setCurrentText(operator_text)
                        self.value_input.setText(str(value))
                    else:
                        self.operator_combo.setCurrentText("equals")
                        self.value_input.setText(str(value))
                    
                    self._add_basic_filter()
            except json.JSONDecodeError:
                QMessageBox.warning(self.widget, "Error", "Invalid template format")
    
    def _get_operator_for_value(self, value: Any) -> str:
        """Get the appropriate operator for a given value."""
        if isinstance(value, dict):
            if "$gt" in value:
                return "greater than"
            elif "$lt" in value:
                return "less than"
            elif "$gte" in value:
                return "greater than or equal"
            elif "$lte" in value:
                return "less than or equal"
            elif "$in" in value:
                return "in list"
            elif "$nin" in value:
                return "not in list"
            elif "$exists" in value:
                return "exists"
            elif "$regex" in value:
                return "regex"
        
        return "equals"
    
    def _apply_filter(self) -> None:
        """Apply the current filter."""
        if self.mode_tabs.currentIndex() == 0:  # Basic mode
            # Combine all active filters
            if self.active_filters:
                filter_json = json.dumps(self.active_filters[0] if len(self.active_filters) == 1 else {"$and": self.active_filters})
            else:
                filter_json = "{}"  # Empty filter as empty JSON object
        else:  # Advanced mode
            filter_json = self.json_editor.toPlainText().strip()
            if not filter_json:
                filter_json = "{}"  # Empty filter as empty JSON object
        
        limit = self.limit_spinbox.value() if self.limit_spinbox else 100
        
        # Validate JSON if not empty
        if filter_json and filter_json != "{}":
            try:
                json.loads(filter_json)
            except json.JSONDecodeError:
                QMessageBox.warning(self.widget, "Validation Error", "Invalid JSON format in filter.")
                return
        
        # Log the filter being applied
        if filter_json == "{}":
            self.logger.info("[FILTER] Applied filter: {} (no filters)")
        else:
            self.logger.info(f"[FILTER] Applied filter: {filter_json}")
        
        self.filter_applied.emit(filter_json, limit)
    
    def _reset_filter(self) -> None:
        """Reset all filters to default state."""
        # Clear basic filters
        self.active_filters.clear()
        self._update_active_filters_display()
        
        # Clear advanced JSON
        if self.json_editor:
            self.json_editor.clear()
        
        # Clear field inputs
        if self.field_combo:
            self.field_combo.setCurrentText("")
        if self.value_input:
            self.value_input.clear()
        
        # Reset limit
        if self.limit_spinbox:
            self.limit_spinbox.setValue(100)
        
        self.logger.info("[FILTER] Reset to default view")
        self.filter_reset.emit()
    
    def set_available_fields(self, fields: List[str]) -> None:
        """Set the available fields for autocomplete."""
        self.available_fields = fields
        if self.field_combo:
            self.field_combo.clear()
            self.field_combo.addItems(fields)
            self._setup_autocomplete()
    
    def set_field_values_cache(self, field_values: Dict[str, List[str]]) -> None:
        """Set cached field values for suggestions."""
        self.field_values_cache = field_values
    
    def get_widget(self) -> QWidget | None:
        """Get the filter panel widget."""
        return self.widget
    
    def get_current_filter(self) -> str:
        """Get the current filter JSON string."""
        if self.mode_tabs.currentIndex() == 0:  # Basic mode
            if self.active_filters:
                return json.dumps(self.active_filters[0] if len(self.active_filters) == 1 else {"$and": self.active_filters})
            return ""
        else:  # Advanced mode
            return self.json_editor.toPlainText().strip() if self.json_editor else ""
    
    def get_current_limit(self) -> int:
        """Get the current limit value."""
        return self.limit_spinbox.value() if self.limit_spinbox else 100
    
    def set_filter(self, filter_json: str) -> None:
        """Set the filter JSON string."""
        if self.mode_tabs.currentIndex() == 0:  # Basic mode
            # Parse JSON and convert to basic filters
            try:
                filter_dict = json.loads(filter_json)
                self.active_filters = [filter_dict]
                self._update_active_filters_display()
            except json.JSONDecodeError:
                self.logger.warning(f"Invalid JSON filter: {filter_json}")
        else:  # Advanced mode
            if self.json_editor:
                self.json_editor.setPlainText(filter_json)
    
    def set_limit(self, limit: int) -> None:
        """Set the limit value."""
        if self.limit_spinbox:
            self.limit_spinbox.setValue(limit)
    
    def enable_filtering(self, enabled: bool = True) -> None:
        """Enable or disable filter controls."""
        if self.field_combo:
            self.field_combo.setEnabled(enabled)
        if self.operator_combo:
            self.operator_combo.setEnabled(enabled)
        if self.value_input:
            self.value_input.setEnabled(enabled)
        if self.json_editor:
            self.json_editor.setEnabled(enabled)
        if self.apply_btn:
            self.apply_btn.setEnabled(enabled)
        if self.reset_btn:
            self.reset_btn.setEnabled(enabled)
