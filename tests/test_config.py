import pytest
from pdfnavigator.utils.config import TOC_KEYWORDS, MAX_SCAN_PAGES


def test_toc_keywords_contains_chinese():
    """Config should include Chinese TOC keywords."""
    assert "目录" in TOC_KEYWORDS
    assert "目 录" in TOC_KEYWORDS


def test_toc_keywords_contains_english():
    """Config should include English TOC keywords."""
    assert "Contents" in TOC_KEYWORDS
    assert "CONTENTS" in TOC_KEYWORDS
    assert "Table of Contents" in TOC_KEYWORDS


def test_max_scan_pages_is_reasonable():
    """Max scan pages should be between 5 and 50."""
    assert 5 <= MAX_SCAN_PAGES <= 50