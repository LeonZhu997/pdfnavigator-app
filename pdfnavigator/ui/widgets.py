"""Custom widgets for PDFNavigator."""

from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QGridLayout
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFont, QPalette, QColor
from pathlib import Path
import fitz

from pdfnavigator.ui.styles import get_drop_area_style, get_drop_area_active_style, COLORS


class DropArea(QFrame):
    """A stylish widget that accepts drag-and-drop of PDF files."""

    file_dropped = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._is_active = False
        self._file_loaded = False
        self._file_path = None

        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        self.setStyleSheet(get_drop_area_style())
        self.setMinimumHeight(250)
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        # Icon hint - larger and more prominent
        self._icon_label = QLabel("📂")
        self._icon_label.setAlignment(Qt.AlignCenter)
        self._icon_label.setStyleSheet("font-size: 64px; background: transparent; border: none;")
        layout.addWidget(self._icon_label)

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

        # Sub text with instructions
        self._sub_label = QLabel("支持拖拽或点击下方按钮选择文件")
        self._sub_label.setAlignment(Qt.AlignCenter)
        self._sub_label.setStyleSheet(f"""
            font-size: 14px;
            color: {COLORS['text_secondary']};
            background: transparent;
            border: none;
        """)
        layout.addWidget(self._sub_label)

        # Hint box
        hint_box = QFrame()
        hint_box.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_white']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        hint_layout = QHBoxLayout(hint_box)
        hint_layout.setSpacing(10)

        hint_icon = QLabel("💡")
        hint_icon.setStyleSheet("font-size: 20px; background: transparent; border: none;")
        hint_layout.addWidget(hint_icon)

        hint_text = QLabel("提示：支持 .pdf 格式文件，文件大小不限")
        hint_text.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']}; background: transparent; border: none;")
        hint_layout.addWidget(hint_text)
        hint_layout.addStretch()

        layout.addWidget(hint_box)

        # File info section (hidden initially) - more prominent
        self._info_frame = QFrame()
        self._info_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_white']};
                border: 1px solid {COLORS['success']};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        info_layout = QHBoxLayout(self._info_frame)
        info_layout.setSpacing(25)

        self._pages_label = QLabel()
        self._pages_label.setStyleSheet(f"font-size: 14px; color: {COLORS['text_primary']}; background: transparent; border: none; font-weight: bold;")
        info_layout.addWidget(self._pages_label)

        self._size_label = QLabel()
        self._size_label.setStyleSheet(f"font-size: 14px; color: {COLORS['text_primary']}; background: transparent; border: none; font-weight: bold;")
        info_layout.addWidget(self._size_label)

        info_layout.addStretch()

        self._path_label = QLabel()
        self._path_label.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']}; background: transparent; border: none;")
        info_layout.addWidget(self._path_label)

        layout.addWidget(self._info_frame)
        self._info_frame.setVisible(False)

        self.setAcceptDrops(True)

    def set_file_loaded(self, file_path: str):
        """Update display when file is loaded."""
        self._file_loaded = True
        self._file_path = Path(file_path)
        self.setStyleSheet(get_drop_area_active_style())

        # Get PDF info
        try:
            doc = fitz.open(file_path)
            page_count = doc.page_count
            doc.close()
        except:
            page_count = "?"

        file_size = self._file_path.stat().st_size
        size_mb = file_size / (1024 * 1024)

        # Show PDF document icon - larger
        self._icon_label.setText("📄")
        self._icon_label.setStyleSheet(f"font-size: 72px; background: transparent; border: none; color: {COLORS['primary']};")

        # Update main text - show filename prominently with underline
        self._main_label.setText(self._file_path.name)
        self._main_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {COLORS['text_primary']};
            background: transparent;
            border: none;
        """)

        # Update sub text with success indicator
        self._sub_label.setText("✓ 已加载，点击「开始提取书签」")
        self._sub_label.setStyleSheet(f"""
            font-size: 14px;
            color: {COLORS['success']};
            background: transparent;
            border: none;
            font-weight: bold;
        """)

        # Show file info with better formatting
        self._pages_label.setText(f"📑 {page_count} 页")
        self._size_label.setText(f"📦 {size_mb:.1f} MB")
        # Show full path if not too long
        parent_path = str(self._file_path.parent)
        if len(parent_path) > 40:
            parent_path = parent_path[:40] + "..."
        self._path_label.setText(f"📁 {parent_path}")
        self._info_frame.setVisible(True)

    def reset(self):
        """Reset to initial state."""
        self._file_loaded = False
        self._file_path = None
        self.setStyleSheet(get_drop_area_style())

        self._icon_label.setText("📂")
        self._icon_label.setStyleSheet("font-size: 64px; background: transparent; border: none;")
        self._main_label.setText("拖拽 PDF 文件到此处")
        self._main_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {COLORS['primary']};
            background: transparent;
            border: none;
        """)
        self._sub_label.setText("支持拖拽或点击下方按钮选择文件")
        self._sub_label.setStyleSheet(f"""
            font-size: 14px;
            color: {COLORS['text_secondary']};
            background: transparent;
            border: none;
        """)
        self._info_frame.setVisible(False)

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