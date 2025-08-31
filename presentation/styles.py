"""
Central Stylesheet for AtlasMogo
Provides consistent colors and styling across the application.
"""

# Color palette - Modern, pleasant colors that work in both light and dark themes
COLORS = {
    # Primary colors
    'primary': '#3b82f6',           # Blue
    'primary_hover': '#2563eb',     # Darker blue for hover
    'primary_light': '#dbeafe',     # Very light blue for selection
    
    # Secondary colors
    'secondary': '#6b7280',         # Gray
    'secondary_hover': '#4b5563',   # Darker gray for hover
    
    # Success colors
    'success': '#10b981',           # Green
    'success_hover': '#059669',     # Darker green for hover
    
    # Warning colors
    'warning': '#f59e0b',           # Orange
    'warning_hover': '#d97706',     # Darker orange for hover
    
    # Danger colors
    'danger': '#ef4444',            # Red
    'danger_hover': '#dc2626',      # Darker red for hover
    
    # Neutral colors
    'white': '#ffffff',
    'light_gray': '#f9fafb',
    'gray': '#e5e7eb',
    'dark_gray': '#6b7280',
    'darker_gray': '#374151',
    'black': '#111827',
    
    # Background colors
    'bg_primary': '#ffffff',
    'bg_secondary': '#f9fafb',
    'bg_tertiary': '#f3f4f6',
    
    # Border colors
    'border_light': '#e5e7eb',
    'border_medium': '#d1d5db',
    'border_dark': '#9ca3af',
    
    # Text colors
    'text_primary': '#111827',
    'text_secondary': '#6b7280',
    'text_muted': '#9ca3af',
    'text_inverse': '#ffffff',
}

# Sidebar TreeView styles
SIDEBAR_TREE_STYLE = f"""
QTreeWidget {{
    border: 1px solid {COLORS['border_light']};
    border-radius: 8px;
    background-color: {COLORS['bg_primary']};
    alternate-background-color: {COLORS['bg_secondary']};
    selection-background-color: {COLORS['primary_light']};
    selection-color: {COLORS['text_primary']};
    font-size: 13px;
    outline: none;
}}

QTreeWidget::item {{
    padding: 10px 8px;
    border-radius: 6px;
    margin: 2px;
    border: none;
}}

QTreeWidget::item:selected {{
    background-color: {COLORS['primary_light']};
    color: {COLORS['text_primary']};
    font-weight: 500;
}}

QTreeWidget::item:hover {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_primary']};
}}

QTreeWidget::item:selected:hover {{
    background-color: {COLORS['primary']};
    color: {COLORS['text_inverse']};
}}

QTreeWidget::branch {{
    background-color: transparent;
}}

QTreeWidget::branch:has-children:!has-siblings:closed,
QTreeWidget::branch:closed:has-children:has-siblings {{
    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTYgNEwxMCA4TDYgMTJWNHoiIGZpbGw9IiM5Y2EzYWYiLz4KPC9zdmc+);
}}

QTreeWidget::branch:open:has-children:!has-siblings,
QTreeWidget::branch:open:has-children:has-siblings {{
    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQgNkw4IDEwTDEyIDZINHoiIGZpbGw9IiM5Y2EzYWYiLz4KPC9zdmc+);
}}
"""

# Data Table styles
DATA_TABLE_STYLE = f"""
QTableWidget {{
    border: 1px solid {COLORS['border_light']};
    border-radius: 8px;
    background-color: {COLORS['bg_primary']};
    gridline-color: {COLORS['border_light']};
    selection-background-color: {COLORS['primary_light']};
    selection-color: {COLORS['text_primary']};
    alternate-background-color: {COLORS['bg_secondary']};
    font-size: 13px;
    outline: none;
}}

QTableWidget::item {{
    padding: 12px 8px;
    border-radius: 4px;
    border: none;
}}

QTableWidget::item:selected {{
    background-color: {COLORS['primary_light']};
    color: {COLORS['text_primary']};
    font-weight: 500;
}}

QTableWidget::item:hover {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_primary']};
}}

QTableWidget::item:selected:hover {{
    background-color: {COLORS['primary']};
    color: {COLORS['text_inverse']};
}}

QHeaderView::section {{
    background-color: {COLORS['bg_tertiary']};
    border: none;
    border-bottom: 2px solid {COLORS['border_medium']};
    padding: 14px 10px;
    font-weight: 600;
    font-size: 13px;
    color: {COLORS['text_primary']};
    text-align: left;
}}

QHeaderView::section:hover {{
    background-color: {COLORS['border_light']};
}}

QHeaderView::section:pressed {{
    background-color: {COLORS['border_medium']};
}}
"""

