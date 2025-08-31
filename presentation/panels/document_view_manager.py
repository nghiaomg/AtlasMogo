"""
Document View Manager
Manages switching between Table View and Object View for document display.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget,
    QLabel, QFrame, QSizePolicy
)
from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QFont
import qtawesome as fa

from .data_table import DataTable
from .object_view import ObjectView
from ..styles.styles import COLORS, BUTTON_STYLES


class DocumentViewManager(QObject):
    """Manages document views with seamless switching between table and object views."""
    
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
        self.stacked_widget = None
        self.data_table = None
        self.object_view = None
        self.current_view = "table"  # "table" or "object"
        self.current_documents = []
        self.current_collection_name = ""
        self._create_view_manager()
    
    def _create_view_manager(self):
        """Create the view manager widget."""
        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)
        layout.setSpacing(8)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # View selector header
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
        
        layout.addWidget(self.stacked_widget)
    
    def _create_view_selector(self, parent_layout):
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
        self.table_view_btn.setIcon(fa.icon('fa6s.table', color=COLORS['primary']))
        self.table_view_btn.setCheckable(True)
        self.table_view_btn.setChecked(True)
        self.table_view_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['text_inverse']};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 500;
                min-height: 32px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_hover']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['primary_hover']};
            }}
            QPushButton:checked {{
                background-color: {COLORS['primary']};
                color: {COLORS['text_inverse']};
            }}
        """)
        self.table_view_btn.clicked.connect(lambda: self._switch_view("table"))
        
        # Object view button
        self.object_view_btn = QPushButton("Object View")
        self.object_view_btn.setIcon(fa.icon('fa6s.code', color=COLORS['secondary']))
        self.object_view_btn.setCheckable(True)
        self.object_view_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_primary']};
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border_light']};
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 500;
                min-height: 32px;
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
        """)
        self.object_view_btn.clicked.connect(lambda: self._switch_view("object"))
        
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
    
    def _connect_signals(self):
        """Connect signals from both views."""
        # Data table signals
        self.data_table.document_selected.connect(self.document_selected.emit)
        self.data_table.refresh_requested.connect(self.refresh_requested.emit)
        self.data_table.view_document_requested.connect(self.view_document_requested.emit)
        self.data_table.edit_document_requested.connect(self.edit_document_requested.emit)
        self.data_table.delete_document_requested.connect(self.delete_document_requested.emit)
        
        # Object view signals
        self.object_view.document_selected.connect(self.document_selected.emit)
        self.object_view.refresh_requested.connect(self.refresh_requested.emit)
        self.object_view.view_document_requested.connect(self.view_document_requested.emit)
        self.object_view.edit_document_requested.connect(self.edit_document_requested.emit)
        self.object_view.delete_document_requested.connect(self.delete_document_requested.emit)
    
    def _switch_view(self, view_type: str):
        """Switch between table and object views."""
        import logging
        logger = logging.getLogger(__name__)
        
        if view_type == self.current_view:
            return
        
        logger.info(f"Switching from {self.current_view} view to {view_type} view")
        
        # Update current view
        self.current_view = view_type
        
        # Update button states
        if view_type == "table":
            self.table_view_btn.setChecked(True)
            self.object_view_btn.setChecked(False)
            self.stacked_widget.setCurrentIndex(0)
        else:
            self.table_view_btn.setChecked(False)
            self.object_view_btn.setChecked(True)
            self.stacked_widget.setCurrentIndex(1)
        
        # Synchronize data between views
        self._synchronize_views()
    
    def _synchronize_views(self):
        """Synchronize data between table and object views."""
        if self.current_documents:
            if self.current_view == "table":
                self.data_table.populate_documents(self.current_documents)
            else:
                self.object_view.populate_documents(self.current_documents)
    
    def get_widget(self):
        """Get the view manager widget."""
        return self.widget
    
    def get_current_view(self) -> str:
        """Get the current view type."""
        return self.current_view
    
    def get_data_table(self) -> DataTable:
        """Get the data table component."""
        return self.data_table
    
    def get_object_view(self) -> ObjectView:
        """Get the object view component."""
        return self.object_view
    
    def set_collection_info(self, collection_name: str, document_count: int):
        """Set collection information in both views."""
        self.current_collection_name = collection_name
        
        # Update both views
        self.data_table.set_collection_info(collection_name, document_count)
        self.object_view.set_collection_info(collection_name, document_count)
        
        # Update document count in selector
        self.doc_count_label.setText(f"Documents: {document_count}")
    
    def populate_documents(self, documents: list):
        """Populate documents in the current view."""
        import logging
        logger = logging.getLogger(__name__)
        
        self.current_documents = documents if documents else []
        
        logger.debug(f"Populating {self.current_view} view with {len(self.current_documents)} documents")
        
        if self.current_view == "table":
            self.data_table.populate_documents(documents)
        else:
            self.object_view.populate_documents(documents)
    
    def get_selected_document(self):
        """Get the currently selected document from the active view."""
        if self.current_view == "table":
            return self.data_table.get_selected_document()
        else:
            return self.object_view.get_selected_document()
    
    def clear_views(self):
        """Clear both views."""
        self.current_documents = []
        self.data_table.clear_table()
        self.object_view.clear_tree()
    
    def set_loading_state(self, loading: bool):
        """Set the loading state for both views."""
        self.data_table.set_loading_state(loading)
        self.object_view.set_loading_state(loading)
    
    def set_error_state(self, error_message: str):
        """Set the error state for both views."""
        self.data_table.set_error_state(error_message)
        self.object_view.set_error_state(error_message)
    
    def refresh_current_view(self):
        """Refresh the current view."""
        if self.current_view == "table":
            self.data_table.populate_documents(self.current_documents)
        else:
            self.object_view.populate_documents(self.current_documents)
    
    def get_document_by_index(self, index: int):
        """Get document by index from the current view."""
        if self.current_view == "table":
            return self.data_table.get_document_by_row(index)
        else:
            return self.object_view.get_document_by_index(index)
    
    def get_document_by_row(self, row: int):
        """Get document by row (for table view compatibility)."""
        if self.current_view == "table":
            return self.data_table.get_document_by_row(row)
        else:
            return self.object_view.get_document_by_index(row)
    
    def remove_selected_row(self):
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
    
    def resize_columns_to_content(self):
        """Resize table columns to fit content (table view only)."""
        if self.current_view == "table":
            self.data_table.resize_columns_to_content()
    
    def set_alternating_row_colors(self, enabled: bool = True):
        """Enable or disable alternating row colors (table view only)."""
        if self.current_view == "table":
            self.data_table.set_alternating_row_colors(enabled)
    
    def set_sorting_enabled(self, enabled: bool = True):
        """Enable or disable sorting (table view only)."""
        if self.current_view == "table":
            self.data_table.set_sorting_enabled(enabled)
