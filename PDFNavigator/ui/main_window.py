"""Main window for PDFNavigator."""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QProgressBar, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from pathlib import Path

from PDFNavigator.ui.widgets import DropArea
from PDFNavigator.core.toc_detector import TOCDetector
from PDFNavigator.core.toc_parser import TOCParser
from PDFNavigator.core.font_chapter_detector import FontChapterDetector


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDFNavigator - PDF 书签添加工具")
        self.setMinimumSize(600, 400)

        self._pdf_path: Path | None = None
        self._toc_page: int | None = None
        self._bookmarks = []

        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # File selection area
        self.drop_area = DropArea()
        self.drop_area.file_dropped.connect(self._on_file_dropped)
        layout.addWidget(self.drop_area)

        # File selection button
        select_btn = QPushButton("选择 PDF 文件")
        select_btn.clicked.connect(self._select_file)
        layout.addWidget(select_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("请选择一个 PDF 文件")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Buttons
        btn_layout = QHBoxLayout()
        self.process_button = QPushButton("开始处理")
        self.process_button.setEnabled(False)
        self.process_button.clicked.connect(self._process_pdf)
        btn_layout.addWidget(self.process_button)

        self.editor_button = QPushButton("打开编辑器")
        self.editor_button.setEnabled(False)
        self.editor_button.clicked.connect(self._open_editor)
        btn_layout.addWidget(self.editor_button)

        self.exit_button = QPushButton("退出")
        self.exit_button.clicked.connect(self.close)
        btn_layout.addWidget(self.exit_button)

        layout.addLayout(btn_layout)

    def _select_file(self):
        """Open file dialog to select PDF."""
        path, _ = QFileDialog.getOpenFileName(
            self, "选择 PDF 文件", "", "PDF Files (*.pdf)"
        )
        if path:
            self._on_file_dropped(path)

    def _on_file_dropped(self, path: str):
        """Handle file selection."""
        self._pdf_path = Path(path)
        self.drop_area.setText(f"已选择: {self._pdf_path.name}")
        self.status_label.setText("文件已加载，点击 '开始处理' 提取书签")
        self.process_button.setEnabled(True)

    def _process_pdf(self):
        """Process the PDF to detect TOC and extract bookmarks."""
        if not self._pdf_path:
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("正在检测目录页...")

        # Detect TOC page
        detector = TOCDetector()
        self._toc_page = detector.detect(str(self._pdf_path))
        self.progress_bar.setValue(30)

        if self._toc_page is None:
            # TOC 检测失败，询问是否使用字体检测
            reply = QMessageBox.question(
                self, "目录页检测失败",
                "未检测到目录页。\n\n是否使用字体大小自动检测章节标题？\n（将扫描全文档，根据字体大小识别章节）",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Yes:
                self._use_font_detection()
            else:
                self.status_label.setText("检测失败，请选择其他 PDF 文件")
                self.progress_bar.setVisible(False)
            return

        self.status_label.setText(f"检测到目录页: 第 {self._toc_page + 1} 页，正在解析...")

        # Parse TOC
        parser = TOCParser()
        self._bookmarks = parser.parse(str(self._pdf_path), self._toc_page)
        self.progress_bar.setValue(100)

        if not self._bookmarks:
            # TOC 解析无结果，尝试字体检测
            reply = QMessageBox.question(
                self, "目录页解析失败",
                f"目录页解析无结果。\n\n是否使用字体大小自动检测章节标题？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                self._use_font_detection()
            else:
                self.status_label.setText("解析失败")
                self.progress_bar.setVisible(False)
            return

        self.status_label.setText(f"提取完成，共 {len(self._bookmarks)} 个书签")
        self.editor_button.setEnabled(True)
        self.progress_bar.setVisible(False)

    def _use_font_detection(self):
        """Use font-based chapter detection."""
        self.status_label.setText("正在扫描全文档，检测章节标题...")
        self.progress_bar.setValue(50)

        font_detector = FontChapterDetector()
        self._bookmarks = font_detector.detect(str(self._pdf_path))

        self.progress_bar.setValue(100)
        self.progress_bar.setVisible(False)

        if not self._bookmarks:
            QMessageBox.warning(
                self, "检测失败",
                "字体检测未找到章节标题。\n可能该文档没有明显的标题格式。"
            )
            self.status_label.setText("检测失败")
            return

        self.status_label.setText(f"字体检测完成，共 {len(self._bookmarks)} 个章节")
        self.editor_button.setEnabled(True)

    def _open_editor(self):
        """Open the bookmark editor window."""
        from PDFNavigator.ui.editor_window import EditorWindow
        editor = EditorWindow(self._pdf_path, self._bookmarks, self)
        editor.exec()