"""
Document View Manager
Manages switching between Table View and Object View for document display.
"""

from __future__ import annotations

from typing import Any

import qtawesome as fa
from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QStackedWidget,
    QVBoxLayout, QWidget
)

from .data_table import DataTable
from .object_view import ObjectView
from ..styles.styles import COLORS, BUTTON_STYLES
from business.pagination_manager import PaginationManager


class DocumentViewManager(QObject):
    """Manages document views with seamless switching between table and object views."""
    
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
        self.stacked_widget: QStackedWidget | None = None
        self.data_table: DataTable | None = None
        self.object_view: ObjectView | None = None
        self.current_view: str = "table"  # "table" or "object"
        self.current_documents: list[dict[str, Any]] = []
        self.current_collection_name: str = ""
        self.table_view_btn: QPushButton | None = None
        self.object_view_btn: QPushButton | None = None
        self.doc_count_label: QLabel | None = None
        
        # Pagination and caching
        self.pagination_manager = PaginationManager(default_page_size=50, max_cache_size=10)
        self.current_page = 1
        self.current_page_size = 50
        self.total_documents = 0
        self.current_query = ""
        self.current_sort = None
        
        self._create_view_manager()
    
    def _create_view_manager(self) -> None:
        """Create the view manager widget."""
        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)
        layout.setSpacing(8)
        layout.setContentsMargins(4, 4, 4, 4)
        
        self._create_view_selector(layout)
        
        # Stacked widget for views
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Create data table view
        self.data_table = DataTable(self.parent)
        self.stacked_widget.addWidget(self.data_table.get_widget())
        
        # Create object view
        self.object_view = ObjectView(self.parent)
        self.stacked_widget.addWidget(self.object_view.get_widget())
        
        # Connect signals
        self._connect_signals()
        
        # Ensure initial state is correct
        self._ensure_correct_button_states()
        
        layout.addWidget(self.stacked_widget)
    
    def _create_view_selector(self, parent_layout: QVBoxLayout) -> None:
        """Create the view selector header."""
        selector_frame = QFrame()
        selector_frame.setFrameStyle(QFrame.StyledPanel)
        selector_frame.setStyleSheet(f"""
            QFrame {{
                border: 1px solid {COLORS['border_light']};
                border-radius: 6px;
                background-color: {COLORS['bg_secondary']};
                padding: 8px;
            }}
        """)
        
        selector_layout = QHBoxLayout(selector_frame)
        selector_layout.setSpacing(12)
        selector_layout.setContentsMargins(12, 8, 12, 8)
        
        # View label
        view_label = QLabel("Document View:")
        view_label.setFont(QFont("Arial", 11, QFont.Bold))
        view_label.setStyleSheet(f"color: {COLORS['text_primary']};")
        
        # Table view button
        self.table_view_btn = QPushButton("Table View")
        self.table_view_btn.setIcon(fa.icon('fa6s.table', color=COLORS['text_inverse']))
        self.table_view_btn.setCheckable(True)
        self.table_view_btn.setChecked(True)  # Default to table view
        self.table_view_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['text_inverse']};
                border: 2px solid {COLORS['primary']};
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 500;
                min-height: 32px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_hover']};
                border-color: {COLORS['primary_hover']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['primary_hover']};
                border-color: {COLORS['primary_hover']};
            }}
            QPushButton:checked {{
                background-color: {COLORS['primary']};
                color: {COLORS['text_inverse']};
                border-color: {COLORS['primary']};
            }}
            QPushButton:!checked {{
                background-color: {COLORS['bg_primary']};
                color: {COLORS['text_secondary']};
                border-color: {COLORS['border_light']};
            }}
        """)
        self.table_view_btn.clicked.connect(self._on_table_view_clicked)
        
        # Object view button
        self.object_view_btn = QPushButton("Object View")
        self.object_view_btn.setIcon(fa.icon('fa6s.code', color=COLORS['text_secondary']))
        self.object_view_btn.setCheckable(True)
        self.object_view_btn.setChecked(False)  # Not checked by default
        self.object_view_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_primary']};
                color: {COLORS['text_secondary']};
                border: 2px solid {COLORS['border_light']};
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 500;
                min-height: 32px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
                border-color: {COLORS['border_medium']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['border_light']};
                color: {COLORS['text_primary']};
            }}
            QPushButton:checked {{
                background-color: {COLORS['primary']};
                color: {COLORS['text_inverse']};
                border-color: {COLORS['primary']};
            }}
            QPushButton:!checked {{
                background-color: {COLORS['bg_primary']};
                color: {COLORS['text_secondary']};
                border-color: {COLORS['border_light']};
            }}
        """)
        self.object_view_btn.clicked.connect(self._on_object_view_clicked)
        
        # Add widgets to layout
        selector_layout.addWidget(view_label)
        selector_layout.addWidget(self.table_view_btn)
        selector_layout.addWidget(self.object_view_btn)
        selector_layout.addStretch()
        
        # Document count label
        self.doc_count_label = QLabel("Documents: 0")
        self.doc_count_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        selector_layout.addWidget(self.doc_count_label)
        
        parent_layout.addWidget(selector_frame)
    
    def _connect_signals(self) -> None:
        """Connect signals from both views."""
        # Data table signals
        self.data_table.document_selected.connect(self.document_selected.emit)
        self.data_table.refresh_requested.connect(self.refresh_requested.emit)
        self.data_table.view_document_requested.connect(self.view_document_requested.emit)
        self.data_table.edit_document_requested.connect(self.edit_document_requested.emit)
        self.data_table.delete_document_requested.connect(self.delete_document_requested.emit)
        
        # Pagination signals
        self.data_table.page_changed.connect(self._on_page_changed)
        self.data_table.page_size_changed.connect(self._on_page_size_changed)
        
        # Object view signals
        self.object_view.document_selected.connect(self.document_selected.emit)
        self.object_view.refresh_requested.connect(self.refresh_requested.emit)
        self.object_view.view_document_requested.connect(self.view_document_requested.emit)
        self.object_view.edit_document_requested.connect(self.edit_document_requested.emit)
        self.object_view.delete_document_requested.connect(self.delete_document_requested.emit)
    
    def _on_table_view_clicked(self) -> None:
        """Handle table view button click."""
        import logging
        logger = logging.getLogger(__name__)
        
        # Always activate table view when clicked
        if self.current_view != "table":
            logger.info("Table View activated")
            self._switch_view("table")
        else:
            # Ensure table view remains active even if clicked again
            logger.info("Table View clicked (already active)")
            self._ensure_correct_button_states()
    
    def _on_object_view_clicked(self) -> None:
        """Handle object view button click."""
        import logging
        logger = logging.getLogger(__name__)
        
        # Always activate object view when clicked
        if self.current_view != "object":
            logger.info("Object View activated")
            self._switch_view("object")
        else:
            # Ensure object view remains active even if clicked again
            logger.info("Object View clicked (already active)")
            self._ensure_correct_button_states()
    
    def _switch_view(self, view_type: str) -> None:
        """Switch between table and object views."""
        import logging
        logger = logging.getLogger(__name__)
        
        if view_type == self.current_view:
            logger.debug(f"Already in {view_type} view, no switch needed")
            return
        
        logger.info(f"Switching from {self.current_view} view to {view_type} view")
        
        # Update current view
        self.current_view = view_type
        
        # Update button states - ensure mutual exclusivity
        if view_type == "table":
            self.table_view_btn.setChecked(True)
            self.object_view_btn.setChecked(False)
            self.stacked_widget.setCurrentIndex(0)
            logger.info("Table View activated - showing table content")
        else:
            self.table_view_btn.setChecked(False)
            self.object_view_btn.setChecked(True)
            self.stacked_widget.setCurrentIndex(1)
            logger.info("Object View activated - showing JSON content")
        
        # Synchronize data between views
        self._synchronize_views()
        
        # Ensure button states are correct
        self._ensure_correct_button_states()
    
    def _ensure_correct_button_states(self) -> None:
        """Ensure only one button is checked at a time."""
        import logging
        logger = logging.getLogger(__name__)
        
        # Block signals temporarily to prevent recursive calls
        self.table_view_btn.blockSignals(True)
        self.object_view_btn.blockSignals(True)
        
        try:
            if self.current_view == "table":
                self.table_view_btn.setChecked(True)
                self.object_view_btn.setChecked(False)
                logger.debug("Button states synchronized: Table View active, Object View inactive")
            else:
                self.table_view_btn.setChecked(False)
                self.object_view_btn.setChecked(True)
                logger.debug("Button states synchronized: Object View active, Table View inactive")
            
            # Update icon colors based on button states
            self._update_button_icons()
        finally:
            # Unblock signals
            self.table_view_btn.blockSignals(False)
            self.object_view_btn.blockSignals(False)
    
    def _update_button_icons(self) -> None:
        """Update button icon colors based on their checked state."""
        # Update table view button icon
        if self.table_view_btn.isChecked():
            self.table_view_btn.setIcon(fa.icon('fa6s.table', color=COLORS['text_inverse']))
        else:
            self.table_view_btn.setIcon(fa.icon('fa6s.table', color=COLORS['text_secondary']))
        
        # Update object view button icon
        if self.object_view_btn.isChecked():
            self.object_view_btn.setIcon(fa.icon('fa6s.code', color=COLORS['text_inverse']))
        else:
            self.object_view_btn.setIcon(fa.icon('fa6s.code', color=COLORS['text_secondary']))
    
    def _synchronize_views(self) -> None:
        """Synchronize data between table and object views."""
        if self.current_documents:
            if self.current_view == "table":
                self.data_table.populate_documents(self.current_documents)
            else:
                self.object_view.populate_documents(self.current_documents)
    
    def get_widget(self) -> QWidget | None:
        """Get the view manager widget."""
        return self.widget
    
    def get_current_view(self) -> str:
        """Get the current view type."""
        return self.current_view
    
    def force_view(self, view_type: str) -> None:
        """Force a specific view to be active (for debugging and consistency)."""
        import logging
        logger = logging.getLogger(__name__)
        
        if view_type not in ["table", "object"]:
            logger.warning(f"Invalid view type: {view_type}. Must be 'table' or 'object'")
            return
        
        logger.info(f"Force activating {view_type} view")
        self._switch_view(view_type)
    
    def _on_page_changed(self, page_number: int) -> None:
        """Handle page change from data table."""
        import logging
        logger = logging.getLogger(__name__)
        
        if page_number != self.current_page:
            logger.info(f"[PAGINATION] Page changed to {page_number}")
            self.current_page = page_number
            self._load_current_page()
    
    def _on_page_size_changed(self, page_size: int) -> None:
        """Handle page size change from data table."""
        import logging
        logger = logging.getLogger(__name__)
        
        if page_size != self.current_page_size:
            logger.info(f"[PAGINATION] Page size changed to {page_size}")
            self.current_page_size = page_size
            self.current_page = 1  # Reset to first page
            self.pagination_manager.clear_cache_for_query(self.current_query, self.current_sort)
            self._load_current_page()
    
    def get_view_status(self) -> dict:
        """Get the current view status for debugging purposes."""
        return {
            "current_view": self.current_view,
            "table_button_checked": self.table_view_btn.isChecked() if self.table_view_btn else False,
            "object_button_checked": self.object_view_btn.isChecked() if self.object_view_btn else False,
            "stacked_widget_index": self.stacked_widget.currentIndex() if self.stacked_widget else -1,
            "pagination": {
                "current_page": self.current_page,
                "page_size": self.current_page_size,
                "total_documents": self.total_documents,
                "total_pages": self.pagination_manager.get_page_info(self.current_page, self.total_documents, self.current_page_size).total_pages
            }
        }
    
    def get_data_table(self) -> DataTable | None:
        """Get the data table component."""
        return self.data_table
    
    def get_object_view(self) -> ObjectView | None:
        """Get the object view component."""
        return self.object_view
    
    def get_pagination_stats(self) -> dict:
        """Get pagination and cache statistics."""
        cache_stats = self.pagination_manager.get_cache_stats()
        memory_stats = self.pagination_manager.get_memory_usage_estimate()
        
        return {
            "current_page": self.current_page,
            "page_size": self.current_page_size,
            "total_documents": self.total_documents,
            "total_pages": self.pagination_manager.get_page_info(self.current_page, self.total_documents, self.current_page_size).total_pages,
            "cache_stats": cache_stats,
            "memory_usage": memory_stats
        }
    
    def _load_current_page(self) -> None:
        """Load the current page of documents."""
        import logging
        logger = logging.getLogger(__name__)
        
        if not self.current_collection_name:
            logger.warning("[PAGINATION] No collection selected, cannot load page")
            return
        
        # Check if page is cached
        cached_documents = self.pagination_manager.get_cached_page(self.current_page)
        if cached_documents:
            logger.info(f"[PAGINATION] Using cached page {self.current_page}")
            self._populate_current_view(cached_documents)
            return
        
        # Page not cached, need to load from database
        logger.info(f"[PAGINATION] Loading page {self.current_page} from database")
        self._request_page_from_database()
    
    def _request_page_from_database(self) -> None:
        """Request a page of documents from the database."""
        import logging
        logger = logging.getLogger(__name__)
        
        # This method will be called by the main window when it has access to mongo_service
        # For now, we'll emit a signal to request the page
        logger.info(f"[PAGINATION] Requesting page {self.current_page} (size: {self.current_page_size})")
        # TODO: Implement database request logic in main window
    
    def _populate_current_view(self, documents: List[Dict[str, Any]]) -> None:
        """Populate the current view with documents."""
        import logging
        logger = logging.getLogger(__name__)
        
        self.current_documents = documents
        
        logger.debug(f"Populating {self.current_view} view with {len(documents)} documents")
        
        if self.current_view == "table":
            self.data_table.populate_documents(documents)
            # Update pagination info in data table
            page_info = self.pagination_manager.get_page_info(self.current_page, self.total_documents, self.current_page_size)
            self.data_table.set_pagination_info(page_info.page_number, page_info.total_pages, page_info.limit)
        else:
            self.object_view.populate_documents(documents)
    
    def set_collection_info(self, collection_name: str, document_count: int) -> None:
        """Set collection information in both views."""
        self.current_collection_name = collection_name
        
        # Update both views
        self.data_table.set_collection_info(collection_name, document_count)
        self.object_view.set_collection_info(collection_name, document_count)
        
        # Update document count in selector
        self.doc_count_label.setText(f"Documents: {document_count}")
        
        # Update pagination information
        self.total_documents = document_count
        self.current_page = 1  # Reset to first page when collection changes
        
        # Clear cache for new collection
        self.pagination_manager.clear_cache()
        
        # Load first page
        self._load_current_page()
    
    def populate_documents(self, documents: list[dict[str, Any]], page_number: int = 1) -> None:
        """Populate documents in the current view with pagination support."""
        import logging
        logger = logging.getLogger(__name__)
        
        self.current_documents = documents if documents else []
        
        logger.debug(f"Populating {self.current_view} view with {len(self.current_documents)} documents (page {page_number})")
        
        # Cache the page if it's not already cached
        if documents and page_number > 0:
            self.pagination_manager.cache_page(page_number, documents)
        
        if self.current_view == "table":
            self.data_table.populate_documents(documents)
            # Update pagination info
            page_info = self.pagination_manager.get_page_info(page_number, self.total_documents, self.current_page_size)
            self.data_table.set_pagination_info(page_info.page_number, page_info.total_pages, page_info.limit)
        else:
            self.object_view.populate_documents(documents)
    
    def load_page(self, page_number: int, documents: list[dict[str, Any]]) -> None:
        """Load a specific page of documents."""
        import logging
        logger = logging.getLogger(__name__)
        
        if page_number != self.current_page:
            logger.info(f"[PAGINATION] Loading page {page_number} with {len(documents)} documents")
            self.current_page = page_number
            self.populate_documents(documents, page_number)
        else:
            logger.debug(f"[PAGINATION] Page {page_number} already loaded")
            self.populate_documents(documents, page_number)
    
    def get_selected_document(self) -> dict[str, Any] | None:
        """Get the currently selected document from the active view."""
        if self.current_view == "table":
            return self.data_table.get_selected_document()
        else:
            return self.object_view.get_selected_document()
    
    def clear_views(self) -> None:
        """Clear both views."""
        self.current_documents = []
        self.data_table.clear_table()
        self.object_view.clear_tree()
    
    def set_loading_state(self, loading: bool) -> None:
        """Set the loading state for both views."""
        self.data_table.set_loading_state(loading)
        self.object_view.set_loading_state(loading)
    
    def set_error_state(self, error_message: str) -> None:
        """Set the error state for both views."""
        self.data_table.set_error_state(error_message)
        self.object_view.set_error_state(error_message)
    
    def refresh_current_view(self) -> None:
        """Refresh the current view."""
        if self.current_view == "table":
            self.data_table.populate_documents(self.current_documents)
        else:
            self.object_view.populate_documents(self.current_documents)
    
    def get_document_by_index(self, index: int) -> dict[str, Any] | None:
        """Get document by index from the current view."""
        if self.current_view == "table":
            return self.data_table.get_document_by_row(index)
        else:
            return self.object_view.get_document_by_index(index)
    
    def get_document_by_row(self, row: int) -> dict[str, Any] | None:
        """Get document by row (for table view compatibility)."""
        if self.current_view == "table":
            return self.data_table.get_document_by_row(row)
        else:
            return self.object_view.get_document_by_index(row)
    
    def remove_selected_row(self) -> bool:
        """Remove the selected row from the current view."""
        if self.current_view == "table":
            return self.data_table.remove_selected_row()
        else:
            # For object view, we need to handle this differently
            # since it doesn't have rows in the same way
            selected_doc = self.object_view.get_selected_document()
            if selected_doc:
                # Remove from documents list
                if selected_doc in self.current_documents:
                    self.current_documents.remove(selected_doc)
                    self.object_view.populate_documents(self.current_documents)
                    return True
            return False
    
    def resize_columns_to_content(self) -> None:
        """Resize table columns to fit content (table view only)."""
        if self.current_view == "table":
            self.data_table.resize_columns_to_content()
    
    def set_alternating_row_colors(self, enabled: bool = True) -> None:
        """Enable or disable alternating row colors (table view only)."""
        if self.current_view == "table":
            self.data_table.set_alternating_row_colors(enabled)
    
    def set_sorting_enabled(self, enabled: bool = True) -> None:
        """Enable or disable sorting (table view only)."""
        if self.current_view == "table":
            self.data_table.set_sorting_enabled(enabled)
