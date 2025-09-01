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
    QSizePolicy, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
    QSpinBox, QFrame, QGridLayout, QComboBox
)

# Import styles at module level
from ..styles.styles import BUTTON_STYLES


class DataTable(QObject):
    """Data table component for displaying MongoDB documents."""
    
    # Signals
    document_selected = Signal(dict)  # Emits selected document
    refresh_requested = Signal()
    
    # Pagination signals
    page_changed = Signal(int)  # Emits new page number
    page_size_changed = Signal(int)  # Emits new page size
    
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
        
        # Pagination properties
        self.current_page = 1
        self.page_size = 50
        self.total_documents = 0
        self.total_pages = 1
        
        # Pagination UI elements
        self.pagination_frame: QFrame | None = None
        self.page_info_label: QLabel | None = None
        self.page_size_spinbox: QComboBox | None = None
        self.first_page_btn: QPushButton | None = None
        self.prev_page_btn: QPushButton | None = None
        self.next_page_btn: QPushButton | None = None
        self.last_page_btn: QPushButton | None = None
        self.go_to_page_spinbox: QSpinBox | None = None
        
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
        self._create_pagination_controls(layout)
    
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
    
    def _on_page_size_changed(self, new_page_size: int) -> None:
        """Handle page size change."""
        import logging
        logger = logging.getLogger(__name__)
        
        if new_page_size != self.page_size:
            self.page_size = new_page_size
            self.current_page = 1  # Reset to first page
            logger.info(f"[PAGINATION] Page size changed to {new_page_size}")
            self.page_size_changed.emit(new_page_size)
    
    def _go_to_first_page(self) -> None:
        """Go to the first page."""
        if self.current_page != 1:
            self._go_to_page(1)
    
    def _go_to_previous_page(self) -> None:
        """Go to the previous page."""
        if self.current_page > 1:
            self._go_to_page(self.current_page - 1)
    
    def _go_to_next_page(self) -> None:
        """Go to the next page."""
        if self.current_page < self.total_pages:
            self._go_to_page(self.current_page + 1)
    
    def _go_to_last_page(self) -> None:
        """Go to the last page."""
        if self.current_page != self.total_pages:
            self._go_to_page(self.total_pages)
    
    def _go_to_specific_page(self, page_number: int) -> None:
        """Go to a specific page number."""
        if 1 <= page_number <= self.total_pages and page_number != self.current_page:
            self._go_to_page(page_number)
    
    def _go_to_page(self, page_number: int) -> None:
        """Internal method to navigate to a specific page."""
        import logging
        logger = logging.getLogger(__name__)
        
        if 1 <= page_number <= self.total_pages:
            self.current_page = page_number
            logger.info(f"[PAGINATION] Navigating to page {page_number}")
            self.page_changed.emit(page_number)
        else:
            logger.warning(f"[PAGINATION] Invalid page number: {page_number}")
    
    def _update_pagination_controls(self) -> None:
        """Update pagination control states and labels."""
        if not self.pagination_frame:
            return
        
        # Update page info label
        if self.page_info_label:
            self.page_info_label.setText(f"Page {self.current_page} of {self.total_pages}")
        
        # Update go-to-page spinbox range
        if self.go_to_page_spinbox:
            self.go_to_page_spinbox.setRange(1, self.total_pages)
            self.go_to_page_spinbox.setValue(self.current_page)
        
        # Update navigation button states
        if self.first_page_btn:
            self.first_page_btn.setEnabled(self.current_page > 1)
        
        if self.prev_page_btn:
            self.prev_page_btn.setEnabled(self.current_page > 1)
        
        if self.next_page_btn:
            self.next_page_btn.setEnabled(self.current_page < self.total_pages)
        
        if self.last_page_btn:
            self.last_page_btn.setEnabled(self.current_page < self.total_pages)
    
    def _create_loading_indicator(self, parent_layout: QVBoxLayout) -> None:
        """Create the loading indicator with contextual messages."""
        loading_layout = QHBoxLayout()
        loading_layout.setSpacing(8)
        
        # Loading spinner
        self.loading_indicator = QProgressBar()
        self.loading_indicator.setVisible(False)
        self.loading_indicator.setRange(0, 0)  # Indeterminate progress
        self.loading_indicator.setMaximumHeight(20)
        self.loading_indicator.setStyleSheet("""
            QProgressBar {
                border: 1px solid #e5e7eb;
                border-radius: 4px;
                background-color: #f9fafb;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 3px;
            }
        """)
        
        # Loading message label
        self.loading_message = QLabel("")
        self.loading_message.setVisible(False)
        self.loading_message.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 11px;
                font-style: italic;
            }
        """)
        
        loading_layout.addWidget(self.loading_indicator)
        loading_layout.addWidget(self.loading_message)
        loading_layout.addStretch()
        
        parent_layout.addLayout(loading_layout)
    
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
    
    def _create_pagination_controls(self, parent_layout: QVBoxLayout) -> None:
        """Create compact, user-friendly pagination controls."""
        # Main pagination container - no border, clean background
        self.pagination_frame = QFrame()
        self.pagination_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                padding: 8px;
            }
        """)
        
        # Main horizontal layout for pagination
        pagination_layout = QHBoxLayout(self.pagination_frame)
        pagination_layout.setSpacing(12)
        pagination_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left side: Navigation controls (centered)
        nav_container = QFrame()
        nav_container.setStyleSheet("background-color: transparent;")
        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setSpacing(8)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        
        # Navigation buttons with improved styling
        self.first_page_btn = QPushButton("⏮")
        self.first_page_btn.setToolTip("Go to first page")
        self.first_page_btn.setStyleSheet(BUTTON_STYLES['pagination_nav'])
        self.first_page_btn.clicked.connect(self._go_to_first_page)
        self.first_page_btn.setEnabled(False)
        
        self.prev_page_btn = QPushButton("◀")
        self.prev_page_btn.setToolTip("Go to previous page")
        self.prev_page_btn.setStyleSheet(BUTTON_STYLES['pagination_nav'])
        self.prev_page_btn.clicked.connect(self._go_to_previous_page)
        self.prev_page_btn.setEnabled(False)
        
        # Page info label - centered and prominent
        self.page_info_label = QLabel("Page 1 of 1")
        self.page_info_label.setStyleSheet("""
            QLabel {
                color: #374151;
                font-weight: 600;
                font-size: 12px;
                min-width: 80px;
                padding: 0 8px;
            }
        """)
        self.page_info_label.setAlignment(Qt.AlignCenter)
        
        self.next_page_btn = QPushButton("▶")
        self.next_page_btn.setToolTip("Go to next page")
        self.next_page_btn.setStyleSheet(BUTTON_STYLES['pagination_nav'])
        self.next_page_btn.clicked.connect(self._go_to_next_page)
        self.next_page_btn.setEnabled(False)
        
        self.last_page_btn = QPushButton("⏭")
        self.last_page_btn.setToolTip("Go to last page")
        self.last_page_btn.setStyleSheet(BUTTON_STYLES['pagination_nav'])
        self.last_page_btn.clicked.connect(self._go_to_last_page)
        self.last_page_btn.setEnabled(False)
        
        # Add navigation controls to nav container
        nav_layout.addWidget(self.first_page_btn)
        nav_layout.addWidget(self.prev_page_btn)
        nav_layout.addWidget(self.page_info_label)
        nav_layout.addWidget(self.next_page_btn)
        nav_layout.addWidget(self.last_page_btn)
        
        # Right side: Page size and go-to controls
        controls_container = QFrame()
        controls_container.setStyleSheet("background-color: transparent;")
        controls_layout = QHBoxLayout(controls_container)
        controls_layout.setSpacing(8)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        
        # Page size selector
        page_size_label = QLabel("Page Size:")
        page_size_label.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 11px;
                font-weight: 500;
            }
        """)
        
        self.page_size_spinbox = QComboBox()
        self.page_size_spinbox.addItems(["10", "25", "50", "100"])
        # Set current value, defaulting to 50 if current page_size is not in the list
        current_size = str(self.page_size) if str(self.page_size) in ["10", "25", "50", "100"] else "50"
        self.page_size_spinbox.setCurrentText(current_size)
        self.page_size_spinbox.setStyleSheet(BUTTON_STYLES['pagination_control'].replace('QSpinBox', 'QComboBox'))
        self.page_size_spinbox.currentTextChanged.connect(lambda text: self._on_page_size_changed(int(text)))
        
        # Go to page input
        go_to_label = QLabel("Go to:")
        go_to_label.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 11px;
                font-weight: 500;
            }
        """)
        
        self.go_to_page_spinbox = QSpinBox()
        self.go_to_page_spinbox.setRange(1, 1)
        self.go_to_page_spinbox.setValue(1)
        self.go_to_page_spinbox.setStyleSheet(BUTTON_STYLES['pagination_control'])
        self.go_to_page_spinbox.valueChanged.connect(self._go_to_specific_page)
        
        # Add Enter key support for go-to page
        self.go_to_page_spinbox.installEventFilter(self)
        
        # Add keyboard navigation support for navigation buttons
        self.first_page_btn.installEventFilter(self)
        self.prev_page_btn.installEventFilter(self)
        self.next_page_btn.installEventFilter(self)
        self.last_page_btn.installEventFilter(self)
        
        # Add controls to right container
        controls_layout.addWidget(page_size_label)
        controls_layout.addWidget(self.page_size_spinbox)
        controls_layout.addWidget(go_to_label)
        controls_layout.addWidget(self.go_to_page_spinbox)
        
        # Main layout: Navigation (centered) | Controls (right-aligned)
        pagination_layout.addStretch()  # Left spacer
        pagination_layout.addWidget(nav_container)  # Center navigation
        pagination_layout.addStretch()  # Right spacer
        pagination_layout.addWidget(controls_container)  # Right controls
        
        parent_layout.addWidget(self.pagination_frame)
    
    def eventFilter(self, obj, event):
        """Handle events for pagination controls."""
        if event.type() == event.Type.KeyPress:
            if obj == self.go_to_page_spinbox:
                if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
                    # Enter key pressed - navigate to the specified page
                    page_number = self.go_to_page_spinbox.value()
                    if 1 <= page_number <= self.total_pages:
                        self._go_to_page(page_number)
                    return True
            elif obj == self.first_page_btn and event.key() == Qt.Key.Key_Home:
                # Home key pressed - go to first page
                if self.first_page_btn.isEnabled():
                    self._go_to_first_page()
                return True
            elif obj == self.prev_page_btn and event.key() == Qt.Key.Key_Left:
                # Left arrow key pressed - go to previous page
                if self.prev_page_btn.isEnabled():
                    self._go_to_previous_page()
                return True
            elif obj == self.next_page_btn and event.key() == Qt.Key.Key_Right:
                # Right arrow key pressed - go to next page
                if self.next_page_btn.isEnabled():
                    self._go_to_next_page()
                return True
            elif obj == self.last_page_btn and event.key() == Qt.Key.Key_End:
                # End key pressed - go to last page
                if self.last_page_btn.isEnabled():
                    self._go_to_last_page()
                return True
        return super().eventFilter(obj, event)
    
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
        
        # Update pagination information
        self.total_documents = document_count
        self.total_pages = max(1, (document_count + self.page_size - 1) // self.page_size)
        
        # Reset to first page if current page is out of range
        if self.current_page > self.total_pages:
            self.current_page = 1
        
        # Update pagination controls
        self._update_pagination_controls()
    
    def set_pagination_info(self, current_page: int, total_pages: int, page_size: int = None) -> None:
        """Set pagination information."""
        if page_size is not None:
            self.page_size = page_size
        
        self.current_page = current_page
        self.total_pages = total_pages
        
        # Update pagination controls
        self._update_pagination_controls()
    
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
    
    def set_loading_state(self, loading: bool, message: str = "") -> None:
        """Set the loading state for the data table with contextual message."""
        if self.loading_indicator:
            self.loading_indicator.setVisible(loading)
        
        if self.loading_message:
            if loading and message:
                self.loading_message.setText(message)
                self.loading_message.setVisible(True)
            else:
                self.loading_message.setVisible(False)
                self.loading_message.setText("")
        
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
    
    def get_pagination_state(self) -> dict:
        """Get current pagination state."""
        return {
            "current_page": self.current_page,
            "page_size": self.page_size,
            "total_documents": self.total_documents,
            "total_pages": self.total_pages
        }
    
    def _show_context_menu(self, position: Any) -> None:
        """Show context menu for document operations."""
        import logging
        logger = logging.getLogger(__name__)
        
        if not self.documents_table:
            return
        
        # Get the item at the clicked position
        item = self.documents_table.itemAt(position)
        if not item:
            logger.debug("No item found at right-click position")
            return
        
        # Get the row that was right-clicked
        clicked_row = item.row()
        logger.debug(f"Right-clicked on row {clicked_row}")
        
        # Set the clicked row as the current selection to ensure context menu actions target the correct document
        self.documents_table.setCurrentCell(clicked_row, 0)
        
        # Get the document data for the clicked row
        document = self.get_document_by_row(clicked_row)
        if not document:
            logger.warning(f"No document data found for row {clicked_row}")
            return
        
        # Log which document is being targeted
        document_id = document.get("_id", "Unknown")
        logger.info(f"Context menu for document at row {clicked_row}, _id: {document_id}")
        
        # Create context menu
        context_menu = QMenu(self.documents_table)
        context_menu.setStyleSheet(self._get_context_menu_style())
        
        # View Document action
        view_action = QAction(fa.icon('fa6s.eye', color='#3b82f6'), "View Document", context_menu)
        view_action.triggered.connect(lambda: self._handle_view_document(clicked_row))
        context_menu.addAction(view_action)
        
        context_menu.addSeparator()
        
        # Edit Document action
        edit_action = QAction(fa.icon('fa6s.pen', color='#10b981'), "Edit Document", context_menu)
        edit_action.triggered.connect(lambda: self._handle_edit_document(clicked_row))
        context_menu.addAction(edit_action)
        
        # Delete Document action
        delete_action = QAction(fa.icon('fa6s.trash', color='#ef4444'), "Delete Document", context_menu)
        delete_action.triggered.connect(lambda: self._handle_delete_document(clicked_row))
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
        
        # Get the document data for the row
        document = self.get_document_by_row(row)
        if document:
            document_id = document.get("_id", "Unknown")
            logger.info(f"Delete document requested for row {row}, _id: {document_id}")
        else:
            logger.warning(f"No document data found for row {row}")
        
        self.delete_document_requested.emit({"row": row})