# Button styles
BUTTON_STYLES = {
    'primary': f"""
        QPushButton {{
            background-color: {COLORS['primary']};
            color: {COLORS['text_inverse']};
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 12px;
            font-weight: 500;
            min-height: 32px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['primary_hover']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['primary_hover']};
        }}
        QPushButton:disabled {{
            background-color: {COLORS['gray']};
            color: {COLORS['text_muted']};
        }}
    """,
    
    'secondary': f"""
        QPushButton {{
            background-color: {COLORS['secondary']};
            color: {COLORS['text_inverse']};
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 12px;
            font-weight: 500;
            min-height: 32px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['secondary_hover']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['secondary_hover']};
        }}
        QPushButton:disabled {{
            background-color: {COLORS['gray']};
            color: {COLORS['text_muted']};
        }}
    """,
    
    'success': f"""
        QPushButton {{
            background-color: {COLORS['success']};
            color: {COLORS['text_inverse']};
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 12px;
            font-weight: 500;
            min-height: 32px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['success_hover']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['success_hover']};
        }}
        QPushButton:disabled {{
            background-color: {COLORS['gray']};
            color: {COLORS['text_muted']};
        }}
    """,
    
    'danger': f"""
        QPushButton {{
            background-color: {COLORS['danger']};
            color: {COLORS['text_inverse']};
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 12px;
            font-weight: 500;
            min-height: 32px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['danger_hover']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['danger_hover']};
        }}
        QPushButton:disabled {{
            background-color: {COLORS['gray']};
            color: {COLORS['text_muted']};
        }}
    """,
    
    # Modern flat button styles for sidebar
    'flat_neutral': f"""
        QPushButton {{
            background-color: transparent;
            color: {COLORS['text_secondary']};
            border: 1px solid {COLORS['border_light']};
            border-radius: 4px;
            padding: 6px 12px;
            font-size: 11px;
            font-weight: 500;
            min-height: 24px;
            min-width: 70px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['bg_tertiary']};
            color: {COLORS['text_primary']};
            border-color: {COLORS['border_medium']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['border_light']};
            color: {COLORS['text_primary']};
        }}
        QPushButton:disabled {{
            background-color: {COLORS['bg_secondary']};
            color: {COLORS['text_muted']};
            border-color: {COLORS['border_light']};
        }}
    """,
    
    'flat_accent': f"""
        QPushButton {{
            background-color: transparent;
            color: {COLORS['success']};
            border: 1px solid {COLORS['success']};
            border-radius: 4px;
            padding: 6px 12px;
            font-size: 11px;
            font-weight: 500;
            min-height: 24px;
            min-width: 70px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['success']};
            color: {COLORS['text_inverse']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['success_hover']};
            color: {COLORS['text_inverse']};
        }}
        QPushButton:disabled {{
            background-color: {COLORS['bg_secondary']};
            color: {COLORS['text_muted']};
            border-color: {COLORS['border_light']};
        }}
    """,
    
    # Connection panel button styles
    'connect_primary': f"""
        QPushButton {{
            background-color: transparent;
            color: {COLORS['primary']};
            border: 1px solid {COLORS['primary']};
            border-radius: 4px;
            padding: 6px 12px;
            font-size: 11px;
            font-weight: 500;
            min-height: 24px;
            min-width: 80px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['primary']};
            color: {COLORS['text_inverse']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['primary_hover']};
            color: {COLORS['text_inverse']};
        }}
        QPushButton:disabled {{
            background-color: {COLORS['bg_secondary']};
            color: {COLORS['text_muted']};
            border-color: {COLORS['border_light']};
        }}
    """,
    
    'connect_danger': f"""
        QPushButton {{
            background-color: transparent;
            color: {COLORS['danger']};
            border: 1px solid {COLORS['danger']};
            border-radius: 4px;
            padding: 6px 12px;
            font-size: 11px;
            font-weight: 500;
            min-height: 24px;
            min-width: 80px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['danger']};
            color: {COLORS['text_inverse']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['danger_hover']};
            color: {COLORS['text_inverse']};
        }}
        QPushButton:disabled {{
            background-color: {COLORS['bg_secondary']};
            color: {COLORS['text_muted']};
            border-color: {COLORS['border_light']};
        }}
    """,
    
    'connect_warning': f"""
        QPushButton {{
            background-color: transparent;
            color: {COLORS['warning']};
            border: 1px solid {COLORS['warning']};
            border-radius: 4px;
            padding: 6px 12px;
            font-size: 11px;
            font-weight: 500;
            min-height: 24px;
            min-width: 60px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['warning']};
            color: {COLORS['text_inverse']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['warning_hover']};
            color: {COLORS['text_inverse']};
        }}
        QPushButton:disabled {{
            background-color: {COLORS['bg_secondary']};
            color: {COLORS['text_muted']};
            border-color: {COLORS['border_light']};
        }}
    """,
    
    # Dialog button styles - Using exact colors specified
    'dialog_primary': f"""
        QPushButton {{
            background-color: #007BFF;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 12px;
            font-weight: 500;
            min-height: 28px;
            min-width: 80px;
        }}
        QPushButton:hover {{
            background-color: #0056b3;
        }}
        QPushButton:pressed {{
            background-color: #0056b3;
        }}
        QPushButton:disabled {{
            background-color: #E0E0E0;
            color: #9CA3AF;
        }}
    """,
    
    'dialog_destructive': f"""
        QPushButton {{
            background-color: #DC3545;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 12px;
            font-weight: 500;
            min-height: 28px;
            min-width: 80px;
        }}
        QPushButton:hover {{
            background-color: #a71d2a;
        }}
        QPushButton:pressed {{
            background-color: #a71d2a;
        }}
        QPushButton:disabled {{
            background-color: #E0E0E0;
            color: #9CA3AF;
        }}
    """,
    
         'dialog_secondary': f"""
         QPushButton {{
             background-color: #E0E0E0;
             color: #333333;
             border: 1px solid #D1D5DB;
             border-radius: 6px;
             padding: 8px 16px;
             font-size: 12px;
             font-weight: 500;
             min-height: 28px;
             min-width: 80px;
         }}
         QPushButton:hover {{
             background-color: #CFCFCF;
             color: #333333;
             border-color: #9CA3AF;
         }}
         QPushButton:pressed {{
             background-color: #CFCFCF;
             color: #333333;
         }}
         QPushButton:disabled {{
             background-color: #F3F4F6;
             color: #9CA3AF;
             border-color: #E5E7EB;
         }}
     """,
     
     # Neutral/Info button style for test, info, and informational actions
     'dialog_neutral': f"""
         QPushButton {{
             background-color: #17A2B8;
             color: white;
             border: none;
             border-radius: 6px;
             padding: 8px 16px;
             font-size: 12px;
             font-weight: 500;
             min-height: 28px;
             min-width: 80px;
         }}
         QPushButton:hover {{
             background-color: #11707F;
         }}
         QPushButton:pressed {{
             background-color: #11707F;
         }}
         QPushButton:disabled {{
             background-color: #E0E0E0;
             color: #9CA3AF;
         }}
     """
}

