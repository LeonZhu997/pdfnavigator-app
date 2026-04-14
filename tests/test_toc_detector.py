import pytest
import fitz
from pathlib import Path
from PDFNavigator.core.toc_detector import TOCDetector


@pytest.fixture
def detector():
    return TOCDetector()


@pytest.fixture
def pdf_with_toc_keyword():
    """Create a test PDF with TOC keyword."""
    doc = fitz.open()
    doc.new_page(width=595, height=842)  # Page 0: title
    page = doc.new_page(width=595, height=842)  # Page 1: TOC
    # Use china-s font for Chinese text support
    page.insert_text((72, 72), "目录", fontsize=24, fontname="china-s")
    page.insert_text((72, 120), "第一章 引言 ... 5", fontname="china-s")
    page.insert_text((72, 150), "第二章 方法 ... 10", fontname="china-s")
    doc.new_page(width=595, height=842)  # Page 2: content

    path = Path("tests/samples/test_toc_keyword.pdf")
    doc.save(str(path))
    doc.close()
    yield path
    path.unlink()


def test_detector_find_toc_page(detector, pdf_with_toc_keyword):
    """Detector should find TOC page."""
    result = detector.detect(str(pdf_with_toc_keyword))
    assert result == 1


def test_detector_keywords_config():
    """Detector should use configured keywords."""
    detector = TOCDetector()
    assert "目录" in detector.keywords
    assert "Contents" in detector.keywords