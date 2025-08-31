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
        
        # Object view signals
        self.object_view.document_selected.connect(self.document_selected.emit)
        self.object_view.refresh_requested.connect(self.refresh_requested.emit)
        self.object_view.view_document_requested.connect(self.view_document_requested.emit)
        self.object_view.edit_document_requested.connect(self.edit_document_requested.emit)
        self.object_view.delete_document_requested.connect(self.delete_document_requested.emit)
    
    def _on_table_view_clicked(self) -> None:
        """Handle table view button click."""
        if self.current_view != "table":
            self._switch_view("table")
    
    def _on_object_view_clicked(self) -> None:
        """Handle object view button click."""
        if self.current_view != "object":
            self._switch_view("object")
    
    def _switch_view(self, view_type: str) -> None:
        """Switch between table and object views."""
        import logging
        logger = logging.getLogger(__name__)
        
        if view_type == self.current_view:
            return
        
        logger.info(f"Switching from {self.current_view} view to {view_type} view")
        
        # Update current view
        self.current_view = view_type
        
        # Update button states - ensure mutual exclusivity
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
        
        # Ensure button states are correct
        self._ensure_correct_button_states()
    
    def _ensure_correct_button_states(self) -> None:
        """Ensure only one button is checked at a time."""
        # Block signals temporarily to prevent recursive calls
        self.table_view_btn.blockSignals(True)
        self.object_view_btn.blockSignals(True)
        
        try:
            if self.current_view == "table":
                self.table_view_btn.setChecked(True)
                self.object_view_btn.setChecked(False)
            else:
                self.table_view_btn.setChecked(False)
                self.object_view_btn.setChecked(True)
            
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
    
    def get_data_table(self) -> DataTable | None:
        """Get the data table component."""
        return self.data_table
    
    def get_object_view(self) -> ObjectView | None:
        """Get the object view component."""
        return self.object_view
    
    def set_collection_info(self, collection_name: str, document_count: int) -> None:
        """Set collection information in both views."""
        self.current_collection_name = collection_name
        
        # Update both views
        self.data_table.set_collection_info(collection_name, document_count)
        self.object_view.set_collection_info(collection_name, document_count)
        
        # Update document count in selector
        self.doc_count_label.setText(f"Documents: {document_count}")
    
    def populate_documents(self, documents: list[dict[str, Any]]) -> None:
        """Populate documents in the current view."""
        import logging
        logger = logging.getLogger(__name__)
        
        self.current_documents = documents if documents else []
        
        logger.debug(f"Populating {self.current_view} view with {len(self.current_documents)} documents")
        
        if self.current_view == "table":
            self.data_table.populate_documents(documents)
        else:
            self.object_view.populate_documents(documents)
    
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
