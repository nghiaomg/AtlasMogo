"""
Toast Notification System
Provides toast notifications with fade-in/out animations for user feedback.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QPropertyAnimation, QTimer, Qt, QEasingCurve, QRect
from PySide6.QtGui import QFont, QPalette
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout

import qtawesome as fa


class ToastNotification(QWidget):
    """Toast notification widget with fade-in/out animations."""
    
    def __init__(self, message: str, notification_type: str = "success", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.message = message
        self.notification_type = notification_type
        self.fade_in_animation: Optional[QPropertyAnimation] = None
        self.fade_out_animation: Optional[QPropertyAnimation] = None
        self.auto_hide_timer: Optional[QTimer] = None
        
        self._setup_ui()
        self._setup_animations()
    
    def _setup_ui(self) -> None:
        """Setup the toast notification UI."""
        # Set window flags for overlay behavior
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Toast container
        toast_container = QWidget()
        toast_container.setObjectName("toast-container")
        
        # Set styles based on notification type
        if self.notification_type == "success":
            background_color = "#10b981"
            border_color = "#059669"
            icon_color = "#ffffff"
        elif self.notification_type == "error":
            background_color = "#ef4444"
            border_color = "#dc2626"
            icon_color = "#ffffff"
        elif self.notification_type == "warning":
            background_color = "#f59e0b"
            border_color = "#d97706"
            icon_color = "#ffffff"
        else:  # info
            background_color = "#3b82f6"
            border_color = "#2563eb"
            icon_color = "#ffffff"
        
        toast_container.setStyleSheet(f"""
            QWidget#toast-container {{
                background-color: {background_color};
                border: 1px solid {border_color};
                border-radius: 8px;
                padding: 12px 16px;
                min-width: 300px;
                max-width: 400px;
            }}
        """)
        
        # Toast content layout
        content_layout = QHBoxLayout(toast_container)
        content_layout.setSpacing(12)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Icon
        icon_label = QLabel()
        if self.notification_type == "success":
            icon_label.setPixmap(fa.icon('fa6s.check', color=icon_color).pixmap(20, 20))
        elif self.notification_type == "error":
            icon_label.setPixmap(fa.icon('fa6s.exclamation', color=icon_color).pixmap(20, 20))
        elif self.notification_type == "warning":
            icon_label.setPixmap(fa.icon('fa6s.triangle-exclamation', color=icon_color).pixmap(20, 20))
        else:  # info
            icon_label.setPixmap(fa.icon('fa6s.info', color=icon_color).pixmap(20, 20))
        
        content_layout.addWidget(icon_label)
        
        # Message
        message_label = QLabel(self.message)
        message_label.setFont(QFont("Arial", 11))
        message_label.setStyleSheet(f"color: {icon_color}; font-weight: 500;")
        message_label.setWordWrap(True)
        content_layout.addWidget(message_label)
        
        layout.addWidget(toast_container)
    
    def _setup_animations(self) -> None:
        """Setup fade-in and fade-out animations."""
        # Fade-in animation
        self.fade_in_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_animation.setDuration(300)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Fade-out animation
        self.fade_out_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out_animation.setDuration(300)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.InCubic)
        self.fade_out_animation.finished.connect(self.close)
        
        # Auto-hide timer
        self.auto_hide_timer = QTimer()
        self.auto_hide_timer.setSingleShot(True)
        self.auto_hide_timer.timeout.connect(self._start_fade_out)
    
    def show_toast(self, duration: int = 3000) -> None:
        """Show the toast notification with fade-in animation."""
        # Position the toast in the bottom-right corner of the parent
        if self.parent():
            parent_rect = self.parent().rect()
            toast_width = self.sizeHint().width()
            toast_height = self.sizeHint().height()
            x = parent_rect.right() - toast_width - 20
            y = parent_rect.bottom() - toast_height - 20
            self.move(x, y)
        
        # Start fade-in animation
        self.setWindowOpacity(0.0)
        self.show()
        self.fade_in_animation.start()
        
        # Start auto-hide timer
        self.auto_hide_timer.start(duration)
    
    def _start_fade_out(self) -> None:
        """Start the fade-out animation."""
        self.fade_out_animation.start()


class ToastManager:
    """Manager for showing toast notifications."""
    
    _instance: Optional[ToastManager] = None
    
    def __new__(cls) -> ToastManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._active_toasts: list[ToastNotification] = []
    
    def show_success(self, message: str, parent: QWidget | None = None, duration: int = 3000) -> None:
        """Show a success toast notification."""
        self._show_toast(message, "success", parent, duration)
    
    def show_error(self, message: str, parent: QWidget | None = None, duration: int = 3000) -> None:
        """Show an error toast notification."""
        self._show_toast(message, "error", parent, duration)
    
    def show_warning(self, message: str, parent: QWidget | None = None, duration: int = 3000) -> None:
        """Show a warning toast notification."""
        self._show_toast(message, "warning", parent, duration)
    
    def show_info(self, message: str, parent: QWidget | None = None, duration: int = 3000) -> None:
        """Show an info toast notification."""
        self._show_toast(message, "info", parent, duration)
    
    def _show_toast(self, message: str, notification_type: str, parent: QWidget | None = None, duration: int = 3000) -> None:
        """Show a toast notification."""
        toast = ToastNotification(message, notification_type, parent)
        self._active_toasts.append(toast)
        
        # Remove from active list when closed
        toast.destroyed.connect(lambda: self._active_toasts.remove(toast) if toast in self._active_toasts else None)
        
        toast.show_toast(duration)
