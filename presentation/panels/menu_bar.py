"""
Menu Bar Component
Handles the main menu bar with File, Database, Tools, and Help menus.
"""

from PySide6.QtWidgets import QMenuBar, QMenu
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import QObject
import qtawesome as fa


class MenuBar(QObject):
    """Main menu bar for AtlasMogo application."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.menu_bar = None
        self.actions = {}
        self._create_menu_bar()
    
    def _create_menu_bar(self):
        """Create the main menu bar with all menus and actions."""
        self.menu_bar = QMenuBar()
        
        # File Menu
        self._create_file_menu()
        
        # Database Menu
        self._create_database_menu()
        
        # Tools Menu
        self._create_tools_menu()
        
        # Help Menu
        self._create_help_menu()
    
    def _create_file_menu(self):
        """Create the File menu with connection and data operations."""
        file_menu = self.menu_bar.addMenu("&File")
        
        # Connection actions
        new_connection_action = QAction("&New Connection", self.parent)
        new_connection_action.setShortcut(QKeySequence("Ctrl+N"))
        new_connection_action.setStatusTip("Create a new MongoDB connection")
        self.actions['new_connection'] = new_connection_action
        file_menu.addAction(new_connection_action)
        
        open_connection_action = QAction("&Open Connection", self.parent)
        open_connection_action.setShortcut(QKeySequence("Ctrl+O"))
        open_connection_action.setStatusTip("Open an existing connection")
        self.actions['open_connection'] = open_connection_action
        file_menu.addAction(open_connection_action)
        
        file_menu.addSeparator()
        
        # Data operations
        export_action = QAction("&Export Data", self.parent)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.setStatusTip("Export data to file")
        self.actions['export_data'] = export_action
        file_menu.addAction(export_action)
        
        import_action = QAction("&Import Data", self.parent)
        import_action.setShortcut(QKeySequence("Ctrl+I"))
        import_action.setStatusTip("Import data from file")
        self.actions['import_data'] = import_action
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("&Exit", self.parent)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.setStatusTip("Exit the application")
        self.actions['exit'] = exit_action
        file_menu.addAction(exit_action)
    
    def _create_database_menu(self):
        """Create the Database menu with database and collection operations."""
        database_menu = self.menu_bar.addMenu("&Database")
        
        # Database CRUD operations
        add_db_action = QAction(fa.icon('fa6s.plus'), "&Create Database", self.parent)
        add_db_action.setShortcut(QKeySequence("Ctrl+Shift+N"))
        add_db_action.setStatusTip("Create a new database")
        self.actions['create_database'] = add_db_action
        database_menu.addAction(add_db_action)
        
        list_db_action = QAction(fa.icon('fa6s.database'), "&List Databases", self.parent)
        list_db_action.setShortcut(QKeySequence("Ctrl+Shift+L"))
        list_db_action.setStatusTip("List all databases")
        self.actions['list_databases'] = list_db_action
        database_menu.addAction(list_db_action)
        
        rename_db_action = QAction(fa.icon('fa6s.pen'), "&Rename Database", self.parent)
        rename_db_action.setShortcut(QKeySequence("Ctrl+Shift+R"))
        rename_db_action.setStatusTip("Rename selected database")
        self.actions['rename_database'] = rename_db_action
        database_menu.addAction(rename_db_action)
        
        delete_db_action = QAction(fa.icon('fa6s.trash'), "&Delete Database", self.parent)
        delete_db_action.setShortcut(QKeySequence("Ctrl+Shift+Delete"))
        delete_db_action.setStatusTip("Delete selected database")
        self.actions['delete_database'] = delete_db_action
        database_menu.addAction(delete_db_action)
        
        database_menu.addSeparator()
        
        # Collection operations
        add_coll_action = QAction("&Add Collection", self.parent)
        add_coll_action.setShortcut(QKeySequence("Ctrl+Shift+C"))
        add_coll_action.setStatusTip("Create a new collection")
        self.actions['add_collection'] = add_coll_action
        database_menu.addAction(add_coll_action)
        
        database_menu.addSeparator()
        
        # Refresh action
        refresh_action = QAction("&Refresh", self.parent)
        refresh_action.setShortcut(QKeySequence("F5"))
        refresh_action.setStatusTip("Refresh databases and collections")
        self.actions['refresh'] = refresh_action
        database_menu.addAction(refresh_action)
    
    def _create_tools_menu(self):
        """Create the Tools menu with utility functions."""
        tools_menu = self.menu_bar.addMenu("&Tools")
        
        # Query builder
        query_builder_action = QAction("&Query Builder", self.parent)
        query_builder_action.setShortcut(QKeySequence("Ctrl+Q"))
        query_builder_action.setStatusTip("Open query builder tool")
        self.actions['query_builder'] = query_builder_action
        tools_menu.addAction(query_builder_action)
        
        # Performance monitor
        performance_action = QAction("&Performance Monitor", self.parent)
        performance_action.setShortcut(QKeySequence("Ctrl+P"))
        performance_action.setStatusTip("Open performance monitoring tool")
        self.actions['performance_monitor'] = performance_action
        tools_menu.addAction(performance_action)
        
        tools_menu.addSeparator()
        
        # Settings
        settings_action = QAction("&Settings", self.parent)
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.setStatusTip("Open application settings")
        self.actions['settings'] = settings_action
        tools_menu.addAction(settings_action)
    
    def _create_help_menu(self):
        """Create the Help menu with documentation and about."""
        help_menu = self.menu_bar.addMenu("&Help")
        
        # Documentation
        docs_action = QAction("&Documentation", self.parent)
        docs_action.setShortcut(QKeySequence("F1"))
        docs_action.setStatusTip("Open documentation")
        self.actions['documentation'] = docs_action
        help_menu.addAction(docs_action)
        
        help_menu.addSeparator()
        
        # About
        about_action = QAction("&About", self.parent)
        about_action.setStatusTip("About AtlasMogo")
        self.actions['about'] = about_action
        help_menu.addAction(about_action)
    
    def get_menu_bar(self):
        """Get the created menu bar."""
        return self.menu_bar
    
    def get_action(self, action_name: str):
        """Get a specific action by name."""
        return self.actions.get(action_name)
    
    def connect_action(self, action_name: str, slot):
        """Connect an action to a slot function."""
        action = self.actions.get(action_name)
        if action:
            action.triggered.connect(slot)
    
    def enable_action(self, action_name: str, enabled: bool = True):
        """Enable or disable a specific action."""
        action = self.actions.get(action_name)
        if action:
            action.setEnabled(enabled)
    
    def set_action_text(self, action_name: str, text: str):
        """Set the text for a specific action."""
        action = self.actions.get(action_name)
        if action:
            action.setText(text)