# Context menu styles
CONTEXT_MENU_STYLE = f"""
QMenu {{
    background-color: {COLORS['bg_primary']};
    border: 1px solid {COLORS['border_light']};
    border-radius: 8px;
    padding: 6px 0px;
    font-size: 13px;
    color: {COLORS['text_primary']};
}}

QMenu::item {{
    padding: 8px 16px;
    border: none;
    background-color: transparent;
    min-height: 20px;
    border-radius: 4px;
    margin: 1px 4px;
}}

QMenu::item:selected {{
    background-color: {COLORS['primary_light']};
    color: {COLORS['text_primary']};
    font-weight: 500;
}}

QMenu::item:hover {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_primary']};
}}

QMenu::item:selected:hover {{
    background-color: {COLORS['primary']};
    color: {COLORS['text_inverse']};
}}

QMenu::separator {{
    height: 1px;
    background-color: {COLORS['border_light']};
    margin: 4px 8px;
}}

QMenu::indicator {{
    width: 16px;
    height: 16px;
    margin-right: 8px;
}}

QMenu::icon {{
    margin-right: 8px;
    width: 16px;
    height: 16px;
}}
"""

# Connection panel styles
CONNECTION_PANEL_STYLE = f"""
QGroupBox {{
    border: 1px solid {COLORS['border_light']};
    border-radius: 8px;
    background-color: {COLORS['bg_primary']};
    margin-top: 8px;
    padding-top: 8px;
    font-size: 13px;
    font-weight: 600;
    color: {COLORS['text_primary']};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px 0 8px;
    color: {COLORS['text_primary']};
    font-weight: 600;
    font-size: 13px;
}}

QLineEdit {{
    border: 1px solid {COLORS['border_light']};
    border-radius: 4px;
    padding: 6px 10px;
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
    font-size: 12px;
    selection-background-color: {COLORS['primary_light']};
}}

QLineEdit:focus {{
    border-color: {COLORS['primary']};
    outline: none;
}}

QLineEdit:disabled {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_muted']};
    border-color: {COLORS['border_light']};
}}
"""

