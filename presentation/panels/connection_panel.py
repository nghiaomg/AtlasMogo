"""
Connection Panel Component
Handles the MongoDB connection configuration and status display.
"""

from __future__ import annotations

import qtawesome as fa
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget
)

# Import styles
from ..styles.styles import BUTTON_STYLES, CONNECTION_PANEL_STYLE


class ConnectionPanel(QObject):
    """Connection panel component for MongoDB connection configuration."""
    
    # Signals
    connect_requested = Signal(str)  # Emits connection string
    disconnect_requested = Signal()
    test_requested = Signal(str)  # Emits connection string for testing
    
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.parent = parent
        self.widget: QGroupBox | None = None
        self.connection_input: QLineEdit | None = None
        self.connection_status_label: QLabel | None = None
        self.loading_spinner: QLabel | None = None
        self.connection_message: QLabel | None = None
        self.connect_button: QPushButton | None = None
        self.disconnect_button: QPushButton | None = None
        self.test_button: QPushButton | None = None
        self.main_layout: QFormLayout | None = None
        self._create_connection_panel()
    
    def _create_connection_panel(self) -> None:
        """Create the connection configuration panel."""
        self.widget = QGroupBox("MongoDB Connection")
        self.widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.widget.setMaximumHeight(140)
        self.widget.setStyleSheet(CONNECTION_PANEL_STYLE)
        
        # Main layout
        self.main_layout = QFormLayout(self.widget)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(12, 16, 12, 12)
        
        self._create_connection_input(self.main_layout)
        self._create_status_section(self.main_layout)
        self._create_button_section(self.main_layout)
    
    def _create_connection_input(self, parent_layout: QFormLayout) -> None:
        """Create the connection string input field."""
        self.connection_input = QLineEdit()
        self.connection_input.setPlaceholderText("mongodb://localhost:27017")
        self.connection_input.setText("mongodb://localhost:27017")
        self.connection_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.connection_input.setMinimumHeight(28)
        parent_layout.addRow("Connection String:", self.connection_input)
    
    def _create_status_section(self, parent_layout: QFormLayout) -> None:
        """Create the status display section."""
        status_layout = QHBoxLayout()
        status_layout.setSpacing(10)
        
        # Connection status label
        self.connection_status_label = QLabel("Disconnected")
        self.connection_status_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #dc3545;")
        self.connection_status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.connection_status_label.setMinimumHeight(24)
        
        # Loading indicator (text-based)
        self.loading_spinner = QLabel("Connecting...")
        self.loading_spinner.setStyleSheet("font-size: 12px; color: #007bff;")
        self.loading_spinner.setVisible(False)
        self.loading_spinner.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
        # Connection message
        self.connection_message = QLabel("Ready to connect")
        self.connection_message.setStyleSheet("color: #6c757d; font-size: 12px;")
        self.connection_message.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.connection_message.setMinimumHeight(24)
        
        status_layout.addWidget(self.connection_status_label)
        status_layout.addWidget(self.loading_spinner)
        status_layout.addWidget(self.connection_message)
        
        parent_layout.addRow("", status_layout)
    
    def _create_button_section(self, parent_layout: QFormLayout) -> None:
        """Create the connection control buttons."""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        # Connect button - modern flat style with primary accent
        self.connect_button = QPushButton(fa.icon('fa6s.play'), " Connect")
        self.connect_button.setObjectName("connectButton")
        self.connect_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.connect_button.setMinimumHeight(24)
        self.connect_button.setMinimumWidth(80)
        self.connect_button.clicked.connect(self._on_connect_clicked)
        self.connect_button.setStyleSheet(BUTTON_STYLES['connect_primary'])
        
        # Disconnect button - modern flat style with danger accent
        self.disconnect_button = QPushButton(fa.icon('fa6s.stop'), " Disconnect")
        self.disconnect_button.setObjectName("disconnectButton")
        self.disconnect_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.disconnect_button.setMinimumHeight(24)
        self.disconnect_button.setMinimumWidth(80)
        self.disconnect_button.setEnabled(False)
        self.disconnect_button.clicked.connect(self._on_disconnect_clicked)
        self.disconnect_button.setStyleSheet(BUTTON_STYLES['connect_danger'])
        
        # Test connection button - modern flat style with warning accent
        self.test_button = QPushButton(fa.icon('fa6s.check'), " Test")
        self.test_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.test_button.setMinimumHeight(24)
        self.test_button.setMinimumWidth(60)
        self.test_button.clicked.connect(self._on_test_clicked)
        self.test_button.setStyleSheet(BUTTON_STYLES['connect_warning'])
        
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.disconnect_button)
        button_layout.addWidget(self.test_button)
        button_layout.addStretch()
        
        parent_layout.addRow("", button_layout)
    
    def _on_connect_clicked(self) -> None:
        """Handle connect button click."""
        connection_string = self.connection_input.text().strip()
        if connection_string:
            self.connect_requested.emit(connection_string)
    
    def _on_disconnect_clicked(self) -> None:
        """Handle disconnect button click."""
        self.disconnect_requested.emit()
    
    def _on_test_clicked(self) -> None:
        """Handle test connection button click."""
        connection_string = self.connection_input.text().strip()
        if connection_string:
            self.test_requested.emit(connection_string)
    
    def get_widget(self) -> QGroupBox | None:
        """Get the connection panel widget."""
        return self.widget
    
    def get_connection_string(self) -> str:
        """Get the current connection string."""
        if self.connection_input:
            return self.connection_input.text().strip()
        return ""
    
    def set_connection_string(self, connection_string: str) -> None:
        """Set the connection string input."""
        if self.connection_input:
            self.connection_input.setText(connection_string)
    
    def set_connection_state(self, state: str) -> None:
        """Set the connection state display."""
        if state == "disconnected":
            self.connection_status_label.setText("Disconnected")
            self.connection_status_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #dc3545;")
            self.connection_message.setText("Ready to connect")
            self.connection_message.setStyleSheet("color: #6c757d; font-size: 12px;")
            self.loading_spinner.setVisible(False)
            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)
            self.test_button.setEnabled(True)
            # Show the connection panel when disconnected
            self.show_connection_panel()
            
        elif state == "connecting":
            self.connection_status_label.setText("Connecting...")
            self.connection_status_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #ffc107;")
            self.connection_message.setText("Establishing connection...")
            self.connection_message.setStyleSheet("color: #007bff; font-weight: bold;")
            self.loading_spinner.setVisible(True)
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(False)
            self.test_button.setEnabled(False)
            
        elif state == "connected":
            self.connection_status_label.setText("Connected")
            self.connection_status_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #28a745;")
            # Extract host from connection string for cleaner display
            connection_string = self.connection_input.text().strip()
            if "localhost" in connection_string:
                host_display = "localhost"
            elif "://" in connection_string:
                host_display = connection_string.split("://")[1].split("/")[0]
            else:
                host_display = connection_string
            self.connection_message.setText(f"Connected to MongoDB at {host_display}")
            self.connection_message.setStyleSheet("color: #28a745; font-size: 12px;")
            self.loading_spinner.setVisible(False)
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
            self.test_button.setEnabled(False)
            # Completely hide the connection panel when connected
            self.hide_connection_panel()
            
        elif state == "failed":
            self.connection_status_label.setText("Connection Failed")
            self.connection_status_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #dc3545;")
            self.connection_message.setText("Connection attempt failed")
            self.connection_message.setStyleSheet("color: #dc3545; font-size: 12px;")
            self.loading_spinner.setVisible(False)
            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)
            self.test_button.setEnabled(True)
            # Show the connection panel when failed
            self.show_connection_panel()
    
    def set_test_result(self, success: bool, message: str) -> None:
        """Set the test connection result."""
        if success:
            self.connection_message.setText("Connection test successful!")
            self.connection_message.setStyleSheet("color: #28a745; font-weight: bold;")
        else:
            self.connection_message.setText("Connection test failed!")
            self.connection_message.setStyleSheet("color: #dc3545; font-weight: bold;")
    
    def reset_message(self) -> None:
        """Reset the connection message to default state."""
        # This will be called by a timer to reset the message
        pass
    
    def enable_input(self, enabled: bool = True) -> None:
        """Enable or disable the connection input field."""
        if self.connection_input:
            self.connection_input.setEnabled(enabled)
    
    def set_placeholder_text(self, text: str) -> None:
        """Set the placeholder text for the connection input."""
        if self.connection_input:
            self.connection_input.setPlaceholderText(text)
    
    def hide_connection_panel(self) -> None:
        """Completely hide the connection panel after successful connection."""
        self.widget.setVisible(False)
    
    def show_connection_panel(self) -> None:
        """Show the connection panel when disconnecting."""
        self.widget.setVisible(True)
