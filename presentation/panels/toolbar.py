"""
Toolbar Component
Handles the main toolbar with text-only buttons for common operations.
"""

from __future__ import annotations

from typing import Any, Callable

import qtawesome as fa
from PySide6.QtCore import QObject
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QToolBar


class ToolBar(QObject):
    """Main toolbar for AtlasMogo application."""
    
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.parent = parent
        self.toolbar: QToolBar | None = None
        self.actions: dict[str, QAction] = {}
        self._create_toolbar()
    
    def _create_toolbar(self) -> None:
        """Create the main toolbar with common actions."""
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setMovable(True)
        self.toolbar.setFloatable(False)
        
        self._add_connection_actions()
        self._add_database_actions()
        self._add_document_actions()
        self._add_query_actions()
    
    def _add_connection_actions(self) -> None:
        """Add connection-related actions to toolbar."""
        self.toolbar.addSeparator()
        
        # Connect action
        connect_action = QAction("Connect", self.parent)
        connect_action.setStatusTip("Connect to MongoDB")
        self.actions['connect'] = connect_action
        self.toolbar.addAction(connect_action)
        
        # Disconnect action
        disconnect_action = QAction("Disconnect", self.parent)
        disconnect_action.setStatusTip("Disconnect from MongoDB")
        self.actions['disconnect'] = disconnect_action
        self.toolbar.addAction(disconnect_action)
        
        self.toolbar.addSeparator()
    
    def _add_database_actions(self) -> None:
        """Add database-related actions to toolbar."""
        # Create Database action
        create_db_action = QAction(fa.icon('fa6s.plus'), "Create Database", self.parent)
        create_db_action.setStatusTip("Create a new database")
        self.actions['create_database'] = create_db_action
        self.toolbar.addAction(create_db_action)
        
        # Add Collection action
        add_collection_action = QAction(fa.icon('fa6s.folder-plus'), "Add Collection", self.parent)
        add_collection_action.setStatusTip("Create a new collection")
        self.actions['add_collection'] = add_collection_action
        self.toolbar.addAction(add_collection_action)
        
        self.toolbar.addSeparator()
    
    def _add_document_actions(self) -> None:
        """Add document-related actions to toolbar."""
        # Insert action
        insert_action = QAction(fa.icon('fa6s.plus'), "Insert", self.parent)
        insert_action.setStatusTip("Insert a new document")
        self.actions['insert'] = insert_action
        self.toolbar.addAction(insert_action)
        
        # Delete action
        delete_action = QAction(fa.icon('fa6s.trash'), "Delete", self.parent)
        delete_action.setStatusTip("Delete a document")
        self.actions['delete'] = delete_action
        self.toolbar.addAction(delete_action)
        
        self.toolbar.addSeparator()
    
    def _add_query_actions(self) -> None:
        """Add query-related actions to toolbar."""
        # Query action
        query_action = QAction(fa.icon('fa6s.magnifying-glass'), "Query", self.parent)
        query_action.setStatusTip("Execute a query")
        self.actions['query'] = query_action
        self.toolbar.addAction(query_action)
        
        # Refresh action
        refresh_action = QAction(fa.icon('fa6s.arrows-rotate'), "Refresh", self.parent)
        refresh_action.setStatusTip("Refresh data")
        self.actions['refresh'] = refresh_action
        self.toolbar.addAction(refresh_action)
    
    def get_toolbar(self) -> QToolBar | None:
        """Get the created toolbar."""
        return self.toolbar
    
    def get_action(self, action_name: str) -> QAction | None:
        """Get a specific action by name."""
        return self.actions.get(action_name)
    
    def connect_action(self, action_name: str, slot: Callable[[], Any]) -> None:
        """Connect an action to a slot function."""
        action = self.actions.get(action_name)
        if action:
            action.triggered.connect(slot)
    
    def enable_action(self, action_name: str, enabled: bool = True) -> None:
        """Enable or disable a specific action."""
        action = self.actions.get(action_name)
        if action:
            action.setEnabled(enabled)
    
    def set_action_text(self, action_name: str, text: str) -> None:
        """Set the text for a specific action."""
        action = self.actions.get(action_name)
        if action:
            action.setText(text)
    
    def update_toolbar_state(self, connected: bool) -> None:
        """Update toolbar button states based on connection status."""
        if connected:
            self.enable_action('connect', False)
            self.enable_action('disconnect', True)
            self.enable_action('create_database', True)
            self.enable_action('add_collection', True)
            self.enable_action('insert', True)
            self.enable_action('delete', True)
            self.enable_action('query', True)
            self.enable_action('refresh', True)
        else:
            self.enable_action('connect', True)
            self.enable_action('disconnect', False)
            self.enable_action('create_database', False)
            self.enable_action('add_collection', False)
            self.enable_action('insert', False)
            self.enable_action('delete', False)
            self.enable_action('query', False)
            self.enable_action('refresh', False)
