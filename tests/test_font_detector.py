"""Tests for FontChapterDetector."""

import pytest
import fitz
from pathlib import Path

from pdfnavigator.core.font_chapter_detector import FontChapterDetector
from pdfnavigator.core.toc_parser import BookmarkEntry


@pytest.fixture
def detector():
    return FontChapterDetector()


@pytest.fixture
def pdf_with_font_sizes():
    """Create a test PDF with different font sizes for titles."""
    doc = fitz.open()

    # Page 1 - with large title
    page1 = doc.new_page(width=595, height=842)
    # 正文字体 12pt
    page1.insert_text((72, 100), "第一章 引言", fontsize=18, fontname="helv")  # 大标题
    page1.insert_text((72, 150), "这是正文内容，使用较小的字体。", fontsize=12, fontname="helv")
    page1.insert_text((72, 180), "1.1 背景", fontsize=14, fontname="helv")  # 小节标题
    page1.insert_text((72, 210), "更多正文内容。", fontsize=12, fontname="helv")

    # Page 2 - another chapter
    page2 = doc.new_page(width=595, height=842)
    page2.insert_text((72, 100), "第二章 方法", fontsize=18, fontname="helv")
    page2.insert_text((72, 150), "正文内容。", fontsize=12, fontname="helv")

    path = Path("tests/samples/test_font_sizes.pdf")
    doc.save(str(path))
    doc.close()
    yield path
    path.unlink()


def test_detector_basic(detector, pdf_with_font_sizes):
    """Detector should find chapter titles based on font size."""
    entries = detector.detect(str(pdf_with_font_sizes))

    # 应该找到大字体标题
    assert len(entries) >= 2

    # 检查层级
    level_1_entries = [e for e in entries if e.level == 1]
    assert len(level_1_entries) >= 2  # 第一章、第二章


def test_detector_base_font_size(detector, pdf_with_font_sizes):
    """Detector should correctly identify base font size."""
    entries = detector.detect(str(pdf_with_font_sizes))
    assert detector._base_font_size > 0
    # 正文字体 12pt，base_font_size 应该接近
    assert detector._base_font_size >= 10
    assert detector._base_font_size <= 14


def test_bookmark_entry_structure(detector, pdf_with_font_sizes):
    """Entries should have correct structure."""
    entries = detector.detect(str(pdf_with_font_sizes))

    for entry in entries:
        assert isinstance(entry, BookmarkEntry)
        assert entry.title
        assert entry.page >= 0
        assert entry.level in [1, 2]


def test_detector_no_empty_titles(detector, pdf_with_font_sizes):
    """Detector should not produce empty titles."""
    entries = detector.detect(str(pdf_with_font_sizes))

    for entry in entries:
        assert len(entry.title.strip()) >= 2