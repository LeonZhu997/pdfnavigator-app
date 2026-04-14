"""Bookmark editor window for PDFNavigator."""

from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem, QPushButton, QFileDialog,
    QMessageBox, QLabel
)
from PySide6.QtCore import Qt
from pathlib import Path
from typing import List

from PDFNavigator.core.toc_parser import BookmarkEntry
from PDFNavigator.core.bookmark_writer import BookmarkWriter


class EditorWindow(QDialog):
    """Dialog for editing bookmark tree before saving."""

    def __init__(self, pdf_path: Path, bookmarks: List[BookmarkEntry], parent=None):
        super().__init__(parent)
        self._pdf_path = pdf_path
        self._original_bookmarks = list(bookmarks)
        self._bookmarks = list(bookmarks)

        self.setWindowTitle(f"编辑书签 - {pdf_path.name}")
        self.setMinimumSize(800, 600)

        self._setup_ui()
        self._populate_tree()

    def _setup_ui(self):
        """Set up UI components."""
        layout = QVBoxLayout(self)

        # Bookmark tree
        self.bookmark_tree = QTreeWidget()
        self.bookmark_tree.setHeaderLabels(["标题", "页码", "层级"])
        self.bookmark_tree.setColumnWidth(0, 400)
        self.bookmark_tree.setColumnWidth(1, 80)
        self.bookmark_tree.setColumnWidth(2, 60)
        layout.addWidget(self.bookmark_tree)

        # Toolbar buttons
        tool_layout = QHBoxLayout()
        add_btn = QPushButton("添加书签")
        add_btn.clicked.connect(self._add_bookmark)
        tool_layout.addWidget(add_btn)

        delete_btn = QPushButton("删除书签")
        delete_btn.clicked.connect(self._delete_bookmark)
        tool_layout.addWidget(delete_btn)

        reset_btn = QPushButton("恢复原始")
        reset_btn.clicked.connect(self._reset_bookmarks)
        tool_layout.addWidget(reset_btn)

        layout.addLayout(tool_layout)

        # Status
        self.status_label = QLabel(f"共 {len(self._bookmarks)} 个书签")
        layout.addWidget(self.status_label)

        # Bottom buttons
        btn_layout = QHBoxLayout()
        self.save_button = QPushButton("保存为新 PDF")
        self.save_button.clicked.connect(self._save_pdf)
        btn_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_button)

        layout.addLayout(btn_layout)

    def _populate_tree(self):
        """Populate tree with bookmark entries."""
        self.bookmark_tree.clear()

        for entry in self._bookmarks:
            item = QTreeWidgetItem([
                entry.title,
                str(entry.page + 1),
                str(entry.level)
            ])
            item.setData(0, Qt.UserRole, entry)
            self.bookmark_tree.addTopLevelItem(item)

        self.status_label.setText(f"共 {len(self._bookmarks)} 个书签")

    def _add_bookmark(self):
        """Add a new bookmark."""
        entry = BookmarkEntry(title="新书签", page=0, level=1)
        self._bookmarks.append(entry)
        self._populate_tree()

    def _delete_bookmark(self):
        """Delete selected bookmark."""
        item = self.bookmark_tree.currentItem()
        if item:
            entry = item.data(0, Qt.UserRole)
            self._bookmarks.remove(entry)
            self._populate_tree()

    def _reset_bookmarks(self):
        """Reset to original bookmarks."""
        self._bookmarks = list(self._original_bookmarks)
        self._populate_tree()

    def _save_pdf(self):
        """Save PDF with bookmarks."""
        # 默认保存到源 PDF 同目录，文件名加 _bookmarked
        default_name = str(self._pdf_path.stem) + "_bookmarked.pdf"
        default_dir = str(self._pdf_path.parent)
        default_path = str(Path(default_dir) / default_name)

        output_path, _ = QFileDialog.getSaveFileName(
            self, "保存 PDF", default_path, "PDF Files (*.pdf)"
        )

        if output_path:
            try:
                writer = BookmarkWriter()
                writer.write(str(self._pdf_path), self._bookmarks, output_path)
                QMessageBox.information(self, "保存成功", f"已保存到:\n{output_path}")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "保存失败", f"错误: {str(e)}")