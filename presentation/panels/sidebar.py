"""
Sidebar Component
Handles the left panel with databases and collections tree view.
"""

from __future__ import annotations

from typing import Any

import qtawesome as fa
from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QMenu, QPushButton, QSizePolicy, QTreeWidget,
    QTreeWidgetItem, QVBoxLayout, QWidget
)

# Import styles at module level
from ..styles.styles import BUTTON_STYLES, LABEL_STYLES, SIDEBAR_TREE_STYLE, CONTEXT_MENU_STYLE


class Sidebar(QObject):
    """Sidebar component for displaying databases and collections."""
    
    # Signals
    database_selected = Signal(str)  # Emits database name
    collection_selected = Signal(str, str)  # Emits database name, collection name
    refresh_requested = Signal()
    add_database_requested = Signal()
    
    # Context menu action signals
    rename_database_requested = Signal(str)  # Emits database name
    delete_database_requested = Signal(str)  # Emits database name
    add_collection_requested = Signal(str)   # Emits database name
    rename_collection_requested = Signal(str, str)  # Emits database name, collection name
    delete_collection_requested = Signal(str, str)  # Emits database name, collection name
    insert_document_requested = Signal(str, str)  # Emits database name, collection name
    
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.parent = parent
        self.widget: QWidget | None = None
        self.db_tree: QTreeWidget | None = None
        self.db_count_label: QLabel | None = None
        self.selected_db_label: QLabel | None = None
        self.collection_count_label: QLabel | None = None
        self._create_sidebar()
    
    def _create_sidebar(self) -> None:
        """Create the sidebar widget with database tree and controls."""
        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)
        layout.setSpacing(8)
        layout.setContentsMargins(6, 6, 6, 6)
        
        self._create_header(layout)
        self._create_action_buttons(layout)
        self._create_database_tree(layout)
        self._create_status_section(layout)
    
    def _create_header(self, parent_layout: QVBoxLayout) -> None:
        """Create the header section with title and database count."""
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        # Databases label
        db_label = QLabel("Databases & Collections")
        db_label.setFont(QFont("Arial", 12, QFont.Bold))
        db_label.setStyleSheet(LABEL_STYLES['header'])
        db_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        header_layout.addWidget(db_label)
        
        # Database count label
        self.db_count_label = QLabel("0 databases")
        self.db_count_label.setStyleSheet(LABEL_STYLES['muted'])
        self.db_count_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        header_layout.addWidget(self.db_count_label)
        
        parent_layout.addLayout(header_layout)
    
    def _create_action_buttons(self, parent_layout: QVBoxLayout) -> None:
        """Create action buttons for database operations."""
        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)
        
        # Refresh button - modern flat style with better contrast
        refresh_button = QPushButton(fa.icon('fa6s.arrows-rotate', color='#6b7280'), " Refresh")
        refresh_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        refresh_button.setMinimumHeight(24)
        refresh_button.setMinimumWidth(70)
        refresh_button.clicked.connect(self._on_refresh_clicked)
        refresh_button.setStyleSheet(BUTTON_STYLES['refresh_secondary'])  # Use secondary refresh style
        
        # Add database button - modern flat style with accent
        add_db_button = QPushButton(fa.icon('fa6s.plus'), " Add DB")
        add_db_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        add_db_button.setMinimumHeight(24)
        add_db_button.setMinimumWidth(70)
        add_db_button.clicked.connect(self.add_database_requested.emit)
        add_db_button.setStyleSheet(BUTTON_STYLES['flat_accent'])
        
        action_layout.addWidget(refresh_button)
        action_layout.addWidget(add_db_button)
        action_layout.addStretch()
        
        parent_layout.addLayout(action_layout)
    
    def _on_refresh_clicked(self):
        """Handle refresh button click with logging."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info("[UI] Refresh button clicked")
        self.refresh_requested.emit()
    
    def _create_database_tree(self, parent_layout: QVBoxLayout) -> None:
        """Create the tree widget for databases and collections."""
        self.db_tree = QTreeWidget()
        self.db_tree.setHeaderLabel("Databases")
        self.db_tree.setAlternatingRowColors(True)
        self.db_tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.db_tree.setMinimumHeight(250)
        self.db_tree.setStyleSheet(SIDEBAR_TREE_STYLE)
        
        # Enable context menu for right-click actions
        self.db_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.db_tree.customContextMenuRequested.connect(self._show_context_menu)
        
        # Connect item selection
        self.db_tree.itemClicked.connect(self._on_tree_item_clicked)
        
        parent_layout.addWidget(self.db_tree)
    
    def _create_status_section(self, parent_layout: QVBoxLayout) -> None:
        """Create the status section at the bottom of sidebar."""
        db_status_layout = QHBoxLayout()
        db_status_layout.setSpacing(8)
        
        # Selected database info
        self.selected_db_label = QLabel("No database selected")
        self.selected_db_label.setStyleSheet(LABEL_STYLES['subheader'])
        self.selected_db_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Collection count
        self.collection_count_label = QLabel("0 collections")
        self.collection_count_label.setStyleSheet(LABEL_STYLES['muted'])
        self.collection_count_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
        db_status_layout.addWidget(self.selected_db_label)
        db_status_layout.addWidget(self.collection_count_label)
        
        parent_layout.addLayout(db_status_layout)
    
    def _show_context_menu(self, position: Any) -> None:
        """Show context menu for database operations."""
        import logging
        logger = logging.getLogger(__name__)
        
        if not self.db_tree:
            return
        
        # Get the item at the clicked position
        item = self.db_tree.itemAt(position)
        if not item:
            return
        
        # Create context menu
        context_menu = QMenu(self.db_tree)
        context_menu.setStyleSheet(self._get_context_menu_style())
        
        # Get item data
        item_data = item.data(0, Qt.UserRole)
        if not item_data:
            return
        
        item_type = item_data.get("type")
        logger.debug(f"Showing context menu for {item_type}: {item_data}")
        
        if item_type == "database":
            # Database context menu
            database_name = item_data.get("name")
            
            # Add Collection action
            add_collection_action = QAction(fa.icon('fa6s.plus', color='#10b981'), "Add Collection", context_menu)
            add_collection_action.triggered.connect(lambda: self._handle_add_collection(database_name))
            context_menu.addAction(add_collection_action)
            
            context_menu.addSeparator()
            
            # Rename Database action
            rename_action = QAction(fa.icon('fa6s.pen', color='#3b82f6'), "Rename Database", context_menu)
            rename_action.triggered.connect(lambda: self._handle_rename_database(database_name))
            context_menu.addAction(rename_action)
            
            # Delete Database action
            delete_action = QAction(fa.icon('fa6s.trash', color='#ef4444'), "Delete Database", context_menu)
            delete_action.triggered.connect(lambda: self._handle_delete_database(database_name))
            context_menu.addAction(delete_action)
            
        elif item_type == "collection":
            # Collection context menu
            collection_name = item_data.get("name")
            database_name = item_data.get("database")
            
            # Insert Document action
            insert_action = QAction(fa.icon('fa6s.plus', color='#10b981'), "Insert Document", context_menu)
            insert_action.triggered.connect(lambda: self._handle_insert_document(database_name, collection_name))
            context_menu.addAction(insert_action)
            
            context_menu.addSeparator()
            
            # Rename Collection action
            rename_action = QAction(fa.icon('fa6s.pen', color='#3b82f6'), "Rename Collection", context_menu)
            rename_action.triggered.connect(lambda: self._handle_rename_collection(database_name, collection_name))
            context_menu.addAction(rename_action)
            
            # Delete Collection action
            delete_action = QAction(fa.icon('fa6s.trash', color='#ef4444'), "Delete Collection", context_menu)
            delete_action.triggered.connect(lambda: self._handle_delete_collection(database_name, collection_name))
            context_menu.addAction(delete_action)
        
        # Show the context menu close to the item
        if context_menu.actions():
            # Position the menu close to the clicked item
            global_pos = self.db_tree.mapToGlobal(position)
            context_menu.exec_(global_pos)
    
    def _handle_add_collection(self, database_name: str) -> None:
        """Handle add collection action with logging."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Add collection requested for database: {database_name}")
        self.add_collection_requested.emit(database_name)
    
    def _handle_rename_database(self, database_name: str) -> None:
        """Handle rename database action with logging."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Rename database requested: {database_name}")
        self.rename_database_requested.emit(database_name)
    
    def _handle_delete_database(self, database_name: str) -> None:
        """Handle delete database action with logging."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Delete database requested: {database_name}")
        self.delete_database_requested.emit(database_name)
    
    def _handle_insert_document(self, database_name: str, collection_name: str) -> None:
        """Handle insert document action with logging."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Insert document requested for {database_name}/{collection_name}")
        self.insert_document_requested.emit(database_name, collection_name)
    
    def _handle_rename_collection(self, database_name: str, collection_name: str) -> None:
        """Handle rename collection action with logging."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Rename collection requested: {database_name}/{collection_name}")
        self.rename_collection_requested.emit(database_name, collection_name)
    
    def _handle_delete_collection(self, database_name: str, collection_name: str) -> None:
        """Handle delete collection action with logging."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Delete collection requested: {database_name}/{collection_name}")
        self.delete_collection_requested.emit(database_name, collection_name)
    
    def _get_context_menu_style(self) -> str:
        """Get the context menu stylesheet."""
        return CONTEXT_MENU_STYLE
    
    def _on_tree_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """Handle tree item selection."""
        parent = item.parent()
        if parent is None:
            # Database selected
            database_name = item.text(0).split(' (')[0].strip()  # Remove collection count and spaces
            self.database_selected.emit(database_name)
        else:
            # Collection selected
            database_name = parent.text(0).split(' (')[0].strip()  # Remove collection count and spaces
            collection_name = item.text(0).strip()  # Remove leading/trailing spaces
            self.collection_selected.emit(database_name, collection_name)
    
    def get_widget(self) -> QWidget | None:
        """Get the sidebar widget."""
        return self.widget
    
    def get_tree_widget(self) -> QTreeWidget | None:
        """Get the database tree widget."""
        return self.db_tree
    
    def clear_tree(self) -> None:
        """Clear the database tree."""
        if self.db_tree:
            self.db_tree.clear()
    
    def add_database(self, database_name: str, collections: list[str] | None = None) -> None:
        """Add a database to the tree."""
        if not self.db_tree:
            return
        
        import logging
        logger = logging.getLogger(__name__)
        
        # Clean the database name (remove leading/trailing spaces)
        clean_db_name = database_name.strip()
        
        # Check if database already exists
        if self.database_exists(clean_db_name):
            logger.debug(f"Database '{clean_db_name}' already exists in sidebar, skipping duplicate")
            return
        
        # Create database item with icon
        db_item = QTreeWidgetItem(self.db_tree, [f"  {clean_db_name}"])
        db_item.setIcon(0, fa.icon('fa6s.database'))
        db_item.setData(0, Qt.UserRole, {"type": "database", "name": clean_db_name})
        
        # Add collections if provided
        if collections:
            collection_count = len(collections)
            for coll_name in collections:
                # Clean the collection name (remove leading/trailing spaces)
                clean_coll_name = coll_name.strip()
                coll_item = QTreeWidgetItem(db_item, [f"  {clean_coll_name}"])
                coll_item.setIcon(0, fa.icon('fa6s.folder'))
                coll_item.setData(0, Qt.UserRole, {
                    "type": "collection", 
                    "name": clean_coll_name, 
                    "database": clean_db_name
                })
            
            # Add collection count to database item
            if collection_count > 0:
                db_item.setText(0, f"  {clean_db_name} ({collection_count} collections)")
        
        logger.debug(f"Added database '{clean_db_name}' to sidebar with {len(collections) if collections else 0} collections")
    
    def add_single_database(self, database_name: str, collections: list[str] | None = None) -> bool:
        """Add a single database to the sidebar without clearing the tree."""
        if not self.db_tree:
            return False
        
        import logging
        logger = logging.getLogger(__name__)
        
        # Clean the database name (remove leading/trailing spaces)
        clean_db_name = database_name.strip()
        
        # Check if database already exists
        if self.database_exists(clean_db_name):
            logger.debug(f"Database '{clean_db_name}' already exists in sidebar, skipping duplicate")
            return False
        
        try:
            # Create database item with icon
            db_item = QTreeWidgetItem(self.db_tree, [f"  {clean_db_name}"])
            db_item.setIcon(0, fa.icon('fa6s.database'))
            db_item.setData(0, Qt.UserRole, {"type": "database", "name": clean_db_name})
            
            # Add collections if provided
            if collections:
                collection_count = len(collections)
                for coll_name in collections:
                    # Clean the collection name (remove leading/trailing spaces)
                    clean_coll_name = coll_name.strip()
                    coll_item = QTreeWidgetItem(db_item, [f"  {clean_coll_name}"])
                    coll_item.setIcon(0, fa.icon('fa6s.folder'))
                    coll_item.setData(0, Qt.UserRole, {
                        "type": "collection", 
                        "name": clean_coll_name, 
                        "database": clean_db_name
                    })
                
                # Add collection count to database item
                if collection_count > 0:
                    db_item.setText(0, f"  {clean_db_name} ({collection_count} collections)")
            
            # Expand the new database item
            db_item.setExpanded(True)
            
            # Update database count
            current_count = self.db_tree.topLevelItemCount()
            self.update_database_count(current_count)
            
            logger.info(f"Added single database '{clean_db_name}' to sidebar with {len(collections) if collections else 0} collections")
            return True
            
        except Exception as e:
            logger.error(f"Error adding single database '{clean_db_name}' to sidebar: {e}")
            return False
    
    def database_exists(self, database_name: str) -> bool:
        """Check if a database already exists in the sidebar."""
        if not self.db_tree:
            return False
        
        try:
            # Find the database item
            for i in range(self.db_tree.topLevelItemCount()):
                db_item = self.db_tree.topLevelItem(i)
                db_data = db_item.data(0, Qt.UserRole)
                
                if db_data and db_data.get("name") == database_name:
                    return True
            
            return False
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error checking if database {database_name} exists: {e}")
            return False
    
    def select_database(self, database_name: str) -> bool:
        """Select a specific database in the tree."""
        if not self.db_tree:
            return False
        
        try:
            # Find the database item
            for i in range(self.db_tree.topLevelItemCount()):
                db_item = self.db_tree.topLevelItem(i)
                db_data = db_item.data(0, Qt.UserRole)
                
                if db_data and db_data.get("name") == database_name:
                    # Select the database item
                    self.db_tree.setCurrentItem(db_item)
                    self.db_tree.scrollToItem(db_item)
                    
                    # Update the selected database label
                    self.update_selected_database(database_name)
                    
                    return True
            
            return False
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error selecting database {database_name}: {e}")
            return False
    
    def update_database_count(self, count: int) -> None:
        """Update the database count label."""
        if self.db_count_label:
            self.db_count_label.setText(f"{count} databases")
    
    def update_selected_database(self, database_name: str) -> None:
        """Update the selected database label."""
        if self.selected_db_label:
            self.selected_db_label.setText(f"Selected: {database_name}")
    
    def update_collection_count(self, count: int) -> None:
        """Update the collection count label."""
        if self.collection_count_label:
            self.collection_count_label.setText(f"{count} collections")
    
    def expand_all(self) -> None:
        """Expand all items in the tree."""
        if self.db_tree:
            self.db_tree.expandAll()
    
    def set_loading_state(self, loading: bool) -> None:
        """Set the loading state for the sidebar."""
        if loading:
            self.db_count_label.setText("Loading databases...")
            self.db_count_label.setStyleSheet("color: #007bff; font-weight: bold;")
        else:
            self.db_count_label.setStyleSheet("color: #6c757d; font-size: 11px; font-style: italic;")
    
    def set_error_state(self, error_message: str) -> None:
        """Set the error state for the sidebar."""
        self.db_count_label.setText("Error loading databases")
        self.db_count_label.setStyleSheet("color: #dc3545; font-weight: bold;")
    
    def select_collection(self, database_name: str, collection_name: str) -> bool:
        """Select a specific collection in the tree."""
        if not self.db_tree:
            return False
        
        try:
            # Find the database item
            for i in range(self.db_tree.topLevelItemCount()):
                db_item = self.db_tree.topLevelItem(i)
                db_data = db_item.data(0, Qt.UserRole)
                
                if db_data and db_data.get("name") == database_name:
                    # Find the collection item
                    for j in range(db_item.childCount()):
                        coll_item = db_item.child(j)
                        coll_data = coll_item.data(0, Qt.UserRole)
                        
                        if coll_data and coll_data.get("name") == collection_name:
                            # Select the collection item
                            self.db_tree.setCurrentItem(coll_item)
                            self.db_tree.scrollToItem(coll_item)
                            return True
            
            return False
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error selecting collection {database_name}/{collection_name}: {e}")
            return False
