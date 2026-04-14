import pytest
from PDFNavigator.utils.helpers import extract_page_number, infer_level_from_numbering


def test_extract_page_number_simple():
    """Extract page number from simple TOC line."""
    text = "Introduction 5"
    result = extract_page_number(text)
    assert result == 5


def test_extract_page_number_with_dots():
    """Extract page number from dotted TOC line."""
    text = "Chapter 1 .... 10"
    result = extract_page_number(text)
    assert result == 10


def test_extract_page_number_no_match():
    """Return None when no page number found."""
    text = "Some title without number"
    result = extract_page_number(text)
    assert result is None


def test_infer_level_from_numbering_single():
    """Single digit numbering is level 1."""
    assert infer_level_from_numbering("1.") == 1
    assert infer_level_from_numbering("2.") == 1


def test_infer_level_from_numbering_double():
    """Double digit numbering is level 2."""
    assert infer_level_from_numbering("1.1") == 2
    assert infer_level_from_numbering("2.3") == 2


def test_infer_level_from_numbering_triple():
    """Triple digit numbering is level 3."""
    assert infer_level_from_numbering("1.1.1") == 3
    assert infer_level_from_numbering("2.3.4") == 3


def test_infer_level_from_numbering_none():
    """No numbering pattern returns default level."""
    assert infer_level_from_numbering("Introduction") == 1