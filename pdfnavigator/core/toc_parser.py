"""Table of contents parsing and bookmark extraction."""

import fitz
import pdfplumber
import re
from dataclasses import dataclass
from typing import List
from pdfnavigator.utils.helpers import extract_page_number, infer_level_from_numbering, clean_title


@dataclass
class BookmarkEntry:
    """Represents a single bookmark entry."""
    title: str
    page: int  # 0-indexed
    level: int  # 1-4

    def to_toc_item(self) -> tuple:
        return (self.level, self.title, self.page + 1)


class TOCParser:
    """Parses table of contents pages."""

    def __init__(self):
        self.entries: List[BookmarkEntry] = []

    def parse(self, pdf_path: str, toc_page: int) -> List[BookmarkEntry]:
        """Parse TOC page and extract bookmarks."""
        self.entries = []

        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[toc_page]
            text = page.extract_text()

            if not text:
                return self.entries

            lines = text.strip().split('\n')

            for line in lines:
                line = line.strip()
                if not line or re.match(r'^\d+$', line):
                    continue

                page_num = extract_page_number(line)
                if page_num is None:
                    continue

                title = clean_title(line)
                level = infer_level_from_numbering(title)

                entry = BookmarkEntry(title=title, page=page_num - 1, level=level)
                self.entries.append(entry)

        return self.entries