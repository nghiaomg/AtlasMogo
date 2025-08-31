"""
Object View Component
Handles the display of MongoDB documents in a tree-like JSON editor format.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLabel, QPushButton, QHeaderView, QSizePolicy, QMenu, QSplitter,
    QTextEdit, QFrame, QScrollArea
)
from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QFont, QAction, QTextCursor, QSyntaxHighlighter, QTextCharFormat, QColor
import json
import qtawesome as fa
from typing import Dict, Any, List, Optional


class JSONSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for JSON text."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_formats()
    
    def _setup_formats(self):
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
    
    def highlightBlock(self, text):
        """Highlight a block of text."""
        import re
        
        # Highlight strings
        string_pattern = r'"[^"]*"'
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


class ObjectView(QObject):
    """Object view component for displaying MongoDB documents in tree format."""
    
    # Signals
    document_selected = Signal(dict)  # Emits selected document
    refresh_requested = Signal()
    
    # Document context menu signals
    view_document_requested = Signal(dict)  # Emits selected document
    edit_document_requested = Signal(dict)  # Emits selected document
    delete_document_requested = Signal(dict)  # Emits selected document
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.widget = None
        self.documents_tree = None
        self.json_editor = None
        self.collection_label = None
        self.doc_count_label = None
        self.documents_data = []  # Store the actual document data
        self.current_document_index = -1
        self._create_object_view()
    
    def _create_object_view(self):
        """Create the object view widget."""
        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)
        layout.setSpacing(8)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Collection info header
        self._create_info_header(layout)
        
        # Create splitter for tree and JSON editor
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        
        # Documents tree
        self._create_documents_tree(splitter)
        
        # JSON editor
        self._create_json_editor(splitter)
        
        # Set splitter proportions (60% tree, 40% editor)
        splitter.setSizes([600, 400])
        
        layout.addWidget(splitter)
    
    def _create_info_header(self, parent_layout):
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
        
        info_layout.addWidget(self.collection_label)
        info_layout.addWidget(self.doc_count_label)
        info_layout.addStretch()
        
        # Refresh documents button
        refresh_docs_button = QPushButton("Refresh Documents")
        refresh_docs_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        refresh_docs_button.setMinimumHeight(28)
        refresh_docs_button.clicked.connect(self.refresh_requested.emit)
        info_layout.addWidget(refresh_docs_button)
        
        parent_layout.addLayout(info_layout)
    
    def _create_documents_tree(self, parent):
        """Create the documents tree widget."""
        # Create frame for tree
        tree_frame = QFrame()
        tree_frame.setFrameStyle(QFrame.StyledPanel)
        tree_layout = QVBoxLayout(tree_frame)
        tree_layout.setContentsMargins(8, 8, 8, 8)
        
        # Tree label
        tree_label = QLabel("Documents")
        tree_label.setFont(QFont("Arial", 12, QFont.Bold))
        tree_layout.addWidget(tree_label)
        
        # Documents tree
        self.documents_tree = QTreeWidget()
        self.documents_tree.setHeaderLabel("Document Structure")
        self.documents_tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.documents_tree.setMinimumHeight(300)
        
        # Import and apply tree styles
        from ..styles.styles import SIDEBAR_TREE_STYLE
        self.documents_tree.setStyleSheet(SIDEBAR_TREE_STYLE)
        
        # Enable sorting
        self.documents_tree.setSortingEnabled(True)
        
        # Set selection behavior
        self.documents_tree.setSelectionBehavior(QTreeWidget.SelectRows)
        self.documents_tree.setSelectionMode(QTreeWidget.SingleSelection)
        
        # Connect selection change
        self.documents_tree.itemSelectionChanged.connect(self._on_tree_selection_changed)
        
        # Enable context menu for right-click actions
        self.documents_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.documents_tree.customContextMenuRequested.connect(self._show_context_menu)
        
        tree_layout.addWidget(self.documents_tree)
        parent.addWidget(tree_frame)
    
    def _create_json_editor(self, parent):
        """Create the JSON editor widget."""
        # Create frame for JSON editor
        editor_frame = QFrame()
        editor_frame.setFrameStyle(QFrame.StyledPanel)
        editor_layout = QVBoxLayout(editor_frame)
        editor_layout.setContentsMargins(8, 8, 8, 8)
        
        # Editor label
        editor_label = QLabel("JSON Editor")
        editor_label.setFont(QFont("Arial", 12, QFont.Bold))
        editor_layout.addWidget(editor_label)
        
        # JSON editor
        self.json_editor = QTextEdit()
        self.json_editor.setFont(QFont("Consolas", 10))
        self.json_editor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.json_editor.setMinimumHeight(300)
        self.json_editor.setPlaceholderText("Select a document to view/edit JSON...")
        
        # Apply syntax highlighting
        self.syntax_highlighter = JSONSyntaxHighlighter(self.json_editor.document())
        
        # Import and apply editor styles
        from ..styles.styles import COLORS
        self.json_editor.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {COLORS['border_light']};
                border-radius: 4px;
                background-color: {COLORS['bg_primary']};
                color: {COLORS['text_primary']};
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10px;
                line-height: 1.4;
            }}
            QTextEdit:focus {{
                border-color: {COLORS['primary']};
                outline: none;
            }}
        """)
        
        # Connect text changes for validation
        self.json_editor.textChanged.connect(self._on_json_text_changed)
        
        editor_layout.addWidget(self.json_editor)
        parent.addWidget(editor_frame)
    
    def _on_tree_selection_changed(self):
        """Handle tree selection changes."""
        current_item = self.documents_tree.currentItem()
        if current_item and hasattr(current_item, 'document_index'):
            self.current_document_index = current_item.document_index
            self._update_json_editor()
    
    def _on_json_text_changed(self):
        """Handle JSON editor text changes."""
        # TODO: Add real-time JSON validation
        pass
    
    def get_widget(self):
        """Get the object view widget."""
        return self.widget
    
    def get_tree_widget(self):
        """Get the documents tree widget."""
        return self.documents_tree
    
    def clear_tree(self):
        """Clear the documents tree."""
        if self.documents_tree:
            self.documents_tree.clear()
            self.json_editor.clear()
            self.current_document_index = -1
    
    def set_collection_info(self, collection_name: str, document_count: int):
        """Set collection information in the header."""
        if self.collection_label:
            self.collection_label.setText(f"Collection: {collection_name}")
        
        if self.doc_count_label:
            self.doc_count_label.setText(f"Documents: {document_count}")
    
    def populate_documents(self, documents: List[Dict[str, Any]]):
        """Populate the tree with documents."""
        import logging
        logger = logging.getLogger(__name__)
        
        if not self.documents_tree:
            logger.error("Documents tree widget not initialized")
            return
        
        logger.debug(f"Populating tree with {len(documents) if documents else 0} documents")
        
        # Store the document data for later use
        self.documents_data = documents if documents else []
        
        # Clear existing data
        self.documents_tree.clear()
        self.json_editor.clear()
        self.current_document_index = -1
        
        if not documents:
            # Show empty state
            empty_item = QTreeWidgetItem(self.documents_tree)
            empty_item.setText(0, "No documents found in this collection")
            empty_item.setFlags(Qt.ItemIsEnabled)  # Make it non-selectable
            logger.debug("Showing empty state for collection")
            return
        
        # Populate tree with documents
        for index, doc in enumerate(documents):
            if not isinstance(doc, dict):
                logger.warning(f"Skipping non-dict document at index {index}")
                continue
            
            # Create root item for document
            doc_item = QTreeWidgetItem(self.documents_tree)
            doc_item.setText(0, f"Document {index + 1}")
            doc_item.document_index = index
            
            # Add document fields as child items
            self._add_document_fields(doc_item, doc)
            
            # Expand the document item
            doc_item.setExpanded(True)
        
        logger.debug(f"Successfully populated tree with {len(documents)} documents")
    
    def _add_document_fields(self, parent_item: QTreeWidgetItem, data: Any, path: str = ""):
        """Recursively add document fields to the tree."""
        if isinstance(data, dict):
            for key, value in data.items():
                field_path = f"{path}.{key}" if path else key
                field_item = QTreeWidgetItem(parent_item)
                field_item.setText(0, key)
                
                if isinstance(value, (dict, list)):
                    # For complex types, show type and add children
                    field_item.setText(1, f"({type(value).__name__})")
                    self._add_document_fields(field_item, value, field_path)
                else:
                    # For simple types, show the value
                    field_item.setText(1, str(value))
        
        elif isinstance(data, list):
            for index, item in enumerate(data):
                field_path = f"{path}[{index}]"
                field_item = QTreeWidgetItem(parent_item)
                field_item.setText(0, f"[{index}]")
                
                if isinstance(item, (dict, list)):
                    # For complex types, show type and add children
                    field_item.setText(1, f"({type(item).__name__})")
                    self._add_document_fields(field_item, item, field_path)
                else:
                    # For simple types, show the value
                    field_item.setText(1, str(item))
    
    def _update_json_editor(self):
        """Update the JSON editor with the selected document."""
        if 0 <= self.current_document_index < len(self.documents_data):
            document = self.documents_data[self.current_document_index]
            try:
                # Format JSON with proper indentation
                json_text = json.dumps(document, indent=2, ensure_ascii=False)
                self.json_editor.setPlainText(json_text)
                
                # Move cursor to beginning
                cursor = self.json_editor.textCursor()
                cursor.movePosition(QTextCursor.Start)
                self.json_editor.setTextCursor(cursor)
                
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error formatting JSON: {e}")
                self.json_editor.setPlainText(str(document))
        else:
            self.json_editor.clear()
    
    def get_document_by_index(self, index: int) -> Optional[Dict[str, Any]]:
        """Get document data by index."""
        if 0 <= index < len(self.documents_data):
            return self.documents_data[index]
        return None
    
    def get_selected_document(self) -> Optional[Dict[str, Any]]:
        """Get the currently selected document."""
        if self.current_document_index >= 0:
            return self.get_document_by_index(self.current_document_index)
        return None
    
    def get_edited_json(self) -> Optional[Dict[str, Any]]:
        """Get the edited JSON from the editor."""
        try:
            json_text = self.json_editor.toPlainText()
            if json_text.strip():
                return json.loads(json_text)
        except json.JSONDecodeError:
            pass
        return None
    
    def set_loading_state(self, loading: bool):
        """Set the loading state for the object view."""
        if loading:
            self.doc_count_label.setText("Loading documents...")
            self.doc_count_label.setStyleSheet("color: #007bff; font-weight: bold;")
        else:
            self.doc_count_label.setStyleSheet("color: #6c757d; font-size: 11px;")
    
    def set_error_state(self, error_message: str):
        """Set the error state for the object view."""
        self.doc_count_label.setText("Error loading documents")
        self.doc_count_label.setStyleSheet("color: #dc3545; font-weight: bold;")
    
    def _show_context_menu(self, position):
        """Show context menu for document operations."""
        import logging
        logger = logging.getLogger(__name__)
        
        if not self.documents_tree:
            return
        
        # Get the item at the clicked position
        item = self.documents_tree.itemAt(position)
        if not item:
            return
        
        # Find the document root item
        document_item = self._find_document_root_item(item)
        if not document_item or not hasattr(document_item, 'document_index'):
            return
        
        document_index = document_item.document_index
        logger.debug(f"Showing context menu for document at index {document_index}")
        
        # Create context menu
        context_menu = QMenu(self.documents_tree)
        context_menu.setStyleSheet(self._get_context_menu_style())
        
        # View Document action
        view_action = QAction(fa.icon('fa6s.eye', color='#3b82f6'), "View Document", context_menu)
        view_action.triggered.connect(lambda: self._handle_view_document(document_index))
        context_menu.addAction(view_action)
        
        context_menu.addSeparator()
        
        # Edit Document action
        edit_action = QAction(fa.icon('fa6s.pen', color='#10b981'), "Edit Document", context_menu)
        edit_action.triggered.connect(lambda: self._handle_edit_document(document_index))
        context_menu.addAction(edit_action)
        
        # Delete Document action
        delete_action = QAction(fa.icon('fa6s.trash', color='#ef4444'), "Delete Document", context_menu)
        delete_action.triggered.connect(lambda: self._handle_delete_document(document_index))
        context_menu.addAction(delete_action)
        
        # Show the context menu close to the clicked item
        if context_menu.actions():
            global_pos = self.documents_tree.mapToGlobal(position)
            context_menu.exec_(global_pos)
    
    def _find_document_root_item(self, item: QTreeWidgetItem) -> Optional[QTreeWidgetItem]:
        """Find the document root item from any child item."""
        current = item
        while current:
            if hasattr(current, 'document_index'):
                return current
            current = current.parent()
        return None
    
    def _get_context_menu_style(self):
        """Get the context menu stylesheet."""
        from ..styles.styles import CONTEXT_MENU_STYLE
        return CONTEXT_MENU_STYLE
    
    def _handle_view_document(self, index: int):
        """Handle view document action with logging."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"View document requested for index {index}")
        self.view_document_requested.emit({"index": index})
    
    def _handle_edit_document(self, index: int):
        """Handle edit document action with logging."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Edit document requested for index {index}")
        self.edit_document_requested.emit({"index": index})
    
    def _handle_delete_document(self, index: int):
        """Handle delete document action with logging."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Delete document requested for index {index}")
        self.delete_document_requested.emit({"index": index})
