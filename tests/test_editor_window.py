import pytest
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PDFNavigator.ui.editor_window import EditorWindow
from PDFNavigator.core.toc_parser import BookmarkEntry


@pytest.fixture
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def sample_bookmarks():
    return [
        BookmarkEntry(title="Chapter 1", page=0, level=1),
        BookmarkEntry(title="Section 1.1", page=2, level=2),
        BookmarkEntry(title="Chapter 2", page=5, level=1),
    ]


def test_editor_window_exists(app, sample_bookmarks):
    """EditorWindow should be created."""
    window = EditorWindow(Path("test.pdf"), sample_bookmarks)
    assert window is not None


def test_editor_window_has_tree(app, sample_bookmarks):
    """EditorWindow should have bookmark tree."""
    window = EditorWindow(Path("test.pdf"), sample_bookmarks)
    assert window.bookmark_tree is not None


def test_editor_window_has_buttons(app, sample_bookmarks):
    """EditorWindow should have action buttons."""
    window = EditorWindow(Path("test.pdf"), sample_bookmarks)
    assert window.save_button is not None
    assert window.cancel_button is not None