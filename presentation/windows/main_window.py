"""
Main Window
Primary GUI interface for AtlasMogo MongoDB management tool.
Integrates all modular UI components.
"""

import sys
import json
from typing import List, Dict, Any
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QSplitter, QTabWidget,
    QApplication, QSizePolicy, QDialog, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QIcon

# Import modular components
from ..panels.menu_bar import MenuBar
from ..panels.toolbar import ToolBar
from ..panels.connection_panel import ConnectionPanel
from ..panels.sidebar import Sidebar
from ..panels.document_view_manager import DocumentViewManager
from ..panels.operations_panel import OperationsPanel
from ..panels.query_panel import QueryPanel
from ..panels.status_bar import StatusBar

# Import dialogs
from ..dialogs.dialogs import (
    CreateDatabaseDialog, CreateCollectionDialog, InsertDocumentDialog,
    QueryBuilderDialog, SettingsDialog, ExportDataDialog
)

# Import helpers
from ..dialogs.message_box_helper import MessageBoxHelper

from business.mongo_service import MongoService


class ConnectionWorker(QThread):
    """Worker thread for MongoDB connection operations."""
    
    connection_result = Signal(bool, str)
    
    def __init__(self, service: MongoService, connection_string: str):
        super().__init__()
        self.service = service
        self.connection_string = connection_string
    
    def run(self):
        """Execute the connection operation."""
        success, message = self.service.connect_to_mongodb(self.connection_string)
        self.connection_result.emit(success, message)


