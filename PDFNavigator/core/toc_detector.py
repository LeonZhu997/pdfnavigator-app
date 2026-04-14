"""Table of contents page detection."""

import fitz
import re
from typing import Optional, List
from PDFNavigator.utils.config import TOC_KEYWORDS, MAX_SCAN_PAGES


class TOCDetector:
    """Detects table of contents pages in PDFs."""

    def __init__(self, keywords: Optional[List[str]] = None, max_pages: int = MAX_SCAN_PAGES):
        self.keywords = keywords or TOC_KEYWORDS
        self.max_pages = max_pages

    def detect(self, pdf_path: str) -> Optional[int]:
        """Detect the TOC page in a PDF."""
        doc = fitz.open(pdf_path)
        candidates = []
        pages_to_scan = min(self.max_pages, doc.page_count)

        for page_num in range(pages_to_scan):
            text = doc[page_num].get_text()
            confidence = self._check_keyword_presence(text)
            if confidence > 0:
                structure_score = self._check_toc_structure(text)
                total_score = confidence + structure_score
                candidates.append((page_num, total_score))

        doc.close()

        if not candidates:
            return None

        best = max(candidates, key=lambda x: x[1])
        return best[0] if best[1] >= 1 else None

    def _check_keyword_presence(self, text: str) -> float:
        text_lower = text.lower().strip()
        for keyword in self.keywords:
            if keyword.lower() in text_lower:
                return 1.0
        return 0.0

    def _check_toc_structure(self, text: str) -> float:
        lines = text.strip().split('\n')
        lines_with_numbers = 0
        for line in lines:
            if re.search(r'\s+\d+$', line.strip()) or re.search(r'\.\s*\d+$', line.strip()):
                lines_with_numbers += 1
        if len(lines) < 3:
            return 0.0
        ratio = lines_with_numbers / len(lines)
        return ratio if ratio > 0.3 else 0.0