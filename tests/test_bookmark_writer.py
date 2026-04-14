import pytest
import fitz
from pathlib import Path
from pdfnavigator.core.bookmark_writer import BookmarkWriter
from pdfnavigator.core.toc_parser import BookmarkEntry


@pytest.fixture
def test_pdf_for_writing():
    """Create a test PDF for bookmark writing."""
    doc = fitz.open()
    for i in range(15):
        page = doc.new_page(width=595, height=842)
        page.insert_text((72, 72), f"Page {i + 1}")

    path = Path("tests/samples/test_write.pdf")
    doc.save(str(path))
    doc.close()
    yield path
    path.unlink()


@pytest.fixture
def bookmark_entries():
    return [
        BookmarkEntry(title="Chapter 1", page=0, level=1),
        BookmarkEntry(title="Section 1.1", page=2, level=2),
        BookmarkEntry(title="Chapter 2", page=5, level=1),
    ]


def test_writer_add_bookmarks(test_pdf_for_writing, bookmark_entries):
    """Writer should add bookmarks to PDF."""
    writer = BookmarkWriter()
    output_path = Path("tests/samples/test_output.pdf")
    writer.write(str(test_pdf_for_writing), bookmark_entries, str(output_path))

    doc = fitz.open(str(output_path))
    toc = doc.get_toc()
    assert len(toc) >= 3
    assert toc[0][1] == "Chapter 1"
    doc.close()
    output_path.unlink()


def test_writer_preserves_content(test_pdf_for_writing, bookmark_entries):
    """Writer should preserve original content."""
    writer = BookmarkWriter()
    output_path = Path("tests/samples/test_output2.pdf")
    writer.write(str(test_pdf_for_writing), bookmark_entries, str(output_path))

    doc = fitz.open(str(output_path))
    assert doc.page_count == 15
    doc.close()
    output_path.unlink()