"""
Presentation Layer
Main entry point for the presentation layer components.
"""

# Import main window
from .windows import MainWindow

# Import panels
from .panels import (
    ConnectionPanel,
    DataTable,
    OperationsPanel,
    QueryPanel,
    Sidebar,
    Toolbar,
    StatusBar,
    MenuBar
)

# Import dialogs and helpers
from .dialogs import (
    DialogHelper,
    DialogLogger,
    bind_button,
    log_dialog_creation,
    log_dialog_result,
    MessageBoxHelper,
    CustomMessageBox
)

# Import styles
from .styles import (
    BUTTON_STYLES,
    LABEL_STYLES,
    SIDEBAR_TREE_STYLE,
    CONTEXT_MENU_STYLE,
    DIALOG_STYLE,
    COLORS
)

__all__ = [
    # Windows
    'MainWindow',
    
    # Panels
    'ConnectionPanel',
    'DataTable',
    'OperationsPanel', 
    'QueryPanel',
    'Sidebar',
    'Toolbar',
    'StatusBar',
    'MenuBar',
    
    # Dialogs
    'DialogHelper',
    'DialogLogger',
    'bind_button',
    'log_dialog_creation',
    'log_dialog_result',
    'MessageBoxHelper',
    'CustomMessageBox',
    
    # Styles
    'BUTTON_STYLES',
    'LABEL_STYLES',
    'SIDEBAR_TREE_STYLE',
    'CONTEXT_MENU_STYLE',
    'DIALOG_STYLE',
    'COLORS'
]
