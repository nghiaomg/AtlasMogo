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
    QApplication, QSizePolicy
)
from .message_box_helper import MessageBoxHelper
from PySide6.QtCore import Qt, QThread, Signal, QTimer

# Import modular components
from .menu_bar import MenuBar
from .toolbar import ToolBar
from .connection_panel import ConnectionPanel
from .sidebar import Sidebar
from .data_table import DataTable
from .operations_panel import OperationsPanel
from .query_panel import QueryPanel
from .status_bar import StatusBar

# Import dialogs
from .dialogs import (
    CreateDatabaseDialog, CreateCollectionDialog, InsertDocumentDialog,
    QueryBuilderDialog, SettingsDialog, ExportDataDialog
)

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
        self.data_table = None
        self.operations_panel = None
        self.query_panel = None
        self.status_bar_component = None
        
        self.init_ui()
        self.setup_connections()
        self.apply_styles()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("AtlasMogo - MongoDB Management Tool")
        
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
        self.data_table = DataTable(self)
        self.tab_widget.addTab(self.data_table.get_widget(), "Documents")
        
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
        
        # Data table signals
        self.data_table.refresh_requested.connect(self.refresh_documents)
        self.data_table.view_document_requested.connect(self.on_view_document)
        self.data_table.edit_document_requested.connect(self.on_edit_document)
        self.data_table.delete_document_requested.connect(self.on_delete_document_from_context)
        
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
            QMessageBox.information(self, "Connection Success", 
                                  f"Successfully connected to MongoDB!\n\n{message}")
        else:
            self.connection_state = "failed"
            self.connection_panel.set_connection_state("failed")
            self.status_bar_component.set_connection_status("Connection Failed", "red")
            
            # Show error message
            QMessageBox.critical(self, "Connection Error", 
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
            self.data_table.clear_table()
            
            # Update status bar
            self.status_bar_component.show_message("Disconnected from MongoDB", 3000)
            
            # Update toolbar state
            self.toolbar_component.update_toolbar_state(False)
            
            # Show disconnection message
            QMessageBox.information(self, "Disconnected", "Successfully disconnected from MongoDB.")
            
        except Exception as e:
            QMessageBox.warning(self, "Disconnect Warning", f"Error during disconnect: {str(e)}")
    
    def refresh_databases(self):
        """Refresh the databases tree."""
        if not self.mongo_service.is_connected():
            QMessageBox.warning(self, "Not Connected", "Please connect to MongoDB first.")
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
            QMessageBox.critical(self, "Database Error", error_msg)
            self.status_bar_component.show_message(f"Failed to refresh databases: {str(e)}", 5000)
        
        finally:
            self.sidebar.set_loading_state(False)
    
    def on_database_selected(self, database_name: str):
        """Handle database selection."""
        import logging
        logger = logging.getLogger(__name__)
        
        self.current_database = database_name
        self.current_collection = ""
        
        logger.info(f"Database selected: {database_name}")
        
        # Update labels
        self.data_table.set_collection_info("None selected", 0)
        self.sidebar.update_selected_database(database_name)
        
        # Get collection count for this database
        try:
            collections = self.mongo_service.get_collections(database_name)
            collection_count = len(collections)
            logger.debug(f"Database {database_name} has {collection_count} collections")
            self.sidebar.update_collection_count(collection_count)
            
            # Clear documents table
            self.data_table.clear_table()
            
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
        self.data_table.set_collection_info(collection_name, 0)
        self.sidebar.update_selected_database(f"{database_name} > {collection_name}")
        
        # Get document count and load documents
        try:
            count = self.mongo_service.count_documents(database_name, collection_name)
            logger.debug(f"Collection {collection_name} has {count} documents")
            self.data_table.set_collection_info(collection_name, count)
            
            # Load documents
            self.refresh_documents()
            
        except Exception as e:
            logger.error(f"Failed to load documents for {database_name}/{collection_name}: {e}")
            self.data_table.set_collection_info(collection_name, 0)
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
        
        self.data_table.set_loading_state(True)
        
        try:
            documents = self.mongo_service.find_documents(
                self.current_database, 
                self.current_collection, 
                limit=50
            )
            
            logger.debug(f"Retrieved {len(documents) if documents else 0} documents")
            self.data_table.populate_documents(documents)
            
            # Update status bar
            doc_count = len(documents) if documents else 0
            self.status_bar_component.show_message(f"Loaded {doc_count} documents", 2000)
            
        except Exception as e:
            logger.error(f"Failed to load documents: {e}")
            self.data_table.set_error_state(str(e))
            MessageBoxHelper.warning(self, "Error", f"Failed to load documents: {str(e)}")
        
        finally:
            self.data_table.set_loading_state(False)
    
    def insert_document(self, document_text: str):
        """Insert a new document."""
        import logging
        logger = logging.getLogger(__name__)
        
        if not self.current_database or not self.current_collection:
            QMessageBox.warning(self, "Warning", "Please select a collection first.")
            return
        
        logger.info(f"Inserting document into {self.current_database}/{self.current_collection}")
        
        success, message = self.mongo_service.insert_document(
            self.current_database, 
            self.current_collection, 
            document_text
        )
        
        if success:
            logger.info(f"Document inserted successfully: {message}")
            QMessageBox.information(self, "Success", message)
            self.operations_panel.clear_insert_form()
            # Refresh documents to show the new document
            self.refresh_documents()
            # Update status bar
            self.status_bar_component.show_message("Document inserted successfully", 3000)
        else:
            logger.error(f"Failed to insert document: {message}")
            QMessageBox.critical(self, "Error", message)
    
    def update_document(self, filter_text: str, update_text: str):
        """Update an existing document."""
        if not self.current_database or not self.current_collection:
            QMessageBox.warning(self, "Warning", "Please select a collection first.")
            return
        
        success, message = self.mongo_service.update_document(
            self.current_database, 
            self.current_collection, 
            filter_text, 
            update_text
        )
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.operations_panel.clear_update_form()
            self.refresh_documents()
        else:
            QMessageBox.critical(self, "Error", message)
    
    def delete_document(self, filter_text: str):
        """Delete a document."""
        import logging
        logger = logging.getLogger(__name__)
        
        if not self.current_database or not self.current_collection:
            QMessageBox.warning(self, "Warning", "Please select a collection first.")
            return
        
        logger.info(f"Deleting document from {self.current_database}/{self.current_collection}")
        
        reply = QMessageBox.question(
            self, 
            "Confirm Delete", 
            "Are you sure you want to delete this document?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.mongo_service.delete_document(
                self.current_database, 
                self.current_collection, 
                filter_text
            )
            
            if success:
                logger.info(f"Document deleted successfully: {message}")
                QMessageBox.information(self, "Success", message)
                self.operations_panel.clear_delete_form()
                # Refresh documents to update the table
                self.refresh_documents()
                # Update status bar
                self.status_bar_component.show_message("Document deleted successfully", 3000)
            else:
                logger.error(f"Failed to delete document: {message}")
                QMessageBox.critical(self, "Error", message)
    
    def execute_query(self, query_text: str, limit: int):
        """Execute a query and display results."""
        if not self.current_database or not self.current_collection:
            QMessageBox.warning(self, "Warning", "Please select a collection first.")
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
        # For now, show a simple new connection dialog
        # In a full implementation, this would show a connection configuration dialog
        QMessageBox.information(
            self, 
            "New Connection", 
            "New connection functionality is currently in development.\n\n"
            "This feature will include:\n"
            "• Connection name and description\n"
            "• Advanced connection options\n"
            "• Connection testing and validation\n"
            "• Connection profiles and favorites\n\n"
            "For now, use the connection panel above to connect to MongoDB."
        )
    
    def on_open_connection(self):
        """Handle open connection menu action."""
        # For now, show a simple open connection dialog
        # In a full implementation, this would show saved connections
        QMessageBox.information(
            self, 
            "Open Connection", 
            "Open connection functionality is currently in development.\n\n"
            "This feature will include:\n"
            "• List of saved connections\n"
            "• Connection history\n"
            "• Quick connection shortcuts\n"
            "• Connection import/export\n\n"
            "For now, use the connection panel above to connect to MongoDB."
        )
    
    def on_export_data(self):
        """Handle export data menu action."""
        if not self.mongo_service.is_connected():
            QMessageBox.warning(self, "Warning", "Please connect to MongoDB first.")
            return
        
        if not self.current_database or not self.current_collection:
            QMessageBox.warning(self, "Warning", "Please select a database and collection first.")
            return
        
        # Show export data dialog
        dialog = ExportDataDialog(self, self.current_database, self.current_collection)
        if dialog.exec() == QDialog.Accepted:
            export_info = dialog.get_export_info()
            
            # For now, show a confirmation
            # In a full implementation, this would actually export the data
            QMessageBox.information(
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
            QMessageBox.warning(self, "Warning", "Please connect to MongoDB first.")
            return
        
        if not self.current_database or not self.current_collection:
            QMessageBox.warning(self, "Warning", "Please select a database and collection first.")
            return
        
        # For now, show a simple import info dialog
        # In a full implementation, this would show a file selection and import dialog
        QMessageBox.information(
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
            QMessageBox.warning(self, "Warning", "Please connect to MongoDB first.")
            return
        
        from PySide6.QtWidgets import QInputDialog
        db_name, ok = QInputDialog.getText(
            self, "Create Database", "Enter database name:"
        )
        
        if ok and db_name.strip():
            success, message = self.mongo_service.create_database(db_name.strip())
            if success:
                QMessageBox.information(self, "Success", message)
                self.refresh_databases()
            else:
                QMessageBox.critical(self, "Error", message)
    
    def on_list_databases(self):
        """Handle list databases menu/toolbar action."""
        if not self.mongo_service.is_connected():
            QMessageBox.warning(self, "Warning", "Please connect to MongoDB first.")
            return
        
        databases = self.mongo_service.get_databases()
        if databases:
            db_list = "\n".join([f"• {db}" for db in databases])
            QMessageBox.information(
                self, 
                "Databases", 
                f"Found {len(databases)} database(s):\n\n{db_list}"
            )
        else:
            QMessageBox.information(self, "Databases", "No databases found.")
    
    def on_rename_database(self):
        """Handle rename database menu/toolbar action."""
        if not self.mongo_service.is_connected():
            QMessageBox.warning(self, "Warning", "Please connect to MongoDB first.")
            return
        
        if not self.current_database:
            QMessageBox.warning(self, "Warning", "Please select a database first.")
            return
        
        from PySide6.QtWidgets import QInputDialog
        new_name, ok = QInputDialog.getText(
            self, 
            "Rename Database", 
            f"Rename '{self.current_database}' to:",
            text=self.current_database
        )
        
        if ok and new_name.strip() and new_name.strip() != self.current_database:
            reply = QMessageBox.question(
                self,
                "Confirm Rename",
                f"Are you sure you want to rename database '{self.current_database}' to '{new_name.strip()}'?\n\n"
                "This operation will copy all collections and data to the new database.",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success, message = self.mongo_service.rename_database(
                    self.current_database, new_name.strip()
                )
                if success:
                    QMessageBox.information(self, "Success", message)
                    self.current_database = new_name.strip()
                    self.refresh_databases()
                else:
                    QMessageBox.critical(self, "Error", message)
    
    def on_delete_database(self):
        """Handle delete database menu/toolbar action."""
        if not self.mongo_service.is_connected():
            QMessageBox.warning(self, "Warning", "Please connect to MongoDB first.")
            return
        
        if not self.current_database:
            QMessageBox.warning(self, "Warning", "Please select a database first.")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete database '{self.current_database}'?\n\n"
            "This action cannot be undone and will permanently remove all data!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.mongo_service.delete_database(self.current_database)
            if success:
                QMessageBox.information(self, "Success", message)
                self.current_database = ""
                self.current_collection = ""
                self.refresh_databases()
            else:
                QMessageBox.critical(self, "Error", message)
    
    def on_add_database(self):
        """Handle add database menu action."""
        if not self.mongo_service.is_connected():
            QMessageBox.warning(self, "Warning", "Please connect to MongoDB first.")
            return
        
        # Show create database dialog
        dialog = CreateDatabaseDialog(self)
        if dialog.exec() == QDialog.Accepted:
            database_name = dialog.get_database_name()
            
            if database_name:
                # Create the database
                success, message = self.mongo_service.create_database(database_name)
                
                if success:
                    QMessageBox.information(self, "Success", message)
                    # Refresh the database list to show the new database
                    self.refresh_databases()
                else:
                    QMessageBox.critical(self, "Error", message)
    
    def on_add_collection(self):
        """Handle add collection menu action."""
        if not self.mongo_service.is_connected():
            QMessageBox.warning(self, "Warning", "Please connect to MongoDB first.")
            return
        if not self.current_database:
            QMessageBox.warning(self, "Warning", "Please select a database first.")
            return
        
        # Show create collection dialog
        dialog = CreateCollectionDialog(self, self.current_database)
        if dialog.exec() == QDialog.Accepted:
            collection_name = dialog.get_collection_name()
            
            if collection_name:
                # Create the collection
                success, message = self.mongo_service.create_collection(self.current_database, collection_name)
                
                if success:
                    QMessageBox.information(self, "Success", message)
                    # Refresh the database list to show the new collection
                    self.refresh_databases()
                else:
                    QMessageBox.critical(self, "Error", message)
    
    def on_query_builder(self):
        """Handle query builder menu action."""
        if not self.mongo_service.is_connected():
            QMessageBox.warning(self, "Warning", "Please connect to MongoDB first.")
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
                QMessageBox.information(self, "Query Results", "No documents found matching the query.")
    
    def on_performance_monitor(self):
        """Handle performance monitor menu action."""
        if not self.mongo_service.is_connected():
            QMessageBox.warning(self, "Warning", "Please connect to MongoDB first.")
            return
        
        # For now, show a simple performance info dialog
        # In a full implementation, this would show real-time MongoDB performance metrics
        QMessageBox.information(
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
            QMessageBox.information(
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
        QMessageBox.information(
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
        # TODO: Implement rename database functionality
        QMessageBox.information(
            self,
            "Rename Database",
            f"Rename database '{database_name}' functionality will be implemented here."
        )
    
    def on_delete_database(self, database_name: str):
        """Handle delete database context menu action."""
        # TODO: Implement delete database functionality
        reply = QMessageBox.question(
            self,
            "Delete Database",
            f"Are you sure you want to delete database '{database_name}'?\n\n"
            "This action cannot be undone and will delete all collections and documents.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            QMessageBox.information(
                self,
                "Delete Database",
                f"Delete database '{database_name}' functionality will be implemented here."
            )
    
    def on_rename_collection(self, database_name: str, collection_name: str):
        """Handle rename collection context menu action."""
        # TODO: Implement rename collection functionality
        QMessageBox.information(
            self,
            "Rename Collection",
            f"Rename collection '{collection_name}' in database '{database_name}' functionality will be implemented here."
        )
    
    def on_delete_collection(self, database_name: str, collection_name: str):
        """Handle delete collection context menu action."""
        # TODO: Implement delete collection functionality
        reply = QMessageBox.question(
            self,
            "Delete Collection",
            f"Are you sure you want to delete collection '{collection_name}' from database '{database_name}'?\n\n"
            "This action cannot be undone and will delete all documents in the collection.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            QMessageBox.information(
                self,
                "Delete Collection",
                f"Delete collection '{collection_name}' functionality will be implemented here."
            )
    
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
        QMessageBox.information(
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
        
        # TODO: Implement document viewer dialog
        QMessageBox.information(
            self,
            "View Document",
            f"View document at row {row} functionality will be implemented here."
        )
    
    def on_edit_document(self, document_data: dict):
        """Handle edit document context menu action."""
        import logging
        logger = logging.getLogger(__name__)
        
        row = document_data.get("row", -1)
        logger.info(f"Edit document requested for row {row}")
        
        # TODO: Implement document editor dialog
        QMessageBox.information(
            self,
            "Edit Document",
            f"Edit document at row {row} functionality will be implemented here."
        )
    
    def on_delete_document_from_context(self, document_data: dict):
        """Handle delete document from context menu action."""
        import logging
        logger = logging.getLogger(__name__)
        
        row = document_data.get("row", -1)
        logger.info(f"Delete document requested for row {row}")
        
        if not self.current_database or not self.current_collection:
            QMessageBox.warning(self, "Warning", "No collection selected.")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the document at row {row}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # TODO: Implement actual document deletion by row
            # For now, just remove from table
            if self.data_table.remove_selected_row():
                QMessageBox.information(self, "Success", "Document removed from table.")
                # Refresh the documents to update counts
                self.refresh_documents()
            else:
                QMessageBox.warning(self, "Warning", "No document selected for deletion.")
    
    def on_insert_document(self):
        """Handle insert document toolbar action."""
        if not self.current_database or not self.current_collection:
            QMessageBox.warning(self, "Warning", "Please select a collection first.")
            return
        self.tab_widget.setCurrentIndex(1)  # Operations tab
    
    def on_update_document(self):
        """Handle update document toolbar action."""
        if not self.current_database or not self.current_collection:
            QMessageBox.warning(self, "Warning", "Please select a collection first.")
            return
        self.tab_widget.setCurrentIndex(1)  # Operations tab
    
    def on_delete_document(self):
        """Handle delete document toolbar action."""
        if not self.current_database or not self.current_collection:
            QMessageBox.warning(self, "Warning", "Please select a collection first.")
            return
        self.tab_widget.setCurrentIndex(1)  # Operations tab
    
    def on_execute_query(self):
        """Handle execute query toolbar action."""
        if not self.current_database or not self.current_collection:
            QMessageBox.warning(self, "Warning", "Please select a collection first.")
            return
        self.tab_widget.setCurrentIndex(2)  # Query tab
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
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
        if self.mongo_service.is_connected():
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "You are still connected to MongoDB. Do you want to disconnect and exit?",
                QMessageBox.Yes | QMessageBox.No
            )
            
        if reply == QMessageBox.Yes:
                self.mongo_service.disconnect_from_mongodb()
                event.accept()
                else:
                event.ignore()
                else:
            event.accept()