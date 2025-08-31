"""
Status Bar Component
Handles the main status bar with connection status and progress indicators.
"""

from __future__ import annotations

from PySide6.QtCore import QObject
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QProgressBar, QStatusBar, QWidget


class StatusBar(QObject):
    """Status bar component for AtlasMogo application."""
    
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.parent = parent
        self.status_bar: QStatusBar | None = None
        self.connection_status: QLabel | None = None
        self.progress_bar: QProgressBar | None = None
        self._create_status_bar()
    
    def _create_status_bar(self) -> None:
        """Create the status bar widget."""
        self.status_bar = QStatusBar()
        
        # Connection status
        self.connection_status = QLabel("Disconnected")
        self.connection_status.setStyleSheet("color: red; font-weight: bold;")
        self.status_bar.addWidget(self.connection_status)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)
    
    def get_status_bar(self) -> QStatusBar | None:
        """Get the created status bar."""
        return self.status_bar
    
    def show_message(self, message: str, timeout: int = 0) -> None:
        """Show a message in the status bar."""
        if self.status_bar:
            self.status_bar.showMessage(message, timeout)
    
    def clear_message(self) -> None:
        """Clear the current status bar message."""
        if self.status_bar:
            self.status_bar.clearMessage()
    
    def set_connection_status(self, status: str, color: str = "black") -> None:
        """Set the connection status with color."""
        if self.connection_status:
            self.connection_status.setText(status)
            self.connection_status.setStyleSheet(f"color: {color}; font-weight: bold;")
    
    def show_progress(self, visible: bool = True) -> None:
        """Show or hide the progress bar."""
        if self.progress_bar:
            self.progress_bar.setVisible(visible)
    
    def set_progress_range(self, minimum: int, maximum: int) -> None:
        """Set the progress bar range."""
        if self.progress_bar:
            self.progress_bar.setRange(minimum, maximum)
    
    def set_progress_value(self, value: int) -> None:
        """Set the progress bar value."""
        if self.progress_bar:
            self.progress_bar.setValue(value)
    
    def set_indeterminate_progress(self, indeterminate: bool = True) -> None:
        """Set the progress bar to indeterminate mode."""
        if self.progress_bar:
            if indeterminate:
                self.progress_bar.setRange(0, 0)  # Indeterminate
            else:
                self.progress_bar.setRange(0, 100)
    
    def add_widget(self, widget: QWidget, stretch: int = 0) -> None:
        """Add a widget to the status bar."""
        if self.status_bar:
            self.status_bar.addWidget(widget, stretch)
    
    def add_permanent_widget(self, widget: QWidget, stretch: int = 0) -> None:
        """Add a permanent widget to the status bar."""
        if self.status_bar:
            self.status_bar.addPermanentWidget(widget, stretch)
    
    def remove_widget(self, widget: QWidget) -> None:
        """Remove a widget from the status bar."""
        if self.status_bar:
            self.status_bar.removeWidget(widget)
    
    def set_status_tip(self, widget: QWidget, tip: str) -> None:
        """Set the status tip for a widget."""
        if widget:
            widget.setStatusTip(tip)
    
    def set_tool_tip(self, widget: QWidget, tip: str) -> None:
        """Set the tool tip for a widget."""
        if widget:
            widget.setToolTip(tip)
