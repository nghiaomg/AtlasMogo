"""
Data Table Component
Handles the display of MongoDB documents in a table format.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QPushButton, QHeaderView, QSizePolicy, QMenu
)
from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QFont, QAction
import json
import qtawesome as fa


class DataTable(QObject):
    """Data table component for displaying MongoDB documents."""
    
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
        self.documents_table = None
        self.collection_label = None
        self.doc_count_label = None
        self.documents_data = []  # Store the actual document data
        self._create_data_table()
    
    def _create_data_table(self):
        """Create the data table widget."""
        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)
        layout.setSpacing(8)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Collection info header
        self._create_info_header(layout)
        
        # Documents table
        self._create_documents_table(layout)
    
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
    
    def _create_documents_table(self, parent_layout):
        """Create the documents table widget."""
        self.documents_table = QTableWidget()
        self.documents_table.setColumnCount(2)
        self.documents_table.setHorizontalHeaderLabels(["Field", "Value"])
        self.documents_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.documents_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.documents_table.setMinimumHeight(300)
        
        # Import and apply table styles
        from ..styles.styles import DATA_TABLE_STYLE
        self.documents_table.setStyleSheet(DATA_TABLE_STYLE)
        
        # Enable sorting
        self.documents_table.setSortingEnabled(True)
        
        # Enable alternating row colors
        self.documents_table.setAlternatingRowColors(True)
        
        # Set selection behavior
        self.documents_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.documents_table.setSelectionMode(QTableWidget.SingleSelection)
        
        # Connect selection change
        self.documents_table.itemSelectionChanged.connect(self._on_selection_changed)
        
        # Enable context menu for right-click actions
        self.documents_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.documents_table.customContextMenuRequested.connect(self._show_context_menu)
        
        parent_layout.addWidget(self.documents_table)
    
    def _on_selection_changed(self):
        """Handle table selection changes."""
        current_row = self.documents_table.currentRow()
        if current_row >= 0:
            # Get the document data from the current row
            # This is a simplified approach - in practice, you might want to store
            # the full document data separately and reference it by row
            pass
    
    def get_widget(self):
        """Get the data table widget."""
        return self.widget
    
    def get_table_widget(self):
        """Get the documents table widget."""
        return self.documents_table
    
    def clear_table(self):
        """Clear the documents table."""
        if self.documents_table:
            self.documents_table.setRowCount(0)
            self.documents_table.setColumnCount(2)
            self.documents_table.setHorizontalHeaderLabels(["Field", "Value"])
    
    def set_collection_info(self, collection_name: str, document_count: int):
        """Set collection information in the header."""
        if self.collection_label:
            self.collection_label.setText(f"Collection: {collection_name}")
        
        if self.doc_count_label:
            self.doc_count_label.setText(f"Documents: {document_count}")
    
    def populate_documents(self, documents: list):
        """Populate the table with documents."""
        import logging
        logger = logging.getLogger(__name__)
        
        if not self.documents_table:
            logger.error("Documents table widget not initialized")
            return
        
        logger.debug(f"Populating table with {len(documents) if documents else 0} documents")
        
        # Store the document data for later use
        self.documents_data = documents if documents else []
        
        # Clear existing data
        self.documents_table.clear()
        
        if not documents:
            # Show empty state
            self.documents_table.setRowCount(1)
            self.documents_table.setColumnCount(1)
            self.documents_table.setHorizontalHeaderLabels(["No Documents"])
            
            # Create placeholder item
            placeholder_item = QTableWidgetItem("No documents found in this collection")
            placeholder_item.setTextAlignment(Qt.AlignCenter)
            placeholder_item.setFlags(Qt.ItemIsEnabled)  # Make it non-selectable
            self.documents_table.setItem(0, 0, placeholder_item)
            
            # Style the placeholder
            self.documents_table.setStyleSheet(self.documents_table.styleSheet() + """
                QTableWidget::item {
                    color: #6b7280;
                    font-style: italic;
                    background-color: #f9fafb;
                }
            """)
            logger.debug("Showing empty state for collection")
            return
        
        # Reset to default style
        from ..styles.styles import DATA_TABLE_STYLE
        self.documents_table.setStyleSheet(DATA_TABLE_STYLE)
        
        # Get all unique fields from documents
        all_fields = set()
        for doc in documents:
            if isinstance(doc, dict):
                all_fields.update(doc.keys())
            else:
                logger.warning(f"Document is not a dict: {type(doc)}")
        
        # Set table columns
        field_list = sorted(list(all_fields))
        logger.debug(f"Found {len(field_list)} unique fields: {field_list}")
        
        self.documents_table.setColumnCount(len(field_list))
        self.documents_table.setHorizontalHeaderLabels(field_list)
        
        # Populate table
        self.documents_table.setRowCount(len(documents))
        for row, doc in enumerate(documents):
            if not isinstance(doc, dict):
                logger.warning(f"Skipping non-dict document at row {row}")
                continue
                
            for col, field in enumerate(field_list):
                value = doc.get(field, "")
                if isinstance(value, dict):
                    value = json.dumps(value, indent=2)
                elif isinstance(value, list):
                    value = json.dumps(value)
                else:
                    value = str(value)
                
                item = QTableWidgetItem(value)
                self.documents_table.setItem(row, col, item)
        
        # Auto-resize columns to fit content
        self.documents_table.resizeColumnsToContents()
        
        # Ensure minimum column width
        for col in range(self.documents_table.columnCount()):
            current_width = self.documents_table.columnWidth(col)
            if current_width < 100:  # Minimum width
                self.documents_table.setColumnWidth(col, 100)
        
        logger.debug(f"Successfully populated table with {len(documents)} documents")
    
    def get_document_by_row(self, row: int):
        """Get document data by row index."""
        if 0 <= row < len(self.documents_data):
            return self.documents_data[row]
        return None
    
    def get_selected_document(self):
        """Get the currently selected document."""
        current_row = self.documents_table.currentRow()
        if current_row >= 0:
            return self.get_document_by_row(current_row)
        return None
    
    def remove_selected_row(self):
        """Remove the currently selected row from the table."""
        import logging
        logger = logging.getLogger(__name__)
        
        current_row = self.documents_table.currentRow()
        if current_row >= 0:
            self.documents_table.removeRow(current_row)
            logger.debug(f"Removed row {current_row} from table")
            return True
        else:
            logger.warning("No row selected for removal")
            return False
    
    def set_loading_state(self, loading: bool):
        """Set the loading state for the data table."""
        if loading:
            self.doc_count_label.setText("Loading documents...")
            self.doc_count_label.setStyleSheet("color: #007bff; font-weight: bold;")
        else:
            self.doc_count_label.setStyleSheet("color: #6c757d; font-size: 11px;")
    
    def set_error_state(self, error_message: str):
        """Set the error state for the data table."""
        self.doc_count_label.setText("Error loading documents")
        self.doc_count_label.setStyleSheet("color: #dc3545; font-weight: bold;")
    
    def resize_columns_to_content(self):
        """Resize table columns to fit content."""
        if self.documents_table:
            self.documents_table.resizeColumnsToContents()
    
    def set_alternating_row_colors(self, enabled: bool = True):
        """Enable or disable alternating row colors."""
        if self.documents_table:
            self.documents_table.setAlternatingRowColors(enabled)
    
    def set_sorting_enabled(self, enabled: bool = True):
        """Enable or disable sorting in the table."""
        if self.documents_table:
            self.documents_table.setSortingEnabled(enabled)
    
    def _show_context_menu(self, position):
        """Show context menu for document operations."""
        import logging
        logger = logging.getLogger(__name__)
        
        if not self.documents_table:
            return
        
        # Get the item at the clicked position
        item = self.documents_table.itemAt(position)
        if not item:
            return
        
        # Get the current row
        current_row = self.documents_table.currentRow()
        if current_row < 0:
            return
        
        logger.debug(f"Showing context menu for document at row {current_row}")
        
        # Create context menu
        context_menu = QMenu(self.documents_table)
        context_menu.setStyleSheet(self._get_context_menu_style())
        
        # View Document action
        view_action = QAction(fa.icon('fa6s.eye', color='#3b82f6'), "View Document", context_menu)
        view_action.triggered.connect(lambda: self._handle_view_document(current_row))
        context_menu.addAction(view_action)
        
        context_menu.addSeparator()
        
        # Edit Document action
        edit_action = QAction(fa.icon('fa6s.pen', color='#10b981'), "Edit Document", context_menu)
        edit_action.triggered.connect(lambda: self._handle_edit_document(current_row))
        context_menu.addAction(edit_action)
        
        # Delete Document action
        delete_action = QAction(fa.icon('fa6s.trash', color='#ef4444'), "Delete Document", context_menu)
        delete_action.triggered.connect(lambda: self._handle_delete_document(current_row))
        context_menu.addAction(delete_action)
        
        # Show the context menu close to the clicked item
        if context_menu.actions():
            global_pos = self.documents_table.mapToGlobal(position)
            context_menu.exec_(global_pos)
    
    def _get_context_menu_style(self):
        """Get the context menu stylesheet."""
        from ..styles.styles import CONTEXT_MENU_STYLE
        return CONTEXT_MENU_STYLE
    
    def _handle_view_document(self, row: int):
        """Handle view document action with logging."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"View document requested for row {row}")
        self.view_document_requested.emit({"row": row})
    
    def _handle_edit_document(self, row: int):
        """Handle edit document action with logging."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Edit document requested for row {row}")
        self.edit_document_requested.emit({"row": row})
    
    def _handle_delete_document(self, row: int):
        """Handle delete document action with logging."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Delete document requested for row {row}")
        self.delete_document_requested.emit({"row": row})
