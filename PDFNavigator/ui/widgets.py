"""Custom widgets for PDFNavigator."""

from PySide6.QtWidgets import QLabel, QWidget
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent


class DropArea(QLabel):
    """A widget that accepts drag-and-drop of PDF files."""

    file_dropped = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setText("拖拽 PDF 文件到此处\n或点击下方按钮选择文件")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #999;
                border-radius: 10px;
                padding: 20px;
                background-color: #f5f5f5;
                font-size: 14px;
                color: #666;
            }
        """)
        self.setMinimumHeight(100)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().lower().endswith('.pdf'):
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.file_dropped.emit(file_path)
            self.setText(f"已选择: {file_path}")
            event.acceptProposedAction()