import pytest
import fitz
from pathlib import Path
from PDFNavigator.core.toc_parser import TOCParser, BookmarkEntry


@pytest.fixture
def pdf_with_toc_content():
    """Create a test PDF with structured TOC."""
    doc = fitz.open()
    doc.new_page(width=595, height=842)  # Page 0: title
    page = doc.new_page(width=595, height=842)  # Page 1: TOC
    page.insert_text((72, 72), "目录", fontsize=24)
    page.insert_text((72, 120), "1. 引言 .................. 5")
    page.insert_text((72, 150), "  1.1 背景 ............... 6")
    page.insert_text((72, 180), "2. 方法 .................. 10")
    for _ in range(10):
        doc.new_page(width=595, height=842)

    path = Path("tests/samples/test_toc_parse.pdf")
    doc.save(str(path))
    doc.close()
    yield path
    path.unlink()


def test_parser_extract_entries(pdf_with_toc_content):
    """Parser should extract TOC entries."""
    parser = TOCParser()
    entries = parser.parse(str(pdf_with_toc_content), toc_page=1)
    assert len(entries) >= 2


def test_parser_infer_levels(pdf_with_toc_content):
    """Parser should infer correct levels."""
    parser = TOCParser()
    entries = parser.parse(str(pdf_with_toc_content), toc_page=1)
    level_1_entries = [e for e in entries if e.level == 1]
    assert len(level_1_entries) >= 2


def test_bookmark_entry_creation():
    """BookmarkEntry should be created correctly."""
    entry = BookmarkEntry(title="Chapter 1", page=10, level=1)
    assert entry.title == "Chapter 1"
    assert entry.page == 10
    assert entry.level == 1