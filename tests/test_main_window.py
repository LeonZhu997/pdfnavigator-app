import pytest
from PySide6.QtWidgets import QApplication
from pdfnavigator.ui.main_window import MainWindow


@pytest.fixture
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_main_window_exists(app):
    """MainWindow should be created."""
    window = MainWindow()
    assert window is not None


def test_main_window_has_drop_area(app):
    """MainWindow should have DropArea widget."""
    window = MainWindow()
    assert window.drop_area is not None


def test_main_window_has_buttons(app):
    """MainWindow should have action buttons."""
    window = MainWindow()
    assert window.process_button is not None
    assert window.exit_button is not None