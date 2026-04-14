"""Main window for PDFNavigator."""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QProgressBar, QFileDialog, QMessageBox,
    QFrame, QGroupBox, QGridLayout
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon
from pathlib import Path

from pdfnavigator.ui.widgets import DropArea, StatusIndicator
from pdfnavigator.ui.styles import get_main_style, COLORS
from pdfnavigator.core.toc_detector import TOCDetector
from pdfnavigator.core.toc_parser import TOCParser
from pdfnavigator.core.font_chapter_detector import FontChapterDetector


class MainWindow(QMainWindow):
    """Main application window with modern styling."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDFNavigator - PDF 书签添加工具")
        self.setMinimumSize(700, 500)
        self.setStyleSheet(get_main_style())

        # Set window icon
        icon_path = Path(__file__).parent.parent / "assets" / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self._pdf_path: Path | None = None
        self._toc_page: int | None = None
        self._bookmarks = []

        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("PDFNavigator")
        title_label.setStyleSheet(f"""
            font-size: 22px;
            font-weight: bold;
            color: {COLORS['primary']};
        """)
        header_layout.addWidget(title_label)

        subtitle_label = QLabel("PDF 书签自动添加工具")
        subtitle_label.setStyleSheet(f"""
            font-size: 13px;
            color: {COLORS['text_secondary']};
            padding-left: 10px;
        """)
        header_layout.addWidget(subtitle_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # 操作流程说明 - 带箭头
        steps_frame = QFrame()
        steps_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_light']};
                border-radius: 8px;
                padding: 10px 15px;
            }}
        """)
        steps_layout = QHBoxLayout(steps_frame)
        steps_layout.setSpacing(5)

        steps = [
            ("①", "选择PDF"),
            ("②", "提取书签"),
            ("③", "编辑确认"),
            ("④", "保存导出"),
        ]
        for i, (num, text) in enumerate(steps):
            step_widget = QWidget()
            step_layout = QVBoxLayout(step_widget)
            step_layout.setSpacing(2)
            num_label = QLabel(num)
            num_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLORS['primary']}; background: transparent;")
            num_label.setAlignment(Qt.AlignCenter)
            step_layout.addWidget(num_label)
            txt_label = QLabel(text)
            txt_label.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']}; background: transparent;")
            txt_label.setAlignment(Qt.AlignCenter)
            step_layout.addWidget(txt_label)
            steps_layout.addWidget(step_widget)

            # 添加箭头（除了最后一个步骤）
            if i < len(steps) - 1:
                arrow_label = QLabel("→")
                arrow_label.setStyleSheet(f"font-size: 20px; color: {COLORS['primary']}; background: transparent; font-weight: bold;")
                arrow_label.setAlignment(Qt.AlignCenter)
                steps_layout.addWidget(arrow_label)

        steps_layout.addStretch()
        layout.addWidget(steps_frame)

        # Drop area
        self.drop_area = DropArea()
        self.drop_area.file_dropped.connect(self._on_file_dropped)
        layout.addWidget(self.drop_area)

        # File selection button - centered and styled
        select_layout = QHBoxLayout()
        select_layout.addStretch()
        self.select_btn = QPushButton("📂 浏览选择文件...")
        self.select_btn.clicked.connect(self._select_file)
        self.select_btn.setMinimumWidth(180)
        self.select_btn.setToolTip("点击打开文件选择对话框")
        select_layout.addWidget(self.select_btn)
        select_layout.addStretch()
        layout.addLayout(select_layout)

        # Progress section
        progress_frame = QFrame()
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setSpacing(8)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)

        self.status_indicator = StatusIndicator()
        progress_layout.addWidget(self.status_indicator)

        layout.addWidget(progress_frame)

        # Action buttons - clearer labels
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        self.process_button = QPushButton("▶ 开始提取书签")
        self.process_button.setObjectName("process_button")
        self.process_button.setEnabled(False)
        self.process_button.clicked.connect(self._process_pdf)
        self.process_button.setMinimumWidth(150)
        self.process_button.setToolTip("自动检测目录页或字体大小提取书签")
        btn_layout.addWidget(self.process_button)

        self.editor_button = QPushButton("✏ 编辑书签列表")
        self.editor_button.setObjectName("editor_button")
        self.editor_button.setEnabled(False)
        self.editor_button.clicked.connect(self._open_editor)
        self.editor_button.setMinimumWidth(150)
        self.editor_button.setToolTip("编辑、删除或调整书签层级")
        btn_layout.addWidget(self.editor_button)

        btn_layout.addStretch()

        self.exit_button = QPushButton("✕ 退出程序")
        self.exit_button.setObjectName("exit_button")
        self.exit_button.clicked.connect(self.close)
        self.exit_button.setMinimumWidth(100)
        btn_layout.addWidget(self.exit_button)

        layout.addLayout(btn_layout)

        # Footer
        footer = QLabel("提示: 支持目录页自动识别 | 字体大小章节检测 | 多级书签结构")
        footer.setStyleSheet(f"""
            font-size: 11px;
            color: {COLORS['text_secondary']};
            padding: 8px;
        """)
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)

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
        self.drop_area.set_file_loaded(path)
        self.status_indicator.set_status("就绪 - 点击「开始处理」提取书签", "normal")
        self.process_button.setEnabled(True)
        self.editor_button.setEnabled(False)
        self._bookmarks = []

    def _process_pdf(self):
        """Process the PDF to detect TOC and extract bookmarks."""
        if not self._pdf_path:
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_indicator.set_status("正在检测目录页...", "processing")
        self.process_button.setEnabled(False)

        # Detect TOC page
        detector = TOCDetector()
        self._toc_page = detector.detect(str(self._pdf_path))
        self.progress_bar.setValue(30)

        if self._toc_page is None:
            # TOC 检测失败，询问是否使用字体检测
            reply = QMessageBox.question(
                self, "目录页检测失败",
                "未检测到目录页。\n\n"
                "是否使用字体大小自动检测章节标题？\n"
                "（将扫描全文档，根据字体大小识别章节）",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Yes:
                self._use_font_detection()
            else:
                self.status_indicator.set_status("检测失败", "error")
                self.progress_bar.setVisible(False)
                self.process_button.setEnabled(True)
            return

        self.status_indicator.set_status(f"检测到目录页: 第 {self._toc_page + 1} 页，正在解析...", "processing")

        # Parse TOC
        parser = TOCParser()
        self._bookmarks = parser.parse(str(self._pdf_path), self._toc_page)
        self.progress_bar.setValue(100)

        if not self._bookmarks:
            # TOC 解析无结果，尝试字体检测
            reply = QMessageBox.question(
                self, "目录页解析失败",
                "目录页解析无结果。\n\n是否使用字体大小自动检测章节标题？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                self._use_font_detection()
            else:
                self.status_indicator.set_status("解析失败", "error")
                self.progress_bar.setVisible(False)
                self.process_button.setEnabled(True)
            return

        self.progress_bar.setVisible(False)
        self.status_indicator.set_status(f"✓ 提取完成，共 {len(self._bookmarks)} 个书签", "success")
        self.editor_button.setEnabled(True)
        self.process_button.setEnabled(True)

    def _use_font_detection(self):
        """Use font-based chapter detection."""
        self.status_indicator.set_status("正在扫描全文档，检测章节标题...", "processing")
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
            self.status_indicator.set_status("检测失败", "error")
            self.process_button.setEnabled(True)
            return

        self.status_indicator.set_status(f"✓ 字体检测完成，共 {len(self._bookmarks)} 个章节", "success")
        self.editor_button.setEnabled(True)
        self.process_button.setEnabled(True)

    def _open_editor(self):
        """Open the bookmark editor window."""
        from pdfnavigator.ui.editor_window import EditorWindow
        editor = EditorWindow(self._pdf_path, self._bookmarks, self)
        editor.exec()