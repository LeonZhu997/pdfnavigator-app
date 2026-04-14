import pytest
from pathlib import Path
import fitz
from pdfnavigator.core.pdf_handler import PDFHandler


@pytest.fixture
def handler():
    return PDFHandler()


def test_handler_open_nonexistent_raises(handler):
    """Opening non-existent file should raise."""
    with pytest.raises(FileNotFoundError):
        handler.open("/nonexistent/file.pdf")


def test_handler_is_open_property(handler):
    """is_open property should reflect state."""
    assert handler.is_open is False


def test_handler_page_count_after_open(handler):
    """Page count should reflect opened PDF."""
    doc = fitz.open()
    doc.new_page(width=595, height=842)
    doc.new_page(width=595, height=842)
    test_path = Path("tests/samples/test_temp.pdf")
    doc.save(str(test_path))
    doc.close()

    handler.open(test_path)
    assert handler.page_count == 2
    handler.close()
    test_path.unlink()