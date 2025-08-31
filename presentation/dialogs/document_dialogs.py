"""
Enhanced Document Dialogs
Provides improved document creation and editing dialogs with form-based and JSON editors.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel, 
    QLineEdit, QTextEdit, QPushButton, QComboBox, QFormLayout, 
    QScrollArea, QFrame, QGridLayout, QCheckBox, QSpinBox, QDoubleSpinBox,
    QListWidget, QListWidgetItem, QMessageBox, QSplitter
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QTextCursor, QSyntaxHighlighter, QTextCharFormat, QColor
import json
import qtawesome as fa
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import uuid

from .dialog_helper import DialogHelper
from ..styles.styles import COLORS, BUTTON_STYLES


class JSONSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for JSON text."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_formats()
    
    def _setup_formats(self):
        """Setup text formats for different JSON elements."""
        # String format
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#22863a"))
        self.string_format.setFontWeight(QFont.Bold)
        
        # Number format
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#005cc5"))
        
        # Boolean format
        self.boolean_format = QTextCharFormat()
        self.boolean_format.setForeground(QColor("#d73a49"))
        self.boolean_format.setFontWeight(QFont.Bold)
        
        # Null format
        self.null_format = QTextCharFormat()
        self.null_format.setForeground(QColor("#6f42c1"))
        self.null_format.setFontWeight(QFont.Bold)
        
        # Key format
        self.key_format = QTextCharFormat()
        self.key_format.setForeground(QColor("#24292e"))
        self.key_format.setFontWeight(QFont.Bold)
    
    def highlightBlock(self, text):
        """Highlight a block of text."""
        import re
        
        # Highlight strings
        string_pattern = r'"[^"]*"'
        for match in re.finditer(string_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.string_format)
        
        # Highlight numbers
        number_pattern = r'\b\d+\.?\d*\b'
        for match in re.finditer(number_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.number_format)
        
        # Highlight booleans
        boolean_pattern = r'\b(true|false)\b'
        for match in re.finditer(boolean_pattern, text, re.IGNORECASE):
            self.setFormat(match.start(), match.end() - match.start(), self.boolean_format)
        
        # Highlight null
        null_pattern = r'\bnull\b'
        for match in re.finditer(null_pattern, text, re.IGNORECASE):
            self.setFormat(match.start(), match.end() - match.start(), self.null_format)
