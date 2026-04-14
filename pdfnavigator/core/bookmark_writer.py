"""Bookmark writing to PDF files."""

import fitz
from pathlib import Path
from typing import List
from pdfnavigator.core.toc_parser import BookmarkEntry


class BookmarkWriter:
    """Writes bookmarks to PDF files."""

    def write(self, input_path: str, entries: List[BookmarkEntry], output_path: str) -> None:
        """Write bookmarks to a new PDF file."""
        doc = fitz.open(input_path)
        toc_items = []
        for entry in entries:
            toc_item = (entry.level, entry.title, entry.page + 1)
            toc_items.append(toc_item)
        doc.set_toc(toc_items)
        doc.save(output_path)
        doc.close()