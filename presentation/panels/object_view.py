"""
Object View Component
Handles the display of MongoDB documents with always-visible, editable JSON content.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

import qtawesome as fa
from PySide6.QtCore import QObject, Qt, Signal, QTimer
from PySide6.QtGui import QAction, QColor, QFont, QTextCharFormat, QTextCursor, QSyntaxHighlighter
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QMenu, QPushButton, QScrollArea, QSizePolicy,
    QTextEdit, QVBoxLayout, QWidget, QToolTip
)

# Import styles at module level
from ..styles.styles import BUTTON_STYLES


class MongoDBJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for MongoDB documents with ObjectId and other special types."""
    
    def default(self, obj: Any) -> Any:
        """Handle MongoDB-specific types that aren't JSON serializable."""
        try:
            # Handle ObjectId (convert to string)
            if hasattr(obj, '__str__'):
                return str(obj)
            # Handle datetime objects
            elif isinstance(obj, (datetime, date)):
                return obj.isoformat()
            # Handle Decimal objects
            elif isinstance(obj, Decimal):
                return float(obj)
            # Handle other non-serializable objects
            else:
                return str(obj)
        except Exception:
            return str(obj)


def safe_json_dumps(obj: Any, **kwargs: Any) -> str:
    """Safely convert MongoDB documents to JSON string."""
    try:
        return json.dumps(obj, cls=MongoDBJSONEncoder, **kwargs)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"JSON serialization failed, using fallback: {e}")
        # Fallback: convert to string representation
        return str(obj)


class JSONEditor(QTextEdit):
    """Custom JSON editor with real-time validation and error highlighting."""
    
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.syntax_highlighter: JSONSyntaxHighlighter | None = None
        self.is_valid: bool = True
        self.error_message: str = ""
        self.error_line: Optional[int] = None
        self.validation_timer: QTimer | None = None
        self._validation_in_progress: bool = False
        self._setup_editor()
    
    def _setup_editor(self) -> None:
        """Setup the JSON editor with syntax highlighting and validation."""
        # Apply syntax highlighting
        self.syntax_highlighter = JSONSyntaxHighlighter(self.document())
        
        # Setup debounced validation timer
        self.validation_timer = QTimer()
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self._validate_json)
        
        # Connect text changes for debounced validation
        self.textChanged.connect(self._schedule_validation)
        
        # Enable tooltips
        self.setMouseTracking(True)
    
    def _schedule_validation(self) -> None:
        """Schedule validation with debouncing."""
        if self.validation_timer:
            self.validation_timer.stop()
            self.validation_timer.start(500)  # 500ms debounce delay
    
    def _validate_json(self) -> None:
        """Validate JSON content with debouncing."""
        # Prevent recursive validation
        if self._validation_in_progress:
            return
        
        self._validation_in_progress = True
        
        try:
            import json
            
            text = self.toPlainText().strip()
            
            if not text:
                # Empty content is considered valid
                self._clear_error()
                return
            
            try:
                json.loads(text)
                # JSON is valid
                self._clear_error()
            except json.JSONDecodeError as e:
                # JSON is invalid - highlight the error
                self._set_error(e)
        finally:
            self._validation_in_progress = False
    
    def _set_error(self, error: json.JSONDecodeError) -> None:
        """Set error state and highlight the problematic line."""
        self.is_valid = False
        self.error_message = self._format_error_message(error)
        self.error_line = error.lineno - 1  # Convert to 0-based indexing
        
        if self.syntax_highlighter:
            self.syntax_highlighter.set_error(self.error_line, self.error_message)
        
        # Log the validation error (only once per error state)
        if not hasattr(self, '_last_error_message') or self._last_error_message != self.error_message:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"JSON validation error: {self.error_message}")
            self._last_error_message = self.error_message
    
    def _clear_error(self) -> None:
        """Clear error state and highlighting."""
        if not self.is_valid:
            self.is_valid = True
            self.error_message = ""
            self.error_line = None
            
            if self.syntax_highlighter:
                self.syntax_highlighter.clear_error()
            
            # Log successful validation (only when transitioning from error to valid)
            if hasattr(self, '_last_error_message') and self._last_error_message:
                import logging
                logger = logging.getLogger(__name__)
                logger.info("JSON validation passed")
                self._last_error_message = ""
    
    def _format_error_message(self, error: json.JSONDecodeError) -> str:
        """Format JSON error message in a user-friendly way."""
        message = str(error.msg)
        
        # Make error messages more user-friendly
        if "Expecting property name enclosed in double quotes" in message:
            return "Missing quotes around property name"
        elif "Expecting ',' delimiter" in message:
            return "Missing comma between properties"
        elif "Expecting value" in message:
            return "Missing value after colon"
        elif "Extra data" in message:
            return "Extra characters after JSON end"
        elif "Invalid control character" in message:
            return "Invalid control character in string"
        elif "Invalid \\escape" in message:
            return "Invalid escape sequence"
        elif "Unterminated string" in message:
            return "Unterminated string (missing closing quote)"
        
        return message
    
    def mouseMoveEvent(self, event) -> None:
        """Show tooltip with error message when hovering over error line."""
        super().mouseMoveEvent(event)
        
        if not self.is_valid and self.error_line is not None:
            cursor = self.cursorForPosition(event.pos())
            current_line = cursor.blockNumber()
            
            if current_line == self.error_line:
                # Show tooltip with error message
                QToolTip.showText(
                    event.globalPos(),
                    f"⚠️ {self.error_message}",
                    self,
                    self.rect(),
                    3000  # Show for 3 seconds
                )
            else:
                                 QToolTip.hideText()
    
    def closeEvent(self, event) -> None:
        """Clean up validation timer when editor is closed."""
        if self.validation_timer:
            self.validation_timer.stop()
        super().closeEvent(event)


class JSONSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for JSON text with real-time validation."""
    
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._setup_formats()
        self.error_line: Optional[int] = None
        self.error_message: str = ""
    
    def _setup_formats(self) -> None:
        """Setup text formats for different JSON elements."""
        # String format
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#22863a"))
        self.string_format.setFontWeight(QFont.Bold)
        
        # Number format
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#005cc5"))
        
        # Boolean format
        self.boolean_format = QTextCharFormat()
        self.boolean_format.setForeground(QColor("#d73a49"))
        self.boolean_format.setFontWeight(QFont.Bold)
        
        # Null format
        self.null_format = QTextCharFormat()
        self.null_format.setForeground(QColor("#6f42c1"))
        self.null_format.setFontWeight(QFont.Bold)
        
        # Key format
        self.key_format = QTextCharFormat()
        self.key_format.setForeground(QColor("#24292e"))
        self.key_format.setFontWeight(QFont.Bold)
        
        # Error format
        self.error_format = QTextCharFormat()
        self.error_format.setBackground(QColor("#fef2f2"))  # Light red background
        self.error_format.setUnderlineColor(QColor("#dc2626"))  # Red underline
        self.error_format.setUnderlineStyle(QTextCharFormat.SingleUnderline)
        
        # Base format
        self.base_format = QTextCharFormat()
    
    def set_error(self, line: Optional[int], message: str) -> None:
        """Set error information for highlighting."""
        self.error_line = line
        self.error_message = message
        self.rehighlight()
    
    def clear_error(self) -> None:
        """Clear error highlighting."""
        self.error_line = None
        self.error_message = ""
        self.rehighlight()
    
    def highlightBlock(self, text: str) -> None:
        """Highlight a block of text."""
        import re
        
        # Reset format for the entire block
        self.setFormat(0, len(text), self.base_format)
        
        # Highlight error line if this block contains the error
        current_line = self.currentBlock().blockNumber()
        if self.error_line is not None and current_line == self.error_line:
            self.setFormat(0, len(text), self.error_format)
        
        # Highlight keys (strings that are followed by a colon)
        key_pattern = r'"[^"]*":'
        for match in re.finditer(key_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.key_format)
        
        # Highlight string values (strings that are NOT followed by a colon)
        string_pattern = r'"[^"]*"(?!\s*:)'
        for match in re.finditer(string_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.string_format)
        
        # Highlight numbers
        number_pattern = r'\b\d+\.?\d*\b'
        for match in re.finditer(number_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.number_format)
        
        # Highlight booleans
        boolean_pattern = r'\b(true|false)\b'
        for match in re.finditer(boolean_pattern, text, re.IGNORECASE):
            self.setFormat(match.start(), match.end() - match.start(), self.boolean_format)
        
        # Highlight null
        null_pattern = r'\bnull\b'
        for match in re.finditer(null_pattern, text, re.IGNORECASE):
            self.setFormat(match.start(), match.end() - match.start(), self.null_format)


class DocumentWidget(QFrame):
    """Document widget with always-visible, editable JSON content."""
    
    # Signals
    document_selected = Signal(int)  # Emits document index
    json_edited = Signal(int)  # Emits document index when JSON is edited
    json_saved = Signal(int)  # Emits document index when JSON is saved
    json_cancelled = Signal(int)  # Emits document index when JSON editing is cancelled
    
    def __init__(self, document: Dict[str, Any], index: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.document = document
        self.index = index
        self.json_editor: JSONEditor | None = None
        self.original_json: str = ""
        self.is_modified: bool = False
        self.save_button: QPushButton | None = None
        self.cancel_button: QPushButton | None = None
        self.action_buttons_layout: QHBoxLayout | None = None
        self._create_widget()
    
    def _create_widget(self) -> None:
        """Create the document widget."""
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                background-color: #ffffff;
                margin: 4px;
            }
            QFrame:hover {
                border-color: #3b82f6;
                border-width: 2px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # JSON editor area (no header, no labels)
        self._create_json_area(layout)
    

    
    def _create_json_area(self, parent_layout: QVBoxLayout) -> None:
        """Create the JSON editor area."""
        # Create a container for the JSON editor and action buttons
        json_container = QWidget()
        json_layout = QVBoxLayout(json_container)
        json_layout.setSpacing(8)
        json_layout.setContentsMargins(0, 0, 0, 0)
        
        # JSON editor with real-time validation
        self.json_editor = JSONEditor()
        self.json_editor.setFont(QFont("Consolas", 10))
        self.json_editor.setMinimumHeight(150)
        self.json_editor.setMaximumHeight(300)
        self.json_editor.setStyleSheet("""
            QTextEdit {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background-color: #f8f9fa;
                color: #374151;
                padding: 12px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 10px;
                line-height: 1.4;
            }
            QTextEdit:focus {
                border-color: #3b82f6;
                outline: none;
                background-color: #ffffff;
            }
        """)
        
        # Connect text changes for editing detection
        self.json_editor.textChanged.connect(self._on_json_text_changed)
        
        json_layout.addWidget(self.json_editor)
        
        # Action buttons layout (initially hidden)
        self.action_buttons_layout = QHBoxLayout()
        self.action_buttons_layout.setSpacing(8)
        self.action_buttons_layout.addStretch()
        
        # Cancel button (red full background)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setIcon(fa.icon('fa6s.xmark', color='#ffffff'))
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        self.cancel_button.clicked.connect(self._cancel_editing)
        self.cancel_button.setVisible(False)
        self.action_buttons_layout.addWidget(self.cancel_button)
        
        # Save button (green border style)
        self.save_button = QPushButton("Save")
        self.save_button.setIcon(fa.icon('fa6s.check', color='#10b981'))
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #10b981;
                border: 2px solid #10b981;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #10b981;
                color: white;
            }
        """)
        self.save_button.clicked.connect(self._save_editing)
        self.save_button.setVisible(False)
        self.action_buttons_layout.addWidget(self.save_button)
        
        json_layout.addLayout(self.action_buttons_layout)
        
        parent_layout.addWidget(json_container)
        
        # Load initial JSON content
        self._load_json_content()
    
    def _load_json_content(self) -> None:
        """Load JSON content into the editor with automatic formatting."""
        if not self.json_editor:
            return
        
        try:
            # Format JSON with proper indentation (2 spaces) for readability
            json_text = safe_json_dumps(self.document, indent=2, ensure_ascii=False, sort_keys=True)
            self.original_json = json_text
            self.json_editor.setPlainText(json_text)
            
            # Move cursor to beginning
            cursor = self.json_editor.textCursor()
            cursor.movePosition(QTextCursor.Start)
            self.json_editor.setTextCursor(cursor)
            
            # Reset modification state
            self.is_modified = False
            self._update_action_buttons_visibility()
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error formatting JSON for document {self.index}: {e}")
            self.json_editor.setPlainText(str(self.document))
            self.original_json = str(self.document)
    
    def _on_json_text_changed(self) -> None:
        """Handle JSON text changes."""
        import logging
        logger = logging.getLogger(__name__)
        
        # Check if content has changed from original
        current_text = self.json_editor.toPlainText()
        self.is_modified = (current_text != self.original_json)
        
        if self.is_modified:
            logger.info(f"User started editing document {self.index}")
            self.json_edited.emit(self.index)
        
        self._update_action_buttons_visibility()
    
    def _update_action_buttons_visibility(self) -> None:
        """Update the visibility of action buttons based on modification state and validation."""
        if self.save_button and self.cancel_button:
            # Cancel button is always enabled when modified
            self.cancel_button.setVisible(self.is_modified)
            
            # Save button is only enabled when modified AND valid
            is_valid = self.json_editor.is_valid if self.json_editor else True
            self.save_button.setVisible(self.is_modified and is_valid)
            
            # Update save button tooltip based on validation state
            if self.is_modified and not is_valid:
                self.save_button.setToolTip("Fix JSON errors before saving.")
            else:
                self.save_button.setToolTip("")
    
    def _save_editing(self) -> None:
        """Save the edited JSON content."""
        import logging
        logger = logging.getLogger(__name__)
        
        # Check if JSON is valid before saving
        if not self.json_editor.is_valid:
            logger.warning(f"User attempted to save invalid JSON for document {self.index}")
            return
        
        try:
            # Parse JSON (should be valid at this point)
            import json
            current_text = self.json_editor.toPlainText()
            parsed_json = json.loads(current_text)
            
            # Update the original JSON and document
            self.original_json = current_text
            self.document = parsed_json
            self.is_modified = False
            self._update_action_buttons_visibility()
            
            # Emit save signal
            self.json_saved.emit(self.index)
            
            # Show toast notification
            from ..dialogs.toast_notification import ToastManager
            toast_manager = ToastManager()
            toast_manager.show_success("Document saved successfully.", self.parent())
            
            logger.info(f"User saved document {self.index}")
            
        except Exception as e:
            # Show general error
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Error saving document: {str(e)}")
            logger.error(f"Error saving document {self.index}: {str(e)}")
    
    def _cancel_editing(self) -> None:
        """Cancel editing and restore original JSON."""
        import logging
        logger = logging.getLogger(__name__)
        
        # Restore original JSON
        self.json_editor.setPlainText(self.original_json)
        self.is_modified = False
        self._update_action_buttons_visibility()
        
        # Emit cancel signal
        self.json_cancelled.emit(self.index)
        
        logger.info(f"User cancelled editing document {self.index}")
        
        # Note: No toast notification on cancel as per requirements
    

    
    def get_edited_json(self) -> Optional[Dict[str, Any]]:
        """Get the edited JSON from the editor."""
        import json
        try:
            json_text = self.json_editor.toPlainText()
            if json_text.strip():
                return json.loads(json_text)
        except json.JSONDecodeError:
            pass
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error parsing edited JSON: {e}")
        return None


