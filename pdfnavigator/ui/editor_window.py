"""Bookmark editor window for PDFNavigator."""

import sys
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem, QPushButton, QFileDialog,
    QMessageBox, QLabel, QFrame, QHeaderView, QSplitter
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from pathlib import Path
from typing import List

from pdfnavigator.core.toc_parser import BookmarkEntry
from pdfnavigator.core.bookmark_writer import BookmarkWriter
from pdfnavigator.ui.styles import get_main_style, COLORS


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / relative_path
    else:
        return Path(__file__).parent.parent / "assets" / relative_path


class EditorWindow(QDialog):
    """Dialog for editing bookmark tree before saving."""

    def __init__(self, pdf_path: Path, bookmarks: List[BookmarkEntry], parent=None):
        super().__init__(parent)
        self._pdf_path = pdf_path
        self._original_bookmarks = list(bookmarks)
        self._bookmarks = list(bookmarks)

        self.setWindowTitle(f"编辑书签 - {pdf_path.name}")
        self.setMinimumSize(900, 650)
        self.setStyleSheet(get_main_style())

        # Set window icon
        icon_path = get_resource_path("icon.ico")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self._setup_ui()
        self._populate_tree()

    def _setup_ui(self):
        """Set up UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("书签编辑器")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLORS['text_primary']};")
        header_layout.addWidget(title)

        self.count_label = QLabel(f"共 {len(self._bookmarks)} 个书签")
        self.count_label.setStyleSheet(f"font-size: 14px; color: {COLORS['text_secondary']};")
        header_layout.addWidget(self.count_label)
        header_layout.addStretch()

        # File info
        file_label = QLabel(f"📄 {self._pdf_path.name}")
        file_label.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']};")
        header_layout.addWidget(file_label)

        layout.addLayout(header_layout)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet(f"background-color: {COLORS['border']}; max-height: 1px;")
        layout.addWidget(divider)

        # Toolbar buttons
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(10)

        self.add_btn = QPushButton("➕ 添加")
        self.add_btn.clicked.connect(self._add_bookmark)
        self.add_btn.setToolTip("添加新书签")
        toolbar_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton("➖ 删除")
        self.delete_btn.clicked.connect(self._delete_bookmark)
        self.delete_btn.setToolTip("删除选中书签")
        toolbar_layout.addWidget(self.delete_btn)

        toolbar_layout.addSpacing(20)

        self.level_up_btn = QPushButton("⬆ 升级")
        self.level_up_btn.clicked.connect(self._level_up)
        self.level_up_btn.setToolTip("提升层级 (变为父级)")
        toolbar_layout.addWidget(self.level_up_btn)

        self.level_down_btn = QPushButton("⬇ 降级")
        self.level_down_btn.clicked.connect(self._level_down)
        self.level_down_btn.setToolTip("降低层级 (变为子级)")
        toolbar_layout.addWidget(self.level_down_btn)

        toolbar_layout.addStretch()

        self.reset_btn = QPushButton("↺ 恢复原始")
        self.reset_btn.clicked.connect(self._reset_bookmarks)
        self.reset_btn.setToolTip("恢复为原始提取结果")
        toolbar_layout.addWidget(self.reset_btn)

        layout.addLayout(toolbar_layout)

        # Tree widget
        self.bookmark_tree = QTreeWidget()
        self.bookmark_tree.setHeaderLabels(["标题", "页码", "层级"])
        self.bookmark_tree.setColumnWidth(0, 450)
        self.bookmark_tree.setColumnWidth(1, 80)
        self.bookmark_tree.setColumnWidth(2, 80)
        self.bookmark_tree.setAlternatingRowColors(True)
        self.bookmark_tree.setAnimated(True)
        self.bookmark_tree.setSelectionMode(QTreeWidget.ExtendedSelection)
        self.bookmark_tree.expandAll()

        # Style tree items by level
        self.bookmark_tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {COLORS['bg_white']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
            }}
            QTreeWidget::item {{
                padding: 6px 8px;
                border-radius: 4px;
                margin: 2px 0;
            }}
            QTreeWidget::item:selected {{
                background-color: {COLORS['primary']};
                color: white;
            }}
            QTreeWidget::item:hover:!selected {{
                background-color: {COLORS['bg_light']};
            }}
        """)

        layout.addWidget(self.bookmark_tree)

        # Selection info
        self.selection_label = QLabel("提示: 双击可编辑标题和页码")
        self.selection_label.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']};")
        layout.addWidget(self.selection_label)

        # Bottom action buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        btn_layout.addStretch()

        self.save_button = QPushButton("💾 保存为新 PDF")
        self.save_button.setObjectName("save_button")
        self.save_button.clicked.connect(self._save_pdf)
        self.save_button.setMinimumWidth(150)
        btn_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setMinimumWidth(100)
        btn_layout.addWidget(self.cancel_button)

        layout.addLayout(btn_layout)

        # Connect selection change
        self.bookmark_tree.itemSelectionChanged.connect(self._update_selection_info)

    def _populate_tree(self):
        """Populate tree with bookmark entries."""
        self.bookmark_tree.clear()

        # Build hierarchical tree
        parent_items = {}  # level -> last item at that level

        for entry in self._bookmarks:
            item = QTreeWidgetItem([
                entry.title,
                str(entry.page + 1),
                f"L{entry.level}"
            ])
            item.setData(0, Qt.UserRole, entry)
            item.setFlags(item.flags() | Qt.ItemIsEditable)

            # Color by level
            level_colors = {
                1: COLORS['primary'],
                2: COLORS['success'],
                3: COLORS['warning'],
                4: COLORS['text_secondary'],
            }
            color = level_colors.get(entry.level, COLORS['text_primary'])

            # Add indentation based on level
            item.setText(0, f"{'  ' * (entry.level - 1)}{entry.title}")
            item.setForeground(0, Qt.darkBlue if entry.level == 1 else Qt.black)

            # Find parent item
            if entry.level == 1:
                self.bookmark_tree.addTopLevelItem(item)
            else:
                parent_level = entry.level - 1
                if parent_level in parent_items:
                    parent_items[parent_level].addChild(item)
                else:
                    self.bookmark_tree.addTopLevelItem(item)

            parent_items[entry.level] = item

        self.bookmark_tree.expandAll()
        self._update_count()

    def _update_count(self):
        """Update the count label."""
        self.count_label.setText(f"共 {len(self._bookmarks)} 个书签")

    def _update_selection_info(self):
        """Update selection info."""
        items = self.bookmark_tree.selectedItems()
        if items:
            self.selection_label.setText(f"已选择 {len(items)} 个书签")
        else:
            self.selection_label.setText("提示: 双击可编辑标题和页码")

    def _add_bookmark(self):
        """Add a new bookmark."""
        items = self.bookmark_tree.selectedItems()
        parent_page = 0
        parent_level = 1

        if items:
            parent_entry = items[0].data(0, Qt.UserRole)
            parent_page = parent_entry.page
            parent_level = parent_entry.level + 1 if parent_entry.level < 4 else 4

        entry = BookmarkEntry(title="新书签", page=parent_page, level=parent_level)
        self._bookmarks.append(entry)
        self._populate_tree()

    def _delete_bookmark(self):
        """Delete selected bookmark(s)."""
        items = self.bookmark_tree.selectedItems()
        if not items:
            return

        for item in items:
            entry = item.data(0, Qt.UserRole)
            self._bookmarks.remove(entry)
        self._populate_tree()

    def _level_up(self):
        """Increase level of selected items."""
        items = self.bookmark_tree.selectedItems()
        for item in items:
            entry = item.data(0, Qt.UserRole)
            if entry.level > 1:
                entry.level -= 1
        self._populate_tree()

    def _level_down(self):
        """Decrease level of selected items."""
        items = self.bookmark_tree.selectedItems()
        for item in items:
            entry = item.data(0, Qt.UserRole)
            if entry.level < 4:
                entry.level += 1
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
                QMessageBox.information(
                    self, "保存成功",
                    f"✓ 已保存到:\n{output_path}\n\n共写入 {len(self._bookmarks)} 个书签"
                )
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "保存失败", f"错误: {str(e)}")