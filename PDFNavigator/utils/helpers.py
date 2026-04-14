"""Helper functions for PDFNavigator."""

import re


def extract_page_number(text: str) -> int | None:
    """Extract page number from a TOC line."""
    patterns = [
        r"\s+(\d+)$",
        r"\.\s*(\d+)$",
        r"[\.\s]+(\d+)$",
    ]
    for pattern in patterns:
        match = re.search(pattern, text.strip())
        if match:
            return int(match.group(1))
    return None


def infer_level_from_numbering(text: str, default: int = 1) -> int:
    """Infer bookmark level from numbering pattern."""
    patterns = [
        (r"^(\d+)\.(\d+)\.(\d+)", 3),
        (r"^(\d+)\.(\d+)", 2),
        (r"^(\d+)\.", 1),
        (r"^Chapter\s*(\d+)", 1),
    ]
    for pattern, level in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return level
    return default


def clean_title(text: str) -> str:
    """Clean TOC title by removing page numbers and dots."""
    cleaned = re.sub(r"[\.\s]+\d+$", "", text.strip())
    cleaned = re.sub(r"\s+\d+$", "", cleaned)
    return cleaned.strip()