class ObjectView(QObject):
    """Object view component for displaying MongoDB documents with always-visible JSON."""
    
    # Signals
    document_selected = Signal(dict)  # Emits selected document
    refresh_requested = Signal()
    
    # Document context menu signals
    view_document_requested = Signal(dict)  # Emits selected document
    edit_document_requested = Signal(dict)  # Emits selected document
    delete_document_requested = Signal(dict)  # Emits selected document
    
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.parent = parent
        self.widget: QWidget | None = None
        self.collection_label: QLabel | None = None
        self.doc_count_label: QLabel | None = None
        self.documents_data: List[Dict[str, Any]] = []  # Store the actual document data
        self.document_widgets: List[DocumentWidget] = []
        self.scroll_area: QScrollArea | None = None
        self.scroll_content: QWidget | None = None
        self.loading_indicator: QLabel | None = None
        self._create_object_view()
    
    def _create_object_view(self) -> None:
        """Create the object view widget."""
        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)
        layout.setSpacing(8)
        layout.setContentsMargins(4, 4, 4, 4)
        
        self._create_info_header(layout)
        self._create_documents_area(layout)
    
    def _create_info_header(self, parent_layout: QVBoxLayout) -> None:
        """Create the information header with collection details."""
        info_layout = QHBoxLayout()
        info_layout.setSpacing(8)
        
        # Collection label
        self.collection_label = QLabel("Collection: None selected")
        self.collection_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.collection_label.setMinimumHeight(24)
        
        # Document count label
        self.doc_count_label = QLabel("Documents: 0")
        self.doc_count_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.doc_count_label.setMinimumHeight(24)
        
        # Loading indicator
        self.loading_indicator = QLabel()
        self.loading_indicator.setVisible(False)
        self.loading_indicator.setPixmap(fa.icon('fa6s.spinner', color='#3b82f6').pixmap(16, 16))
        self.loading_indicator.setStyleSheet("margin-left: 8px;")
        
        info_layout.addWidget(self.collection_label)
        info_layout.addWidget(self.doc_count_label)
        info_layout.addWidget(self.loading_indicator)
        info_layout.addStretch()
        
        # Refresh documents button
        refresh_docs_button = QPushButton("Refresh Documents")
        refresh_docs_button.setIcon(fa.icon('fa6s.arrows-rotate', color='#ffffff'))  # White icon for contrast
        refresh_docs_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        refresh_docs_button.setMinimumHeight(28)
        refresh_docs_button.setStyleSheet(BUTTON_STYLES['refresh_primary'])  # Use primary refresh style
        refresh_docs_button.clicked.connect(self._on_refresh_clicked)
        info_layout.addWidget(refresh_docs_button)
        
        parent_layout.addLayout(info_layout)
    
    def _on_refresh_clicked(self):
        """Handle refresh button click with logging."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info("[UI] Refresh button clicked")
        self.refresh_requested.emit()
    
    def _create_documents_area(self, parent_layout: QVBoxLayout) -> None:
        """Create the scrollable documents area."""
        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                background-color: #f9fafb;
            }
        """)
        
        # Create content widget for scroll area
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(4)
        self.scroll_layout.setContentsMargins(8, 8, 8, 8)
        self.scroll_layout.addStretch()  # Add stretch to push content to top
        
        # Set content widget for scroll area
        self.scroll_area.setWidget(self.scroll_content)
        
        parent_layout.addWidget(self.scroll_area)
    
    def _on_document_selected(self, index: int) -> None:
        """Handle document selection."""
        # Emit document selected signal
        if 0 <= index < len(self.documents_data):
            self.document_selected.emit(self.documents_data[index])
    
    def _on_json_edited(self, index: int) -> None:
        """Handle JSON editing."""
        # This can be used for tracking edits or triggering save operations
        pass
    
    def _on_json_saved(self, index: int) -> None:
        """Handle JSON save."""
        # This can be used for tracking saves or triggering database operations
        pass
    
    def _on_json_cancelled(self, index: int) -> None:
        """Handle JSON cancel."""
        # This can be used for tracking cancellations
        pass
    
    def get_widget(self) -> QWidget | None:
        """Get the object view widget."""
        return self.widget
    
    def clear_tree(self) -> None:
        """Clear the documents list."""
        self._clear_document_widgets()
        self.documents_data = []
    
    def _clear_document_widgets(self) -> None:
        """Clear all document widgets."""
        for widget in self.document_widgets:
            if widget:
                widget.deleteLater()
        self.document_widgets.clear()
        
        # Clear the layout (keep the stretch)
        while self.scroll_layout.count() > 1:  # Keep the stretch at the end
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def set_collection_info(self, collection_name: str, document_count: int) -> None:
        """Set collection information in the header."""
        if self.collection_label:
            self.collection_label.setText(f"Collection: {collection_name}")
        
        if self.doc_count_label:
            self.doc_count_label.setText(f"Documents: {document_count}")
    
    def populate_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Populate the documents area with document widgets."""
        import logging
        logger = logging.getLogger(__name__)
        
        if not self.scroll_layout:
            logger.error("Scroll layout not initialized")
            return
        
        logger.debug(f"Populating documents area with {len(documents) if documents else 0} documents")
        
        # Store the document data for later use
        self.documents_data = documents if documents else []
        
        # Clear existing widgets
        self._clear_document_widgets()
        
        if not documents:
            # Show empty state
            empty_label = QLabel("No documents found")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("""
                QLabel {
                    color: #6b7280;
                    font-style: italic;
                    padding: 20px;
                    font-size: 14px;
                }
            """)
            self.scroll_layout.insertWidget(0, empty_label)
            logger.debug("Showing empty state for collection")
            return
        
        # Create document widgets (lazy loading will be handled by scroll area)
        for index, doc in enumerate(documents):
            if not isinstance(doc, dict):
                logger.warning(f"Skipping non-dict document at index {index}")
                continue
            
            # Create document widget
            doc_widget = DocumentWidget(doc, index, self.scroll_content)
            doc_widget.document_selected.connect(self._on_document_selected)
            doc_widget.json_edited.connect(self._on_json_edited)
            doc_widget.json_saved.connect(self._on_json_saved)
            doc_widget.json_cancelled.connect(self._on_json_cancelled)
            
            # Add to layout (before the stretch)
            self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, doc_widget)
            self.document_widgets.append(doc_widget)
        
        logger.debug(f"Successfully populated documents area with {len(documents)} documents")
    
    def get_document_by_index(self, index: int) -> Optional[Dict[str, Any]]:
        """Get document data by index."""
        if 0 <= index < len(self.documents_data):
            return self.documents_data[index]
        return None
    
    def get_selected_document(self) -> Optional[Dict[str, Any]]:
        """Get the currently selected document."""
        # Since we removed the selection mechanism, return None for now
        # This can be enhanced if needed for specific use cases
        return None
    
    def get_edited_json(self) -> Optional[Dict[str, Any]]:
        """Get the edited JSON from the first document widget (for compatibility)."""
        if self.document_widgets:
            return self.document_widgets[0].get_edited_json()
        return None
    
    def set_loading_state(self, loading: bool) -> None:
        """Set the loading state for the object view."""
        if self.loading_indicator:
            self.loading_indicator.setVisible(loading)
    
    def set_error_state(self, error_message: str) -> None:
        """Set the error state for the object view."""
        if self.loading_indicator:
            self.loading_indicator.setVisible(False)
        
        self.doc_count_label.setText("Error loading documents")
        self.doc_count_label.setStyleSheet("color: #dc3545; font-weight: bold;")
