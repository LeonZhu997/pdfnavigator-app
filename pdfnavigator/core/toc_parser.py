"""Table of contents parsing and bookmark extraction."""

import fitz
import pdfplumber
import re
from dataclasses import dataclass
from typing import List, Dict
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

    # Threshold for detecting if a page is TOC continuation
    TOC_LINE_THRESHOLD = 0.3  # At least 30% of lines should have page numbers
    TOC_DOT_THRESHOLD = 30  # Pages with >30 dots are likely TOC pages

    def __init__(self):
        self.entries: List[BookmarkEntry] = []
        self._title_to_page: Dict[str, int] = {}  # Maps title keywords to PDF pages

    def parse(self, pdf_path: str, toc_page: int) -> List[BookmarkEntry]:
        """Parse TOC page and extract bookmarks.

        Uses title search to find actual content locations in PDF,
        rather than relying on TOC page numbers which may not match
        PDF physical pages due to conversion differences.

        Args:
            pdf_path: Path to the PDF file.
            toc_page: Starting page number of TOC (0-indexed).

        Returns:
            List of BookmarkEntry objects.
        """
        self.entries = []

        # First, build a mapping of title keywords to actual PDF pages
        # by searching for content after TOC pages
        self._build_title_location_map(pdf_path, toc_page)

        with pdfplumber.open(pdf_path) as pdf:
            current_page = toc_page

            # Parse the starting TOC page
            self._parse_single_page(pdf, current_page)

            # Check subsequent pages for TOC continuation
            while current_page + 1 < len(pdf.pages):
                next_page = current_page + 1
                if self._is_toc_continuation(pdf, next_page):
                    self._parse_single_page(pdf, next_page)
                    current_page = next_page
                else:
                    break  # Stop when we hit non-TOC content

        return self.entries

    def _build_title_location_map(self, pdf_path: str, toc_page: int) -> None:
        """Build mapping from title keywords to actual PDF page locations.

        Scans PDF pages after TOC to find where each major section
        actually appears in the PDF.
        """
        with pdfplumber.open(pdf_path) as pdf:
            # Find the first content page (skip TOC pages)
            content_start = self._find_content_start(pdf)

            # Scan content pages to build title-location mapping
            for page_idx in range(content_start, len(pdf.pages)):
                text = pdf.pages[page_idx].extract_text()
                if not text:
                    continue

                # Skip if this page still looks like TOC
                if text.count("...") > self.TOC_DOT_THRESHOLD:
                    continue

                # Skip "总说明" page which lists all chapters
                if "本招标文件由以下章节组成" in text or "上述章节和本总说明" in text:
                    continue

                # Check for chapter headings at start of page or section
                # Only record if it appears as the FIRST line (chapter start page)
                lines = text.strip().split('\n')

                # Check first line for chapter heading
                first_line = lines[0].strip() if lines else ''

                # Chapter headings: "第一章 xxx" or "第一章xxx" (may have no space)
                chapter_match = re.match(r'第[一二三四五六七八九十]+章[\s\u3000]*(.+)', first_line)
                if chapter_match:
                    chapter_num = re.search(r'第[一二三四五六七八九十]+章', first_line).group()
                    chapter_content = chapter_match.group(1).strip()
                    # Store both chapter number and full title
                    if chapter_num not in self._title_to_page:
                        self._title_to_page[chapter_num] = page_idx
                    if chapter_content and chapter_content not in self._title_to_page:
                        self._title_to_page[chapter_content] = page_idx

                # Section headings: "第一节 xxx" - check first few lines
                for i in range(min(5, len(lines))):
                    line = lines[i].strip()
                    section_match = re.match(r'第[一二三四五六七八九十]+节\s+(.+)', line)
                    if section_match:
                        section_num = re.search(r'第[一二三四五六七八九十]+节', line).group()
                        section_content = section_match.group(1).strip()
                        if section_num not in self._title_to_page:
                            self._title_to_page[section_num] = page_idx
                        break

                # Numbered sections - check first few lines
                for i in range(min(10, len(lines))):
                    line = lines[i].strip()

                    # Skip if line is too long (likely not a heading)
                    if len(line) > 50:
                        continue

                    # Numbered sections: "1.1 xxx", "2.3 xxx"
                    num_match = re.match(r'(\d+\.\d+)[\s\u3000]+(.+)', line)
                    if num_match:
                        num_key = num_match.group(1)
                        content = num_match.group(2).strip()
                        if num_key not in self._title_to_page:
                            self._title_to_page[num_key] = page_idx
                        continue

                    # Main numbered sections: "1. xxx"
                    main_match = re.match(r'(\d+\.)[\s\u3000]+(.+)', line)
                    if main_match and not num_match:
                        num_key = main_match.group(1)
                        content = main_match.group(2).strip()
                        if num_key not in self._title_to_page:
                            self._title_to_page[num_key] = page_idx
                        continue

                    # Chinese numbered: "一、xxx"
                    cn_match = re.match(r'([一二三四五六七八九十]+、)(.+)', line)
                    if cn_match:
                        cn_key = cn_match.group(1)
                        content = cn_match.group(2).strip()
                        if cn_key not in self._title_to_page:
                            self._title_to_page[cn_key] = page_idx

    def _find_content_start(self, pdf: pdfplumber.PDF) -> int:
        """Find the first page that contains actual content (not TOC)."""
        for page_idx in range(len(pdf.pages)):
            text = pdf.pages[page_idx].extract_text()
            if not text:
                continue

            # Skip TOC pages (high dot count)
            if text.count("...") > self.TOC_DOT_THRESHOLD:
                continue

            # Skip pages that list all chapters (like "总说明")
            if "本招标文件由以下章节组成" in text:
                continue

            return page_idx

        return 0  # Default to first page if no content found

    def _extract_footer_page_number(self, text: str) -> int | None:
        """Extract page number from footer (last lines of page)."""
        lines = text.strip().split('\n')
        for line in reversed(lines[-5:]):
            line = line.strip()
            if re.match(r'^\d+$', line):
                return int(line)
        return None

    def _parse_single_page(self, pdf: pdfplumber.PDF, page_num: int) -> None:
        """Parse a single TOC page and add entries."""
        page = pdf.pages[page_num]
        text = page.extract_text()

        if not text:
            return

        lines = text.strip().split('\n')

        # Track current chapter for sub-entries
        current_chapter_page = None
        last_entry_page = None

        for line in lines:
            line = line.strip()
            if not line or re.match(r'^\d+$', line):
                continue

            toc_page_num = extract_page_number(line)
            if toc_page_num is None:
                continue

            title = clean_title(line)
            level = infer_level_from_numbering(title)

            # Check if this is a chapter heading (level 1, has "第X章")
            is_chapter = bool(re.match(r'第[一二三四五六七八九十]+章', title))

            if is_chapter:
                # For chapter headings, use title search to find actual page
                actual_page = self._find_title_in_pdf(title)
                if actual_page == -1:
                    actual_page = self._find_content_start(pdf)
                current_chapter_page = actual_page
                last_entry_page = actual_page
            else:
                # For sub-entries, first try exact match
                actual_page = self._find_title_in_pdf(title)
                if actual_page == -1:
                    # If not found, use current chapter page as reference
                    # Sub-entries should be near their parent chapter
                    if current_chapter_page is not None:
                        # Try to find the title within chapter pages
                        actual_page = self._find_title_near_chapter(pdf, title, current_chapter_page)
                        if actual_page == -1:
                            # Default to chapter start page
                            actual_page = current_chapter_page
                    elif last_entry_page is not None:
                        # Use previous entry's page as fallback
                        actual_page = last_entry_page
                    else:
                        actual_page = self._find_content_start(pdf)
                last_entry_page = actual_page

            entry = BookmarkEntry(title=title, page=actual_page, level=level)
            self.entries.append(entry)

    def _find_title_near_chapter(self, pdf: pdfplumber.PDF, title: str, chapter_page: int) -> int:
        """Find title within a reasonable range from the chapter start page."""
        # Search within +/- 20 pages from chapter start
        search_range = 20

        # Extract key search terms from title
        # Remove numbering prefix like "1.", "1.1", etc.
        search_title = re.sub(r'^[\d\.]+\s*', '', title).strip()

        if len(search_title) < 2:
            return -1

        # Search pages around chapter start
        for page_offset in range(-2, search_range):
            page_idx = chapter_page + page_offset
            if page_idx < 0 or page_idx >= len(pdf.pages):
                continue

            text = pdf.pages[page_idx].extract_text()
            if not text:
                continue

            # Skip TOC pages
            if text.count("...") > self.TOC_DOT_THRESHOLD:
                continue

            # Check if title or search_title appears at start of lines
            lines = text.strip().split('\n')
            for i, line in enumerate(lines[:15]):
                line = line.strip()
                # Match the numbered pattern from title
                if title[:10] in line or search_title in line:
                    return page_idx

        return -1

    def _find_title_in_pdf(self, title: str) -> int:
        """Find the PDF page index where a title appears.

        Searches the pre-built title-location map and also
        looks for key title fragments.
        """
        # Clean title for matching
        clean_t = title.strip()

        # Try exact match first
        if clean_t in self._title_to_page:
            return self._title_to_page[clean_t]

        # For numbered titles like "1. 招标条件", "2. 项目概况"
        # Try to match the full numbered prefix + significant content
        num_match = re.match(r'(\d+\.\d+)[\s\u3000]+(.+)', clean_t)  # "1.1 xxx"
        if num_match:
            num_key = num_match.group(1)
            # Only use numbered key if it has enough precision (like "1.1")
            # Avoid using just "1." or "2." which are too generic
            if '.' in num_key and len(num_key) >= 3:  # "1.1", "2.3" etc.
                if num_key in self._title_to_page:
                    return self._title_to_page[num_key]

        # For main numbered titles like "1. xxx", "2. xxx"
        # Don't match just the number - too many duplicates
        # Instead, try to match significant content words
        main_match = re.match(r'(\d+\.)[\s\u3000]+(.+)', clean_t)
        if main_match:
            content = main_match.group(2).strip()
            # Try content word matching
            if content in self._title_to_page:
                return self._title_to_page[content]
            # Try significant words
            words = re.findall(r'\S+', content)
            for word in words:
                if len(word) > 3 and word in self._title_to_page:
                    return self._title_to_page[word]

        # Try matching chapter/section numbers (these are unique)
        patterns = [
            (r'第[一二三四五六七八九十]+章', 'chapter'),  # "第一章", "第二章"
            (r'第[一二三四五六七八九十]+节', 'section'),  # "第一节", "第二节"
            (r'[一二三四五六七八九十]+、', 'chinese_num'),  # "一、", "二、"
        ]

        for pattern, ptype in patterns:
            match = re.search(pattern, clean_t)
            if match:
                key = match.group().strip()
                if key in self._title_to_page:
                    return self._title_to_page[key]

        # Try removing chapter prefix and searching for content name
        content_match = re.search(r'第[一二三四五六七八九十]+[章节]\s+(.+)', clean_t)
        if content_match:
            content_name = content_match.group(1).strip()
            if content_name in self._title_to_page:
                return self._title_to_page[content_name]

        return -1  # Not found

    def _is_toc_continuation(self, pdf: pdfplumber.PDF, page_num: int) -> bool:
        """Check if a page is likely a TOC continuation.

        A page is considered TOC continuation if:
        1. It has high dot density (typical of TOC formatting)
        2. A significant portion of lines have trailing page numbers
        """
        page = pdf.pages[page_num]
        text = page.extract_text()

        if not text:
            return False

        # Check for high dot count (typical TOC formatting)
        if text.count("...") > self.TOC_DOT_THRESHOLD:
            return True

        lines = text.strip().split('\n')
        if len(lines) < 3:
            return False

        # Count lines that look like TOC entries (end with page number)
        toc_like_lines = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if extract_page_number(line) is not None:
                toc_like_lines += 1

        ratio = toc_like_lines / len(lines)
        return ratio >= self.TOC_LINE_THRESHOLD