# Dialog styles
DIALOG_STYLE = f"""
QDialog {{
    background-color: {COLORS['bg_primary']};
    border: 1px solid {COLORS['border_light']};
    border-radius: 8px;
}}

QDialog QLabel {{
    color: {COLORS['text_primary']};
}}

QDialog QLineEdit {{
    border: 1px solid {COLORS['border_light']};
    border-radius: 4px;
    padding: 8px 12px;
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
    font-size: 12px;
    selection-background-color: {COLORS['primary_light']};
}}

QDialog QLineEdit:focus {{
    border-color: {COLORS['primary']};
    outline: none;
}}

QDialog QTextEdit {{
    border: 1px solid {COLORS['border_light']};
    border-radius: 4px;
    padding: 8px 12px;
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
    font-size: 12px;
    selection-background-color: {COLORS['primary_light']};
}}

QDialog QTextEdit:focus {{
    border-color: {COLORS['primary']};
    outline: none;
}}

QDialog QComboBox {{
    border: 1px solid {COLORS['border_light']};
    border-radius: 4px;
    padding: 6px 10px;
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
    font-size: 12px;
    min-height: 20px;
}}

QDialog QComboBox:focus {{
    border-color: {COLORS['primary']};
    outline: none;
}}

QDialog QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QDialog QComboBox::down-arrow {{
    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTMgNEw2IDdMOSA0SDN6IiBmaWxsPSIjNmI3MjgwIi8+Cjwvc3ZnPgo=);
}}

QDialog QGroupBox {{
    border: 1px solid {COLORS['border_light']};
    border-radius: 6px;
    margin-top: 8px;
    padding-top: 8px;
    font-size: 12px;
    font-weight: 600;
    color: {COLORS['text_primary']};
}}

QDialog QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px 0 6px;
    color: {COLORS['text_primary']};
    font-weight: 600;
    font-size: 12px;
}}
"""

# Label styles
LABEL_STYLES = {
    'header': f"""
        QLabel {{
            color: {COLORS['text_primary']};
            font-size: 14px;
            font-weight: 600;
        }}
    """,
    
    'subheader': f"""
        QLabel {{
            color: {COLORS['text_secondary']};
            font-size: 12px;
            font-weight: 500;
        }}
    """,
    
    'muted': f"""
        QLabel {{
            color: {COLORS['text_muted']};
            font-size: 11px;
            font-style: italic;
        }}
    """
}
