import pytest
from PySide6.QtWidgets import QApplication
from pdfnavigator.ui.widgets import DropArea


@pytest.fixture
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_drop_area_exists(app):
    """DropArea widget should be created."""
    widget = DropArea()
    assert widget is not None


def test_drop_area_accepts_drops(app):
    """DropArea should accept drops."""
    widget = DropArea()
    assert widget.acceptDrops()