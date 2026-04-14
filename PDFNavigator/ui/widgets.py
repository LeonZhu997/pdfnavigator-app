"""Custom widgets for PDFNavigator."""

from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFont, QPalette, QColor

from PDFNavigator.ui.styles import get_drop_area_style, get_drop_area_active_style, COLORS


class DropArea(QFrame):
    """A stylish widget that accepts drag-and-drop of PDF files."""

    file_dropped = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._is_active = False
        self._file_loaded = False

        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        self.setStyleSheet(get_drop_area_style())
        self.setMinimumHeight(150)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Icon hint (using text as placeholder)
        icon_label = QLabel("📄")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px; background: transparent; border: none;")
        layout.addWidget(icon_label)

        # Main text
        self._main_label = QLabel("拖拽 PDF 文件到此处")
        self._main_label.setAlignment(Qt.AlignCenter)
        self._main_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {COLORS['primary']};
            background: transparent;
            border: none;
        """)
        layout.addWidget(self._main_label)

        # Sub text
        self._sub_label = QLabel("或点击下方按钮选择文件")
        self._sub_label.setAlignment(Qt.AlignCenter)
        self._sub_label.setStyleSheet(f"""
            font-size: 14px;
            color: {COLORS['text_secondary']};
            background: transparent;
            border: none;
        """)
        layout.addWidget(self._sub_label)

        self.setAcceptDrops(True)

    def set_file_loaded(self, filename: str):
        """Update display when file is loaded."""
        self._file_loaded = True
        self.setStyleSheet(get_drop_area_active_style())

        self._main_label.setText(f"✓ 已加载")
        self._main_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {COLORS['success']};
            background: transparent;
            border: none;
        """)
        self._sub_label.setText(filename)
        self._sub_label.setStyleSheet(f"""
            font-size: 14px;
            color: {COLORS['text_primary']};
            background: transparent;
            border: none;
        """)

    def reset(self):
        """Reset to initial state."""
        self._file_loaded = False
        self.setStyleSheet(get_drop_area_style())

        self._main_label.setText("拖拽 PDF 文件到此处")
        self._main_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {COLORS['primary']};
            background: transparent;
            border: none;
        """)
        self._sub_label.setText("或点击下方按钮选择文件")
        self._sub_label.setStyleSheet(f"""
            font-size: 14px;
            color: {COLORS['text_secondary']};
            background: transparent;
            border: none;
        """)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().lower().endswith('.pdf'):
                self.setStyleSheet(get_drop_area_active_style())
                self._is_active = True
                self._main_label.setText("松开鼠标以添加文件")
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        """Reset style when drag leaves."""
        if not self._file_loaded:
            self.setStyleSheet(get_drop_area_style())
            self._main_label.setText("拖拽 PDF 文件到此处")
        self._is_active = False

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.file_dropped.emit(file_path)
            event.acceptProposedAction()


class StatusIndicator(QWidget):
    """A widget showing current status with icon."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._icon_label = QLabel("○")
        self._icon_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(self._icon_label)

        self._text_label = QLabel("就绪")
        layout.addWidget(self._text_label)
        layout.addStretch()

    def set_status(self, text: str, state: str = "normal"):
        """Set status text and icon.

        Args:
            text: Status text
            state: "normal", "processing", "success", "error"
        """
        icons = {
            "normal": "○",
            "processing": "◌",
            "success": "●",
            "error": "✗",
        }
        colors = {
            "normal": COLORS['text_secondary'],
            "processing": COLORS['primary'],
            "success": COLORS['success'],
            "error": COLORS['danger'],
        }

        self._icon_label.setText(icons.get(state, "○"))
        self._icon_label.setStyleSheet(f"font-size: 16px; color: {colors.get(state, COLORS['text_secondary'])};")
        self._text_label.setText(text)
        self._text_label.setStyleSheet(f"color: {colors.get(state, COLORS['text_primary'])};")