"""
Data Table Component
Handles the display of MongoDB documents in a table format.
"""

from __future__ import annotations

from typing import Any

import qtawesome as fa
from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QAction, QFont, QIcon
from PySide6.QtWidgets import (
    QHBoxLayout, QHeaderView, QLabel, QMenu, QProgressBar, QPushButton,
    QSizePolicy, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
)


class DataTable(QObject):
    """Data table component for displaying MongoDB documents."""
    
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
        self.documents_table: QTableWidget | None = None
        self.collection_label: QLabel | None = None
        self.doc_count_label: QLabel | None = None
        self.loading_indicator: QProgressBar | None = None
        self.documents_data: list[dict[str, Any]] = []  # Store the actual document data
        self._create_data_table()
    
    def _create_data_table(self) -> None:
        """Create the data table widget."""
        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)
        layout.setSpacing(8)
        layout.setContentsMargins(4, 4, 4, 4)
        
        self._create_info_header(layout)
        self._create_loading_indicator(layout)
        self._create_documents_table(layout)
    
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
        
        info_layout.addWidget(self.collection_label)
        info_layout.addWidget(self.doc_count_label)
        info_layout.addStretch()
        
        # Refresh documents button
        refresh_docs_button = QPushButton("Refresh Documents")
        refresh_docs_button.setIcon(fa.icon('fa6s.arrows-rotate', color='#3b82f6'))
        refresh_docs_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        refresh_docs_button.setMinimumHeight(28)
        refresh_docs_button.clicked.connect(self.refresh_requested.emit)
        info_layout.addWidget(refresh_docs_button)
        
        parent_layout.addLayout(info_layout)
    
    def _create_loading_indicator(self, parent_layout: QVBoxLayout) -> None:
        """Create the loading indicator."""
        self.loading_indicator = QProgressBar()
        self.loading_indicator.setVisible(False)
        self.loading_indicator.setRange(0, 0)  # Indeterminate progress
        self.loading_indicator.setStyleSheet("""
            QProgressBar {
                border: 1px solid #e5e7eb;
                border-radius: 4px;
                background-color: #f9fafb;
                height: 20px;
                margin: 4px 0px;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 3px;
            }
        """)
        parent_layout.addWidget(self.loading_indicator)
    
    def _create_documents_table(self, parent_layout: QVBoxLayout) -> None:
        """Create the documents table widget."""
        self.documents_table = QTableWidget()
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
    
    def _on_selection_changed(self) -> None:
        """Handle table selection changes."""
        current_row = self.documents_table.currentRow()
        if current_row >= 0:
            # Get the document data from the current row
            # This is a simplified approach - in practice, you might want to store
            # the full document data separately and reference it by row
            pass
    
    def get_widget(self) -> QWidget | None:
        """Get the data table widget."""
        return self.widget
    
    def get_table_widget(self) -> QTableWidget | None:
        """Get the documents table widget."""
        return self.documents_table
    
    def clear_table(self) -> None:
        """Clear the documents table."""
        if self.documents_table:
            self.documents_table.setRowCount(0)
            self.documents_table.setColumnCount(0)
    
    def set_collection_info(self, collection_name: str, document_count: int) -> None:
        """Set collection information in the header."""
        if self.collection_label:
            self.collection_label.setText(f"Collection: {collection_name}")
        
        if self.doc_count_label:
            self.doc_count_label.setText(f"Documents: {document_count}")
    
    def populate_documents(self, documents: list[dict[str, Any]]) -> None:
        """Populate the table with documents in phpMyAdmin-style format."""
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
            self.documents_table.setHorizontalHeaderLabels(["No documents found"])
            
            # Create placeholder item
            placeholder_item = QTableWidgetItem("This collection is empty")
            placeholder_item.setFlags(Qt.ItemIsEnabled)
            placeholder_item.setTextAlignment(Qt.AlignCenter)
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
        
        # Get all unique field names from all documents
        all_fields = set()
        for doc in documents:
            if isinstance(doc, dict):
                all_fields.update(doc.keys())
        
        # Sort field names for consistent column order
        field_names = sorted(list(all_fields))
        
        # Set up table structure: one row per document, one column per field
        self.documents_table.setRowCount(len(documents))
        self.documents_table.setColumnCount(len(field_names))
        self.documents_table.setHorizontalHeaderLabels(field_names)
        
        # Populate table data
        for row, doc in enumerate(documents):
            if not isinstance(doc, dict):
                logger.warning(f"Skipping non-dict document at index {row}")
                continue
            
            for col, field_name in enumerate(field_names):
                value = doc.get(field_name, "")
                value_text = self._format_field_value(value)
                
                item = QTableWidgetItem(value_text)
                self.documents_table.setItem(row, col, item)
        
        # Auto-resize columns to fit content
        self.documents_table.resizeColumnsToContents()
        
        # Ensure minimum column width
        for col in range(self.documents_table.columnCount()):
            current_width = self.documents_table.columnWidth(col)
            if current_width < 100:
                self.documents_table.setColumnWidth(col, 100)
        
        # Set header to stretch
        header = self.documents_table.horizontalHeader()
        header.setStretchLastSection(True)
        
        logger.debug(f"Table populated with {len(documents)} documents and {len(field_names)} columns")
        logger.debug(f"Successfully populated table with {len(documents)} documents")
    
    def _get_field_icon(self, value: Any) -> QIcon:
        """Get appropriate icon for field type."""
        if isinstance(value, str):
            return fa.icon('fa6s.font', color='#10b981')
        elif isinstance(value, (int, float)):
            return fa.icon('fa6s.hashtag', color='#3b82f6')
        elif isinstance(value, bool):
            return fa.icon('fa6s.toggle-on' if value else 'fa6s.toggle-off', color='#f59e0b')
        elif isinstance(value, dict):
            return fa.icon('fa6s.file-code', color='#8b5cf6')
        elif isinstance(value, list):
            return fa.icon('fa6s.list', color='#ef4444')
        elif value is None:
            return fa.icon('fa6s.circle-xmark', color='#6b7280')
        else:
            return fa.icon('fa6s.question', color='#9ca3af')
    
    def _format_field_value(self, value: Any) -> str:
        """Format field value for display."""
        if isinstance(value, dict):
            return f"{{ {len(value)} fields }}"
        elif isinstance(value, list):
            return f"[ {len(value)} items ]"
        elif isinstance(value, str):
            if len(value) > 50:
                return value[:47] + "..."
            return value
        elif value is None:
            return "null"
        else:
            return str(value)
    
    def get_document_by_row(self, row: int) -> dict[str, Any] | None:
        """Get document data by row index."""
        if 0 <= row < len(self.documents_data):
            return self.documents_data[row]
        return None
    
    def get_selected_document(self) -> dict[str, Any] | None:
        """Get the currently selected document."""
        current_row = self.documents_table.currentRow()
        if current_row >= 0:
            return self.get_document_by_row(current_row)
        return None
    
    def remove_selected_row(self) -> bool:
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
    
    def set_loading_state(self, loading: bool) -> None:
        """Set the loading state for the data table."""
        if self.loading_indicator:
            self.loading_indicator.setVisible(loading)
        
        # Don't change the document count label text during loading
        # Just show/hide the loading indicator
    
    def set_error_state(self, error_message: str) -> None:
        """Set the error state for the data table."""
        if self.loading_indicator:
            self.loading_indicator.setVisible(False)
        
        self.doc_count_label.setText("Error loading documents")
        self.doc_count_label.setStyleSheet("color: #dc3545; font-weight: bold;")
    
    def resize_columns_to_content(self) -> None:
        """Resize table columns to fit content."""
        if self.documents_table:
            self.documents_table.resizeColumnsToContents()
    
    def set_alternating_row_colors(self, enabled: bool = True) -> None:
        """Enable or disable alternating row colors."""
        if self.documents_table:
            self.documents_table.setAlternatingRowColors(enabled)
    
    def set_sorting_enabled(self, enabled: bool = True) -> None:
        """Enable or disable sorting in the table."""
        if self.documents_table:
            self.documents_table.setSortingEnabled(enabled)
    
    def _show_context_menu(self, position: Any) -> None:
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
    
    def _get_context_menu_style(self) -> str:
        """Get the context menu stylesheet."""
        from ..styles.styles import CONTEXT_MENU_STYLE
        return CONTEXT_MENU_STYLE
    
    def _handle_view_document(self, row: int) -> None:
        """Handle view document action with logging."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"View document requested for row {row}")
        self.view_document_requested.emit({"row": row})
    
    def _handle_edit_document(self, row: int) -> None:
        """Handle edit document action with logging."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Edit document requested for row {row}")
        self.edit_document_requested.emit({"row": row})
    
    def _handle_delete_document(self, row: int) -> None:
        """Handle delete document action with logging."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Delete document requested for row {row}")
        self.delete_document_requested.emit({"row": row})