class MainWindow(QMainWindow):
    """Main application window for AtlasMogo."""
    
    def __init__(self):
        super().__init__()
        self.mongo_service = MongoService()
        self.current_database = ""
        self.current_collection = ""
        self.connection_state = "disconnected"
        
        # Initialize UI components
        self.menu_bar_component = None
        self.toolbar_component = None
        self.connection_panel = None
        self.sidebar = None
        self.document_view_manager = None
        self.operations_panel = None
        self.query_panel = None
        self.status_bar_component = None
        
        self.init_ui()
        self.setup_connections()
        self.apply_styles()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("AtlasMogo - MongoDB Management Tool")
        
        # Set application icon
        self._set_window_icon()
        
        # Get screen geometry and calculate optimal window size
        screen = QApplication.primaryScreen().geometry()
        taskbar_height = 40
        available_height = screen.height() - taskbar_height - 80
        
        # Set window size with responsive height
        window_width = min(1200, screen.width() - 80)
        window_height = min(800, available_height)
        
        # Center the window on screen
        x = (screen.width() - window_width) // 2
        y = (screen.height() - window_height) // 2
        self.setGeometry(x, y, window_width, window_height)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(6)
        main_layout.setContentsMargins(6, 6, 6, 6)
        
        # Create and add UI components
        self._create_ui_components(main_layout)
        
        # Set size policies for responsive behavior
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Connect resize event for dynamic layout adjustment
        self.resizeEvent = self.on_resize_event
    
    def _set_window_icon(self):
        """Set the application window icon."""
        import logging
        import os
        from pathlib import Path
        
        logger = logging.getLogger(__name__)
        
        # Try multiple paths for the icon file
        icon_paths = [
            "resources/icons/icon.ico",  # Relative to current directory
            os.path.join(os.path.dirname(__file__), "..", "..", "resources", "icons", "icon.ico"),  # Relative to this file
            os.path.join(os.getcwd(), "resources", "icons", "icon.ico"),  # Relative to working directory
        ]
        
        # For PyInstaller bundled app
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            base_path = sys._MEIPASS
            icon_paths.insert(0, os.path.join(base_path, "resources", "icons", "icon.ico"))
        
        icon_set = False
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                try:
                    self.setWindowIcon(QIcon(icon_path))
                    logger.info(f"App icon loaded from {icon_path}")
                    icon_set = True
                    break
                except Exception as e:
                    logger.warning(f"Failed to load icon from {icon_path}: {e}")
                    continue
        
        if not icon_set:
            logger.error("Could not load application icon from any of the expected paths")
    
    def _create_ui_components(self, main_layout):
        """Create and integrate all UI components."""
        # Create connection panel
        self.connection_panel = ConnectionPanel(self)
        main_layout.addWidget(self.connection_panel.get_widget())
        
        # Create main splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.setChildrenCollapsible(False)
        self.main_splitter.setHandleWidth(3)
        main_layout.addWidget(self.main_splitter)
        
        # Create left panel (sidebar)
        self.sidebar = Sidebar(self)
        self.main_splitter.addWidget(self.sidebar.get_widget())
        
        # Create right panel (tabs)
        self._create_right_panel()
        
        # Set responsive splitter proportions
        total_width = self.width() - 12
        left_width = int(total_width * 0.35)
        right_width = total_width - left_width
        self.main_splitter.setSizes([left_width, right_width])
        
        # Create menu bar
        self.menu_bar_component = MenuBar(self)
        self.setMenuBar(self.menu_bar_component.get_menu_bar())
        
        # Create toolbar
        self.toolbar_component = ToolBar(self)
        self.addToolBar(self.toolbar_component.get_toolbar())
        
        # Create status bar
        self.status_bar_component = StatusBar(self)
        self.setStatusBar(self.status_bar_component.get_status_bar())
    
    def _create_right_panel(self):
        """Create the right panel with tabs."""
        self.tab_widget = QTabWidget()
        self.tab_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Documents tab
        self.document_view_manager = DocumentViewManager(self)
        self.tab_widget.addTab(self.document_view_manager.get_widget(), "Documents")
        
        # Operations tab
        self.operations_panel = OperationsPanel(self)
        self.tab_widget.addTab(self.operations_panel.get_widget(), "Operations")
        
        # Query tab
        self.query_panel = QueryPanel(self)
        self.tab_widget.addTab(self.query_panel.get_widget(), "Query")
        
        self.main_splitter.addWidget(self.tab_widget)
    
    def setup_connections(self):
        """Setup signal connections between components."""
        # Connection panel signals
        self.connection_panel.connect_requested.connect(self.connect_to_mongodb)
        self.connection_panel.disconnect_requested.connect(self.disconnect_from_mongodb)
        self.connection_panel.test_requested.connect(self.test_connection)
        
        # Sidebar signals
        self.sidebar.database_selected.connect(self.on_database_selected)
        self.sidebar.collection_selected.connect(self.on_collection_selected)
        self.sidebar.refresh_requested.connect(self.refresh_databases)
        self.sidebar.add_database_requested.connect(self.on_add_database)
        
        # Context menu signals
        self.sidebar.rename_database_requested.connect(self.on_rename_database)
        self.sidebar.delete_database_requested.connect(self.on_delete_database)
        self.sidebar.add_collection_requested.connect(self.on_add_collection)
        self.sidebar.rename_collection_requested.connect(self.on_rename_collection)
        self.sidebar.delete_collection_requested.connect(self.on_delete_collection)
        self.sidebar.insert_document_requested.connect(self.on_insert_document_from_context)
        
        # Document view manager signals
        self.document_view_manager.refresh_requested.connect(self.refresh_documents)
        self.document_view_manager.view_document_requested.connect(self.on_view_document)
        self.document_view_manager.edit_document_requested.connect(self.on_edit_document)
        self.document_view_manager.delete_document_requested.connect(self.on_delete_document_from_context)
        
        # Operations panel signals
        self.operations_panel.insert_requested.connect(self.insert_document)
        self.operations_panel.update_requested.connect(self.update_document)
        self.operations_panel.delete_requested.connect(self.delete_document)
        
        # Query panel signals
        self.query_panel.query_executed.connect(self.execute_query)
        
        # Menu bar signals
        self._connect_menu_actions()
        
        # Toolbar signals
        self._connect_toolbar_actions()
    
    def _connect_menu_actions(self):
        """Connect menu actions to their handlers."""
        self.menu_bar_component.connect_action('new_connection', self.on_new_connection)
        self.menu_bar_component.connect_action('open_connection', self.on_open_connection)
        self.menu_bar_component.connect_action('export_data', self.on_export_data)
        self.menu_bar_component.connect_action('import_data', self.on_import_data)
        self.menu_bar_component.connect_action('exit', self.close)
        self.menu_bar_component.connect_action('create_database', self.on_create_database)
        self.menu_bar_component.connect_action('list_databases', self.on_list_databases)
        self.menu_bar_component.connect_action('rename_database', self.on_rename_database)
        self.menu_bar_component.connect_action('delete_database', self.on_delete_database)
        self.menu_bar_component.connect_action('add_collection', self.on_add_collection)
        self.menu_bar_component.connect_action('refresh', self.refresh_databases)
        self.menu_bar_component.connect_action('query_builder', self.on_query_builder)
        self.menu_bar_component.connect_action('performance_monitor', self.on_performance_monitor)
        self.menu_bar_component.connect_action('settings', self.on_settings)
        self.menu_bar_component.connect_action('documentation', self.on_documentation)
        self.menu_bar_component.connect_action('about', self.show_about)
    
    def _connect_toolbar_actions(self):
        """Connect toolbar actions to their handlers."""
        self.toolbar_component.connect_action('connect', self.connect_to_mongodb)
        self.toolbar_component.connect_action('disconnect', self.disconnect_from_mongodb)
        self.toolbar_component.connect_action('create_database', self.on_create_database)
        self.toolbar_component.connect_action('list_databases', self.on_list_databases)
        self.toolbar_component.connect_action('rename_database', self.on_rename_database)
        self.toolbar_component.connect_action('delete_database', self.on_delete_database)
        self.toolbar_component.connect_action('add_collection', self.on_add_collection)
        self.toolbar_component.connect_action('insert', self.on_insert_document)
        self.toolbar_component.connect_action('update', self.on_update_document)
        self.toolbar_component.connect_action('delete', self.on_delete_document)
        self.toolbar_component.connect_action('query', self.on_execute_query)
        self.toolbar_component.connect_action('refresh', self.refresh_databases)
    
    def connect_to_mongodb(self, connection_string: str):
        """Connect to MongoDB using the connection string."""
        if not connection_string:
            MessageBoxHelper.warning(self, "Connection Error", "Please enter a connection string.")
            return
        
        # Update connection state and UI
        self.connection_state = "connecting"
        self.connection_panel.set_connection_state("connecting")
        self.status_bar_component.show_progress(True)
        self.status_bar_component.set_indeterminate_progress(True)
        
        # Create worker thread
        self.connection_worker = ConnectionWorker(self.mongo_service, connection_string)
        self.connection_worker.connection_result.connect(self.on_connection_result)
        self.connection_worker.start()
    
    def test_connection(self, connection_string: str):
        """Test MongoDB connection without establishing a full connection."""
        if not connection_string:
            MessageBoxHelper.warning(self, "Test Error", "Please enter a connection string.")
            return
        
        # Update UI for testing
        self.connection_panel.set_connection_state("connecting")
        
        # Create a temporary connection for testing
        try:
            from pymongo import MongoClient
            from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
            
            # Test connection with short timeout
            test_client = MongoClient(connection_string, serverSelectionTimeoutMS=3000)
            test_client.admin.command('ping')
            test_client.close()
            
            # Success
            self.connection_panel.set_test_result(True, "Connection test successful!")
            MessageBoxHelper.information(self, "Test Result", "Connection test successful! MongoDB server is reachable.")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            # Connection failed
            self.connection_panel.set_test_result(False, f"Connection test failed: {str(e)}")
            MessageBoxHelper.critical(self, "Test Result", f"Connection test failed: {str(e)}")
            
        except Exception as e:
            # Other error
            self.connection_panel.set_test_result(False, f"Unexpected error: {str(e)}")
            MessageBoxHelper.critical(self, "Test Result", f"Unexpected error: {str(e)}")
        
        finally:
            # Reset message after a delay
            QTimer.singleShot(3000, lambda: self.connection_panel.reset_message())
    
    def on_connection_result(self, success: bool, message: str):
        """Handle connection result."""
        self.status_bar_component.show_progress(False)
        
        if success:
            self.connection_state = "connected"
            self.connection_panel.set_connection_state("connected")
            self.status_bar_component.set_connection_status("Connected", "green")
            self.status_bar_component.show_message(f"Connected successfully: {message}", 5000)
            
            # Update toolbar state
            self.toolbar_component.update_toolbar_state(True)
            
            # Refresh databases
            self.refresh_databases()
            
            # Show success message
            MessageBoxHelper.information(self, "Connection Success", 
                                  f"Successfully connected to MongoDB!\n\n{message}")
        else:
            self.connection_state = "failed"
            self.connection_panel.set_connection_state("failed")
            self.status_bar_component.set_connection_status("Connection Failed", "red")
            
            # Show error message
            MessageBoxHelper.critical(self, "Connection Error", 
                               f"Failed to connect to MongoDB:\n\n{message}")
            
            # Update status bar
            self.status_bar_component.show_message(f"Connection failed: {message}", 5000)
            
            # Update toolbar state
            self.toolbar_component.update_toolbar_state(False)
    
    def disconnect_from_mongodb(self):
        """Disconnect from MongoDB."""
        try:
            self.mongo_service.disconnect_from_mongodb()
            
            # Update connection state
            self.connection_state = "disconnected"
            self.connection_panel.set_connection_state("disconnected")
            self.status_bar_component.set_connection_status("Disconnected", "red")
            
            # Clear UI state
            self.sidebar.clear_tree()
            self.current_database = ""
            self.current_collection = ""
            
            # Reset labels
            self.sidebar.update_selected_database("No database selected")
            self.sidebar.update_collection_count(0)
            self.document_view_manager.clear_views()
            
            # Update status bar
            self.status_bar_component.show_message("Disconnected from MongoDB", 3000)
            
            # Update toolbar state
            self.toolbar_component.update_toolbar_state(False)
            
            # Show disconnection message
            MessageBoxHelper.information(self, "Disconnected", "Successfully disconnected from MongoDB.")
            
        except Exception as e:
            MessageBoxHelper.warning(self, "Disconnect Warning", f"Error during disconnect: {str(e)}")
    
    def refresh_databases(self):
        """Refresh the databases tree."""
        if not self.mongo_service.is_connected():
            MessageBoxHelper.warning(self, "Not Connected", "Please connect to MongoDB first.")
            return
        
        # Show loading state
        self.sidebar.set_loading_state(True)
        
        try:
            # Clear existing tree
            self.sidebar.clear_tree()
            
            # Get databases
            databases = self.mongo_service.get_databases()
            user_databases = [db for db in databases if db not in ['admin', 'local', 'config']]
            
            # Update database count
            self.sidebar.update_database_count(len(user_databases))
            
            # Populate tree
            for db_name in user_databases:
                try:
                    collections = self.mongo_service.get_collections(db_name)
                    self.sidebar.add_database(db_name, collections)
                except Exception as e:
                    # Handle collection loading errors
                    self.sidebar.add_database(db_name, [])
            
            # Expand all items
            self.sidebar.expand_all()
            
            # Update status
            status_msg = f"Refreshed {len(user_databases)} databases"
            self.status_bar_component.show_message(status_msg, 3000)
            
            # Show warning if no user databases found
            if len(user_databases) == 0:
                self.status_bar_component.show_message("No user databases found. System databases (admin, local, config) are hidden.", 5000)
            
        except Exception as e:
            # Handle database loading errors
            error_msg = f"Failed to load databases: {str(e)}"
            self.sidebar.set_error_state(str(e))
            MessageBoxHelper.critical(self, "Database Error", error_msg)
            self.status_bar_component.show_message(f"Failed to refresh databases: {str(e)}", 5000)
        
        finally:
            self.sidebar.set_loading_state(False)
    
    def select_collection_in_sidebar(self, database_name: str, collection_name: str):
        """Select a specific collection in the sidebar after refresh."""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Find and select the collection in the sidebar
            success = self.sidebar.select_collection(database_name, collection_name)
            if success:
                logger.info(f"Successfully selected collection {database_name}/{collection_name} in sidebar")
                # Trigger collection selection to load documents
                self.on_collection_selected(database_name, collection_name)
            else:
                logger.warning(f"Could not select collection {database_name}/{collection_name} in sidebar")
        except Exception as e:
            logger.error(f"Error selecting collection in sidebar: {e}")
            # Fallback: just trigger collection selection
            self.on_collection_selected(database_name, collection_name)
    
    def on_database_selected(self, database_name: str):
        """Handle database selection."""
        import logging
        logger = logging.getLogger(__name__)
        
        self.current_database = database_name
        self.current_collection = ""
        
        logger.info(f"Database selected: {database_name}")
        
        # Update labels
        self.document_view_manager.set_collection_info("None selected", 0)
        self.sidebar.update_selected_database(database_name)
        
        # Get collection count for this database
        try:
            collections = self.mongo_service.get_collections(database_name)
            collection_count = len(collections)
            logger.debug(f"Database {database_name} has {collection_count} collections")
            self.sidebar.update_collection_count(collection_count)
            
            # Clear documents table
            self.document_view_manager.clear_views()
            
        except Exception as e:
            logger.error(f"Failed to get collections for database {database_name}: {e}")
            self.sidebar.update_collection_count(0)
        
        # Update status bar
        self.status_bar_component.show_message(f"Selected database: {database_name}", 2000)
    
    def on_collection_selected(self, database_name: str, collection_name: str):
        """Handle collection selection."""
        import logging
        logger = logging.getLogger(__name__)
        
        self.current_database = database_name
        self.current_collection = collection_name
        
        logger.info(f"Collection selected: {database_name}/{collection_name}")
        
        # Update labels
        self.document_view_manager.set_collection_info(collection_name, 0)
        self.sidebar.update_selected_database(f"{database_name} > {collection_name}")
        
        # Get document count and load documents
        try:
            count = self.mongo_service.count_documents(database_name, collection_name)
            logger.debug(f"Collection {collection_name} has {count} documents")
            self.document_view_manager.set_collection_info(collection_name, count)
            
            # Load documents
            self.refresh_documents()
            
        except Exception as e:
            logger.error(f"Failed to load documents for {database_name}/{collection_name}: {e}")
            self.document_view_manager.set_collection_info(collection_name, 0)
            MessageBoxHelper.warning(self, "Error", f"Failed to load documents: {str(e)}")
        
        # Update status bar
        self.status_bar_component.show_message(f"Selected: {database_name}/{collection_name}", 2000)
    
    def refresh_documents(self):
        """Refresh the documents table."""
        import logging
        logger = logging.getLogger(__name__)
        
        if not self.current_database or not self.current_collection:
            logger.warning("No database or collection selected for document refresh")
            return
        
        logger.info(f"Refreshing documents for {self.current_database}/{self.current_collection}")
        
        self.document_view_manager.set_loading_state(True)
        
        try:
            documents = self.mongo_service.find_documents(
                self.current_database, 
                self.current_collection, 
                limit=50
            )
            
            logger.debug(f"Retrieved {len(documents) if documents else 0} documents")
            self.document_view_manager.populate_documents(documents)
            
            # Update status bar
            doc_count = len(documents) if documents else 0
            self.status_bar_component.show_message(f"Loaded {doc_count} documents", 2000)
            
        except Exception as e:
            logger.error(f"Failed to load documents: {e}")
            self.document_view_manager.set_error_state(str(e))
            MessageBoxHelper.warning(self, "Error", f"Failed to load documents: {str(e)}")
        
        finally:
            self.document_view_manager.set_loading_state(False)
    
    def insert_document(self, document_text: str):
        """Insert a new document."""
        import logging
        logger = logging.getLogger(__name__)
        
        if not self.current_database or not self.current_collection:
            MessageBoxHelper.warning(self, "Warning", "Please select a collection first.")
            return
        
        logger.info(f"Inserting document into {self.current_database}/{self.current_collection}")
        
        success, message = self.mongo_service.insert_document(
            self.current_database, 
            self.current_collection, 
            document_text
        )
        
        if success:
            logger.info(f"Document inserted successfully: {message}")
            MessageBoxHelper.information(self, "Success", message)
            self.operations_panel.clear_insert_form()
            # Refresh documents to show the new document
            self.refresh_documents()
            # Update status bar
            self.status_bar_component.show_message("Document inserted successfully", 3000)
        else:
            logger.error(f"Failed to insert document: {message}")
            MessageBoxHelper.critical(self, "Error", message)
    
    def update_document(self, filter_text: str, update_text: str):
        """Update an existing document."""
        if not self.current_database or not self.current_collection:
            MessageBoxHelper.warning(self, "Warning", "Please select a collection first.")
            return
        
        success, message = self.mongo_service.update_document(
            self.current_database, 
            self.current_collection, 
            filter_text, 
            update_text
        )
        
        if success:
            MessageBoxHelper.information(self, "Success", message)
            self.operations_panel.clear_update_form()
            self.refresh_documents()
        else:
            MessageBoxHelper.critical(self, "Error", message)
    
    def delete_document(self, filter_text: str):
        """Delete a document."""
        import logging
        logger = logging.getLogger(__name__)
        
        if not self.current_database or not self.current_collection:
            MessageBoxHelper.warning(self, "Warning", "Please select a collection first.")
            return
        
        logger.info(f"Deleting document from {self.current_database}/{self.current_collection}")
        
        reply = MessageBoxHelper.question(
            self, 
            "Confirm Delete", 
            "Are you sure you want to delete this document?"
        )
        
        if reply:
            success, message = self.mongo_service.delete_document(
                self.current_database, 
                self.current_collection, 
                filter_text
            )
            
            if success:
                logger.info(f"Document deleted successfully: {message}")
                MessageBoxHelper.information(self, "Success", message)
                self.operations_panel.clear_delete_form()
                # Refresh documents to update the table
                self.refresh_documents()
                # Update status bar
                self.status_bar_component.show_message("Document deleted successfully", 3000)
            else:
                logger.error(f"Failed to delete document: {message}")
                MessageBoxHelper.critical(self, "Error", message)
    
    def execute_query(self, query_text: str, limit: int):
        """Execute a query and display results."""
        if not self.current_database or not self.current_collection:
            MessageBoxHelper.warning(self, "Warning", "Please select a collection first.")
            return
        
        documents = self.mongo_service.find_documents(
            self.current_database, 
            self.current_collection, 
            query_text if query_text else None, 
            limit
        )
        
        if documents:
            # Format results as JSON
            formatted_results = json.dumps(documents, indent=2, default=str)
            self.query_panel.set_query_results(formatted_results)
        else:
            self.query_panel.set_query_results("No documents found.")
    
    def on_resize_event(self, event):
        """Handle window resize events for responsive layout."""
        # Call the parent resize event handler
        super().resizeEvent(event)
        
        # Adjust splitter proportions based on new window size
        if hasattr(self, 'main_splitter'):
            window_width = self.width()
            total_width = window_width - 16
            left_width = int(total_width * 0.35)
            right_width = total_width - left_width
            
            # Ensure minimum widths
            left_width = max(left_width, 300)
            right_width = max(right_width, 400)
            
            self.main_splitter.setSizes([left_width, right_width])
        
        # Update status bar message
        self.status_bar_component.show_message(f"Window resized to {self.width()}x{self.height()}", 2000)
    
    def apply_styles(self):
        """Apply custom styles to the application."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
                color: #212529;
            }
            
            QGroupBox {
                font-weight: 600;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 12px;
                background-color: #ffffff;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px 0 8px;
                color: #495057;
                font-size: 13px;
            }
            
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 13px;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background-color: #0056b3;
            }
            
            QPushButton:pressed {
                background-color: #004085;
            }
            
            QPushButton:disabled {
                background-color: #6c757d;
                color: #adb5bd;
            }
            
            QPushButton#connectButton {
                background-color: #28a745;
            }
            
            QPushButton#connectButton:hover {
                background-color: #218838;
            }
            
            QPushButton#disconnectButton {
                background-color: #dc3545;
            }
            
            QPushButton#disconnectButton:hover {
                background-color: #c82333;
            }
            
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                background-color: white;
            }
            
            QTabBar::tab {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 10px 20px;
                margin-right: 2px;
                font-weight: 500;
                color: #495057;
                min-width: 80px;
            }
            
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
                color: #007bff;
                font-weight: 600;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #e9ecef;
            }
        """)
    
    # Placeholder methods for menu actions
    def on_new_connection(self):
        """Handle new connection menu action."""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info("Opening new connection dialog")
        
        # Show connection dialog
        from ..dialogs.dialogs import ConnectionDialog
        dialog = ConnectionDialog(self)
        
        if dialog.exec() == QDialog.Accepted:
            connection_string = dialog.get_connection_string()
            connection_options = dialog.get_connection_options()
            
            if connection_string:
                logger.info(f"User confirmed new connection: {connection_string}")
                
                # Attempt to connect
                success, message = self.mongo_service.connect_to_mongodb(connection_string)
                
                if success:
                    logger.info("New connection established successfully")
                    MessageBoxHelper.success(self, "Connection Successful", message)
                    
                    # Update UI state
                    self.update_connection_state(True)
                    self.refresh_databases()
                else:
                    logger.error(f"New connection failed: {message}")
                    MessageBoxHelper.critical(self, "Connection Failed", message)
            else:
                logger.info("User cancelled new connection (empty connection string)")
        else:
            logger.info("User cancelled new connection dialog")
    
    def on_open_connection(self):
        """Handle open connection menu action."""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info("Opening connection dialog")
        
        # Get current connection string if connected
        current_connection = ""
        if self.mongo_service.is_connected():
            connection_info = self.mongo_service.get_connection_info()
            current_connection = connection_info.get('connection_string', '')
        
        # Show connection dialog with current connection string
        from ..dialogs.dialogs import ConnectionDialog
        dialog = ConnectionDialog(self, current_connection)
        
        if dialog.exec() == QDialog.Accepted:
            connection_string = dialog.get_connection_string()
            connection_options = dialog.get_connection_options()
            
            if connection_string:
                logger.info(f"User confirmed connection: {connection_string}")
                
                # If already connected, disconnect first
                if self.mongo_service.is_connected():
                    logger.info("Disconnecting from current connection")
                    self.mongo_service.disconnect_from_mongodb()
                    self.update_connection_state(False)
                
                # Attempt to connect
                success, message = self.mongo_service.connect_to_mongodb(connection_string)
                
                if success:
                    logger.info("Connection established successfully")
                    MessageBoxHelper.success(self, "Connection Successful", message)
                    
                    # Update UI state
                    self.update_connection_state(True)
                    self.refresh_databases()
                else:
                    logger.error(f"Connection failed: {message}")
                    MessageBoxHelper.critical(self, "Connection Failed", message)
            else:
                logger.info("User cancelled connection (empty connection string)")
        else:
            logger.info("User cancelled connection dialog")
    
    def on_export_data(self):
        """Handle export data menu action."""
        if not self.mongo_service.is_connected():
            MessageBoxHelper.warning(self, "Warning", "Please connect to MongoDB first.")
            return
        
        if not self.current_database or not self.current_collection:
            MessageBoxHelper.warning(self, "Warning", "Please select a database and collection first.")
            return
        
        # Show export data dialog
        dialog = ExportDataDialog(self, self.current_database, self.current_collection)
        if dialog.exec() == QDialog.Accepted:
            export_info = dialog.get_export_info()
            
            # For now, show a confirmation
            # In a full implementation, this would actually export the data
            MessageBoxHelper.information(
                self, 
                "Export Data", 
                f"Export configuration:\n\n"
                f"Database: {self.current_database}\n"
                f"Collection: {self.current_collection}\n"
                f"Format: {export_info['format'].upper()}\n"
                f"Path: {export_info['path']}\n\n"
                f"Data export functionality is currently in development.\n"
                f"This will export collection data in the specified format."
            )
    
    def on_import_data(self):
        """Handle import data menu action."""
        if not self.mongo_service.is_connected():
            MessageBoxHelper.warning(self, "Warning", "Please connect to MongoDB first.")
            return
        
        if not self.current_database or not self.current_collection:
            MessageBoxHelper.warning(self, "Warning", "Please select a database and collection first.")
            return
        
        # For now, show a simple import info dialog
        # In a full implementation, this would show a file selection and import dialog
        MessageBoxHelper.information(
            self, 
            "Import Data", 
            f"Import data into:\n\n"
            f"Database: {self.current_database}\n"
            f"Collection: {self.current_collection}\n\n"
            f"Data import functionality is currently in development.\n"
            f"This feature will include:\n"
            "• File selection (JSON, CSV, XML)\n"
            "• Data validation and preview\n"
            "• Import options and mapping\n"
            "• Progress tracking and error handling"
        )
    
    def on_create_database(self):
        """Handle create database menu/toolbar action."""
        if not self.mongo_service.is_connected():
            MessageBoxHelper.warning(self, "Warning", "Please connect to MongoDB first.")
            return
        
        from PySide6.QtWidgets import QInputDialog
        db_name, ok = QInputDialog.getText(
            self, "Create Database", "Enter database name:"
        )
        
        if ok and db_name.strip():
            success, message = self.mongo_service.create_database(db_name.strip())
            if success:
                MessageBoxHelper.information(self, "Success", message)
                self.refresh_databases()
            else:
                MessageBoxHelper.critical(self, "Error", message)
    
    def on_list_databases(self):
        """Handle list databases menu/toolbar action."""
        if not self.mongo_service.is_connected():
            MessageBoxHelper.warning(self, "Warning", "Please connect to MongoDB first.")
            return
        
        databases = self.mongo_service.get_databases()
        if databases:
            db_list = "\n".join([f"• {db}" for db in databases])
            MessageBoxHelper.information(
                self, 
                "Databases", 
                f"Found {len(databases)} database(s):\n\n{db_list}"
            )
        else:
            MessageBoxHelper.information(self, "Databases", "No databases found.")
    
    def on_rename_database(self):
        """Handle rename database menu/toolbar action."""
        if not self.mongo_service.is_connected():
            MessageBoxHelper.warning(self, "Warning", "Please connect to MongoDB first.")
            return
        
        if not self.current_database:
            MessageBoxHelper.warning(self, "Warning", "Please select a database first.")
            return
        
        from PySide6.QtWidgets import QInputDialog
        new_name, ok = QInputDialog.getText(
            self, 
            "Rename Database", 
            f"Rename '{self.current_database}' to:",
            text=self.current_database
        )
        
        if ok and new_name.strip() and new_name.strip() != self.current_database:
            reply = MessageBoxHelper.question(
                self,
                "Confirm Rename",
                f"Are you sure you want to rename database '{self.current_database}' to '{new_name.strip()}'?\n\n"
                "This operation will copy all collections and data to the new database."
            )
            
            if reply:
                success, message = self.mongo_service.rename_database(
                    self.current_database, new_name.strip()
                )
                if success:
                    MessageBoxHelper.information(self, "Success", message)
                    self.current_database = new_name.strip()
                    self.refresh_databases()
                else:
                    MessageBoxHelper.critical(self, "Error", message)
    
    def on_delete_database(self):
        """Handle delete database menu/toolbar action."""
        if not self.mongo_service.is_connected():
            MessageBoxHelper.warning(self, "Warning", "Please connect to MongoDB first.")
            return
        
        if not self.current_database:
            MessageBoxHelper.warning(self, "Warning", "Please select a database first.")
            return
        
        reply = MessageBoxHelper.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete database '{self.current_database}'?\n\n"
            "This action cannot be undone and will permanently remove all data!"
        )
        
        if reply:
            success, message = self.mongo_service.delete_database(self.current_database)
            if success:
                MessageBoxHelper.information(self, "Success", message)
                self.current_database = ""
                self.current_collection = ""
                self.refresh_databases()
            else:
                MessageBoxHelper.critical(self, "Error", message)
    
    def on_add_database(self):
        """Handle add database menu action."""
        if not self.mongo_service.is_connected():
            MessageBoxHelper.warning(self, "Warning", "Please connect to MongoDB first.")
            return
        
        # Show create database dialog
        dialog = CreateDatabaseDialog(self)
        if dialog.exec() == QDialog.Accepted:
            database_name = dialog.get_database_name()
            
            if database_name:
                # Create the database
                success, message = self.mongo_service.create_database(database_name)
                
                if success:
                    MessageBoxHelper.information(self, "Success", message)
                    # Refresh the database list to show the new database
                    self.refresh_databases()
                else:
                    MessageBoxHelper.critical(self, "Error", message)
    
    def on_add_collection(self):
        """Handle add collection menu action."""
        if not self.mongo_service.is_connected():
            MessageBoxHelper.warning(self, "Warning", "Please connect to MongoDB first.")
            return
        if not self.current_database:
            MessageBoxHelper.warning(self, "Warning", "Please select a database first.")
            return
        
        # Show create collection dialog
        dialog = CreateCollectionDialog(self, self.current_database)
        if dialog.exec() == QDialog.Accepted:
            collection_name = dialog.get_collection_name()
            
            if collection_name:
                # Create the collection
                success, message = self.mongo_service.create_collection(self.current_database, collection_name)
                
                if success:
                    MessageBoxHelper.information(self, "Success", message)
                    # Refresh the database list to show the new collection
                    self.refresh_databases()
                else:
                    MessageBoxHelper.critical(self, "Error", message)
    
    def on_query_builder(self):
        """Handle query builder menu action."""
        if not self.mongo_service.is_connected():
            MessageBoxHelper.warning(self, "Warning", "Please connect to MongoDB first.")
            return
        
        # Show query builder dialog
        dialog = QueryBuilderDialog(self, self.current_database, self.current_collection)
        if dialog.exec() == QDialog.Accepted:
            query_json = dialog.get_query_json()
            limit = dialog.get_limit()
            
            # Execute the query
            documents = self.mongo_service.find_documents(
                self.current_database, 
                self.current_collection,  # Fixed: use collection name
                query_json if query_json != "{}" else None, 
                limit
            )
            
            if documents:
                # Format results as JSON
                import json
                formatted_results = json.dumps(documents, indent=2, default=str)
                self.query_panel.set_query_results(formatted_results)
                # Switch to query tab to show results
                self.tab_widget.setCurrentIndex(2)
            else:
                MessageBoxHelper.information(self, "Query Results", "No documents found matching the query.")
    
    def on_performance_monitor(self):
        """Handle performance monitor menu action."""
        if not self.mongo_service.is_connected():
            MessageBoxHelper.warning(self, "Warning", "Please connect to MongoDB first.")
            return
        
        # For now, show a simple performance info dialog
        # In a full implementation, this would show real-time MongoDB performance metrics
        MessageBoxHelper.information(
            self, 
            "Performance Monitor", 
            "Performance monitoring is currently in development.\n\n"
            "This feature will include:\n"
            "• Real-time query performance metrics\n"
            "• Database connection statistics\n"
            "• Collection size and index information\n"
            "• Slow query analysis"
        )
    
    def on_settings(self):
        """Handle settings menu action."""
        # Show settings dialog
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.Accepted:
            settings = dialog.get_settings()
            # Here you would save the settings to a configuration file
            # For now, just show a confirmation
            MessageBoxHelper.information(
                self, 
                "Settings Saved", 
                f"Settings have been saved:\n\n"
                f"Default URI: {settings['default_uri']}\n"
                f"Timeout: {settings['timeout']} ms\n"
                f"Auto-refresh: {'Enabled' if settings['auto_refresh'] else 'Disabled'}\n"
                f"Confirm delete: {'Enabled' if settings['confirm_delete'] else 'Disabled'}"
            )
    
    def on_documentation(self):
        """Handle documentation menu action."""
        # Show documentation dialog
        MessageBoxHelper.information(
            self, 
            "Documentation", 
            "AtlasMogo Documentation\n\n"
            "This is a MongoDB management tool built with Python and PySide6.\n\n"
            "Key Features:\n"
            "• Connect to MongoDB instances\n"
            "• Create, rename, and delete databases\n"
            "• Create collections and manage documents\n"
            "• Execute queries with a visual builder\n"
            "• Import/export data in multiple formats\n\n"
            "For more information, visit the project repository."
        )
    
    # Context menu action handlers
    def on_rename_database(self, database_name: str):
        """Handle rename database context menu action."""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Opening rename database dialog for: {database_name}")
        
        if not self.mongo_service.is_connected():
            MessageBoxHelper.warning(self, "Warning", "Please connect to MongoDB first.")
            return
        
        from PySide6.QtWidgets import QInputDialog
        new_name, ok = QInputDialog.getText(
            self, 
            "Rename Database", 
            f"Rename '{database_name}' to:",
            text=database_name
        )
        
        if ok and new_name.strip() and new_name.strip() != database_name:
            logger.info(f"User confirmed rename database from '{database_name}' to '{new_name.strip()}'")
            
            reply = MessageBoxHelper.question(
                self,
                "Confirm Rename",
                f"Are you sure you want to rename database '{database_name}' to '{new_name.strip()}'?\n\n"
                "This operation will copy all collections and data to the new database."
            )
            
            if reply:
                logger.info(f"Attempting to rename database from '{database_name}' to '{new_name.strip()}'")
                success, message = self.mongo_service.rename_database(database_name, new_name.strip())
                
                if success:
                    logger.info(f"Successfully renamed database from '{database_name}' to '{new_name.strip()}'")
                    MessageBoxHelper.information(self, "Success", message)
                    
                    # Update current database if it was the renamed one
                    if self.current_database == database_name:
                        self.current_database = new_name.strip()
                        self.current_collection = ""
                    
                    self.refresh_databases()
                else:
                    logger.error(f"Failed to rename database from '{database_name}' to '{new_name.strip()}': {message}")
                    MessageBoxHelper.critical(self, "Error", message)
            else:
                logger.info("User cancelled database rename operation")
        elif ok:
            logger.info("User cancelled rename (no change in name)")
        else:
            logger.info("User cancelled rename dialog")
    
    def on_delete_database(self, database_name: str):
        """Handle delete database context menu action."""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Opening delete database dialog for: {database_name}")
        
        if not self.mongo_service.is_connected():
            MessageBoxHelper.warning(self, "Warning", "Please connect to MongoDB first.")
            return
        
        reply = MessageBoxHelper.question(
            self,
            "Delete Database",
            f"Are you sure you want to delete database '{database_name}'?\n\n"
            "This action cannot be undone and will delete all collections and documents."
        )
        
        if reply:
            logger.info(f"User confirmed delete database: {database_name}")
            
            logger.info(f"Attempting to delete database: {database_name}")
            success, message = self.mongo_service.delete_database(database_name)
            
            if success:
                logger.info(f"Successfully deleted database: {database_name}")
                MessageBoxHelper.information(self, "Success", message)
                
                # Update current database if it was the deleted one
                if self.current_database == database_name:
                    self.current_database = ""
                    self.current_collection = ""
                
                self.refresh_databases()
            else:
                logger.error(f"Failed to delete database '{database_name}': {message}")
                MessageBoxHelper.critical(self, "Error", message)
        else:
            logger.info("User cancelled database deletion")
    
    def on_rename_collection(self, database_name: str, collection_name: str):
        """Handle rename collection context menu action."""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Opening rename collection dialog for: {database_name}/{collection_name}")
        
        if not self.mongo_service.is_connected():
            MessageBoxHelper.warning(self, "Warning", "Please connect to MongoDB first.")
            return
        
        from PySide6.QtWidgets import QInputDialog
        new_name, ok = QInputDialog.getText(
            self, 
            "Rename Collection", 
            f"Rename '{collection_name}' to:",
            text=collection_name
        )
        
        if ok and new_name.strip():
            if new_name.strip() == collection_name:
                logger.info("User cancelled rename (no change in name)")
                return
            
            logger.info(f"Attempting to rename collection {database_name}.{collection_name} → {database_name}.{new_name.strip()}")
            
            # Use the repository directly for collection rename
            try:
                from data.mongo_repository import MongoRepository
                client = self.mongo_service._connection.get_client()
                if client:
                    repo = MongoRepository(client)
                    success = repo.rename_collection(database_name, collection_name, new_name.strip())
                    
                    if success:
                        logger.info(f"Successfully renamed collection to {new_name.strip()}")
                        
                        # Update current collection if it was the renamed one
                        if self.current_database == database_name and self.current_collection == collection_name:
                            self.current_collection = new_name.strip()
                        
                        # Refresh UI and automatically select the new collection
                        self.refresh_databases()
                        
                        # Try to select the renamed collection in the sidebar
                        self.select_collection_in_sidebar(database_name, new_name.strip())
                    else:
                        logger.error(f"Failed to rename collection: {new_name.strip()}")
                        MessageBoxHelper.critical(
                            self, 
                            "Error", 
                            f"Failed to rename collection '{collection_name}' to '{new_name.strip()}'"
                        )
                else:
                    logger.error("No MongoDB client available")
                    MessageBoxHelper.critical(self, "Error", "No MongoDB client available")
            except Exception as e:
                logger.error(f"Failed to rename collection: {e}", exc_info=True)
                MessageBoxHelper.critical(self, "Error", f"Error renaming collection: {str(e)}")
        else:
            logger.info("User cancelled rename dialog")
    
    def on_delete_collection(self, database_name: str, collection_name: str):
        """Handle delete collection context menu action."""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Opening delete collection dialog for: {database_name}/{collection_name}")
        
        if not self.mongo_service.is_connected():
            MessageBoxHelper.warning(self, "Warning", "Please connect to MongoDB first.")
            return
        
        reply = MessageBoxHelper.question(
            self,
            "Delete Collection",
            f"Are you sure you want to delete collection '{collection_name}' from database '{database_name}'?\n\n"
            "This action cannot be undone and will delete all documents in the collection."
        )
        
        if reply:
            logger.info(f"User confirmed delete collection: {database_name}/{collection_name}")
            
            logger.info(f"Attempting to delete collection: {database_name}/{collection_name}")
            success, message = self.mongo_service.drop_collection(database_name, collection_name)
            
            if success:
                logger.info(f"Successfully deleted collection: {database_name}/{collection_name}")
                MessageBoxHelper.information(self, "Success", message)
                
                # Update current collection if it was the deleted one
                if self.current_database == database_name and self.current_collection == collection_name:
                    self.current_collection = ""
                
                self.refresh_databases()
            else:
                logger.error(f"Failed to delete collection '{database_name}/{collection_name}': {message}")
                MessageBoxHelper.critical(self, "Error", message)
        else:
            logger.info("User cancelled collection deletion")
    
    def on_insert_document_from_context(self, database_name: str, collection_name: str):
        """Handle insert document from context menu action."""
        import logging
        logger = logging.getLogger(__name__)
        
        # Set the current database and collection
        self.current_database = database_name
        self.current_collection = collection_name
        
        logger.info(f"Insert document requested for {database_name}/{collection_name}")
        
        # Switch to operations tab for document insertion
        self.tab_widget.setCurrentIndex(1)  # Operations tab
        
        # Show success message
        MessageBoxHelper.information(
            self,
            "Insert Document",
            f"Ready to insert document into collection '{collection_name}' in database '{database_name}'.\n\n"
            "Use the Operations tab to insert your document."
        )
    
    def on_view_document(self, document_data: dict):
        """Handle view document context menu action."""
        import logging
        logger = logging.getLogger(__name__)
        
        row = document_data.get("row", -1)
        logger.info(f"View document requested for row {row}")
        
        if not self.current_database or not self.current_collection:
            MessageBoxHelper.warning(self, "Warning", "No collection selected.")
            return
        
        # Get the document data for the selected row
        document = self.document_view_manager.get_document_by_row(row)
        if not document:
            logger.error(f"No document found at row {row}")
            MessageBoxHelper.warning(self, "Warning", "No document found at the selected row.")
            return
        
        logger.info(f"Opening document viewer for document at row {row}")
        
        # Create and show document viewer dialog
        from ..dialogs.dialogs import DocumentViewerDialog
        dialog = DocumentViewerDialog(document, self)
        dialog.exec()
    
    def on_edit_document(self, document_data: dict):
        """Handle edit document context menu action."""
        import logging
        logger = logging.getLogger(__name__)
        
        row = document_data.get("row", -1)
        logger.info(f"Edit document requested for row {row}")
        
        if not self.current_database or not self.current_collection:
            MessageBoxHelper.warning(self, "Warning", "No collection selected.")
            return
        
        # Get the document data for the selected row
        document = self.document_view_manager.get_document_by_row(row)
        if not document:
            logger.error(f"No document found at row {row}")
            MessageBoxHelper.warning(self, "Warning", "No document found at the selected row.")
            return
        
        logger.info(f"Opening document editor for document at row {row}")
        
        # Create and show document editor dialog
        from ..dialogs.dialogs import EditDocumentDialog
        dialog = EditDocumentDialog(document, self.current_database, self.current_collection, self)
        if dialog.exec() == QDialog.Accepted:
            updated_document = dialog.get_document()
            if updated_document:
                logger.info(f"User confirmed document edit for row {row}")
                
                # Update the document in MongoDB
                try:
                    import json
                    from data.mongo_repository import MongoRepository
                    client = self.mongo_service._connection.get_client()
                    if client:
                        repo = MongoRepository(client)
                        success = repo.replace_document(
                            self.current_database, 
                            self.current_collection, 
                            document.get("_id"), 
                            updated_document
                        )
                        
                        if success:
                            logger.info(f"Successfully updated document at row {row}")
                            MessageBoxHelper.information(self, "Success", "Document updated successfully")
                            self.refresh_documents()
                        else:
                            logger.error(f"Failed to update document at row {row}")
                            MessageBoxHelper.critical(self, "Error", "Failed to update document")
                    else:
                        logger.error("No MongoDB client available")
                        MessageBoxHelper.critical(self, "Error", "No MongoDB client available")
                except Exception as e:
                    logger.error(f"Error updating document: {e}", exc_info=True)
                    MessageBoxHelper.critical(self, "Error", f"Error updating document: {str(e)}")
            else:
                logger.info("User cancelled document edit (no changes)")
        else:
            logger.info("User cancelled document edit dialog")
    
    def on_delete_document_from_context(self, document_data: dict):
        """Handle delete document from context menu action."""
        import logging
        logger = logging.getLogger(__name__)
        
        row = document_data.get("row", -1)
        logger.info(f"Delete document requested for row {row}")
        
        if not self.current_database or not self.current_collection:
            MessageBoxHelper.warning(self, "Warning", "No collection selected.")
            return
        
        # Get the document data for the selected row
        document = self.document_view_manager.get_document_by_row(row)
        if not document:
            logger.error(f"No document found at row {row}")
            MessageBoxHelper.warning(self, "Warning", "No document found at the selected row.")
            return
        
        # Get the document _id
        document_id = document.get("_id")
        if not document_id:
            logger.error(f"Document at row {row} has no _id field")
            MessageBoxHelper.warning(self, "Warning", "Document has no _id field and cannot be deleted.")
            return
        
        logger.info(f"Attempting to delete document with _id: {document_id}")
        
        reply = MessageBoxHelper.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the document at row {row}?\n\nDocument ID: {document_id}"
        )
        
        if reply:
            logger.info(f"User confirmed deletion of document with _id: {document_id}")
            
            # Delete the document from MongoDB
            success, message = self.mongo_service.delete_document_by_id(
                self.current_database, 
                self.current_collection, 
                document_id
            )
            
            if success:
                logger.info(f"Successfully deleted document with _id: {document_id}")
                MessageBoxHelper.information(self, "Success", f"Document deleted successfully.\n\n{message}")
                # Refresh the documents to update the table
                self.refresh_documents()
            else:
                logger.error(f"Failed to delete document with _id: {document_id} - {message}")
                MessageBoxHelper.critical(self, "Error", f"Failed to delete document.\n\n{message}")
        else:
            logger.info("User cancelled document deletion")
    
    def on_insert_document(self):
        """Handle insert document toolbar action."""
        import logging
        logger = logging.getLogger(__name__)
        
        if not self.mongo_service.is_connected():
            MessageBoxHelper.warning(self, "Warning", "Please connect to MongoDB first.")
            return
        
        if not self.current_database or not self.current_collection:
            MessageBoxHelper.warning(self, "Warning", "Please select a collection first.")
            return
        
        logger.info(f"Opening insert document dialog for {self.current_database}/{self.current_collection}")
        
        # Show insert document dialog
        from ..dialogs.dialogs import InsertDocumentDialog
        dialog = InsertDocumentDialog(self.current_database, self.current_collection, self)
        
        if dialog.exec() == QDialog.Accepted:
            document = dialog.get_document()
            if document:
                logger.info(f"User confirmed document insertion")
                
                # Insert the document into MongoDB
                try:
                    import json
                    document_json = json.dumps(document)
                    success, message = self.mongo_service.insert_document(
                        self.current_database, 
                        self.current_collection, 
                        document_json
                    )
                    
                    if success:
                        logger.info(f"Successfully inserted document: {message}")
                        MessageBoxHelper.information(self, "Success", f"Document inserted successfully.\n\n{message}")
                        self.refresh_documents()
                    else:
                        logger.error(f"Failed to insert document: {message}")
                        MessageBoxHelper.critical(self, "Error", f"Failed to insert document.\n\n{message}")
                except Exception as e:
                    logger.error(f"Error inserting document: {e}", exc_info=True)
                    MessageBoxHelper.critical(self, "Error", f"Error inserting document: {str(e)}")
            else:
                logger.info("User cancelled document insertion (invalid document)")
        else:
            logger.info("User cancelled insert document dialog")
    
    def on_update_document(self):
        """Handle update document toolbar action."""
        if not self.current_database or not self.current_collection:
            MessageBoxHelper.warning(self, "Warning", "Please select a collection first.")
            return
        self.tab_widget.setCurrentIndex(1)  # Operations tab
    
    def on_delete_document(self):
        """Handle delete document toolbar action."""
        if not self.current_database or not self.current_collection:
            MessageBoxHelper.warning(self, "Warning", "Please select a collection first.")
            return
        self.tab_widget.setCurrentIndex(1)  # Operations tab
    
    def on_execute_query(self):
        """Handle execute query toolbar action."""
        if not self.current_database or not self.current_collection:
            MessageBoxHelper.warning(self, "Warning", "Please select a collection first.")
            return
        self.tab_widget.setCurrentIndex(2)  # Query tab
    
    def show_about(self):
        """Show about dialog."""
        MessageBoxHelper.information(
            self,
            "About AtlasMogo",
            "AtlasMogo - MongoDB Management Tool\n\n"
            "Version 1.0.0\n"
            "A desktop application for managing MongoDB databases\n"
            "with a clean, modern interface.\n\n"
            "Built with Python and PySide6"
        )
    
    def closeEvent(self, event):
        """Handle application close event."""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info("Close event triggered")
        
        if self.mongo_service.is_connected():
            logger.info("MongoDB is connected, showing confirmation dialog")
            
            try:
                reply = MessageBoxHelper.question(
                    self,
                    "Confirm Exit",
                    "You are still connected to MongoDB. Do you want to disconnect and exit?"
                )
                
                logger.info(f"User response: {reply}")
                
                if reply:
                    logger.info("User confirmed exit, disconnecting MongoDB")
                    self.mongo_service.disconnect_from_mongodb()
                    logger.info("Calling event.accept()")
                    event.accept()
                else:
                    logger.info("User cancelled exit, calling event.ignore()")
                    event.ignore()
                    
            except Exception as e:
                logger.error(f"Error in closeEvent: {e}", exc_info=True)
                event.accept()
        else:
            logger.info("MongoDB not connected, accepting close event")
            event.accept()