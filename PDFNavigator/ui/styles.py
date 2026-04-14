"""Application styles for PDFNavigator."""

# Modern color palette
COLORS = {
    'primary': '#2563EB',       # 蓝色主色
    'primary_hover': '#1D4ED8',
    'success': '#10B981',       # 绿色
    'warning': '#F59E0B',       # 橙色
    'danger': '#EF4444',        # 红色
    'bg_light': '#F8FAFC',
    'bg_white': '#FFFFFF',
    'text_primary': '#1E293B',
    'text_secondary': '#64748B',
    'border': '#E2E8F0',
    'border_focus': '#94A3B8',
}

# Main application style
MAIN_STYLE = """
/* Global */
QMainWindow, QDialog {
    background-color: {{bg_light}};
}

QWidget {
    font-family: "Microsoft YaHei", "Segoe UI", Arial;
    font-size: 14px;
    color: {{text_primary}};
}

/* Labels */
QLabel {
    color: {{text_primary}};
    background: transparent;
}

/* Buttons */
QPushButton {
    background-color: {{bg_white}};
    border: 1px solid {{border}};
    border-radius: 6px;
    padding: 10px 20px;
    font-size: 14px;
    color: {{text_primary}};
    min-height: 20px;
}

QPushButton:hover {
    background-color: {{border}};
    border-color: {{border_focus}};
}

QPushButton:pressed {
    background-color: {{border}};
}

QPushButton:disabled {
    background-color: {{bg_light}};
    color: {{text_secondary}};
    border-color: {{border}};
}

/* Primary Buttons */
QPushButton#process_button,
QPushButton#save_button {
    background-color: {{primary}};
    border: none;
    color: white;
    font-weight: bold;
}

QPushButton#process_button:hover,
QPushButton#save_button:hover {
    background-color: {{primary_hover}};
}

QPushButton#process_button:disabled,
QPushButton#save_button:disabled {
    background-color: #94A3B8;
    color: #E2E8F0;
}

/* Success Button */
QPushButton#editor_button {
    background-color: {{success}};
    border: none;
    color: white;
}

QPushButton#editor_button:hover {
    background-color: #059669;
}

QPushButton#editor_button:disabled {
    background-color: #94A3B8;
}

/* Danger/Exit Button */
QPushButton#exit_button,
QPushButton#cancel_button {
    background-color: transparent;
    border: 1px solid {{danger}};
    color: {{danger}};
}

QPushButton#exit_button:hover,
QPushButton#cancel_button:hover {
    background-color: {{danger}};
    color: white;
}

/* Progress Bar */
QProgressBar {
    background-color: {{border}};
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: {{primary}};
    border-radius: 4px;
}

/* Tree Widget */
QTreeWidget {
    background-color: {{bg_white}};
    border: 1px solid {{border}};
    border-radius: 8px;
    padding: 8px;
    font-size: 13px;
}

QTreeWidget::item {
    padding: 8px 4px;
    border-radius: 4px;
    margin: 2px;
}

QTreeWidget::item:selected {
    background-color: {{primary}};
    color: white;
}

QTreeWidget::item:hover {
    background-color: {{border}};
}

QHeaderView::section {
    background-color: {{bg_light}};
    border: none;
    border-bottom: 1px solid {{border}};
    padding: 10px;
    font-weight: bold;
    color: {{text_secondary}};
}

/* Scrollbar */
QScrollBar:vertical {
    background-color: {{bg_light}};
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: {{border}};
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: {{border_focus}};
}

/* QMessageBox */
QMessageBox {
    background-color: {{bg_white}};
}

QMessageBox QLabel {
    font-size: 14px;
}
"""

# Drop area style (enhanced)
DROP_AREA_STYLE = """
QLabel {
    border: 3px dashed {{primary}};
    border-radius: 16px;
    padding: 40px 30px;
    background-color: #EEF2FF;
    font-size: 16px;
    color: {{primary}};
    font-weight: bold;
}
"""

DROP_AREA_ACTIVE_STYLE = """
QLabel {
    border: 3px solid {{success}};
    border-radius: 16px;
    padding: 40px 30px;
    background-color: #ECFDF5;
    font-size: 16px;
    color: {{success}};
    font-weight: bold;
}
"""

def get_main_style():
    """Get the main application style with colors applied."""
    style = MAIN_STYLE
    for key, value in COLORS.items():
        style = style.replace('{{' + key + '}}', value)
    return style

def get_drop_area_style():
    """Get the drop area style."""
    style = DROP_AREA_STYLE
    for key, value in COLORS.items():
        style = style.replace('{{' + key + '}}', value)
    return style

def get_drop_area_active_style():
    """Get the active drop area style."""
    style = DROP_AREA_ACTIVE_STYLE
    for key, value in COLORS.items():
        style = style.replace('{{' + key + '}}', value)
    return style