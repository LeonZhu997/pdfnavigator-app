"""Font-based chapter detection for PDFs without TOC pages."""

import fitz
from typing import List, Dict
from collections import Counter

from PDFNavigator.core.toc_parser import BookmarkEntry


class FontChapterDetector:
    """Detects chapter titles based on font size."""

    # 字体大小阈值（相对于基准字体）
    CHAPTER_THRESHOLD = 4.0  # 章节标题：基准 + 4pt
    SECTION_THRESHOLD = 2.0  # 小节标题：基准 + 2pt

    def __init__(self):
        self.entries: List[BookmarkEntry] = []
        self._base_font_size: float = 0

    def detect(self, pdf_path: str) -> List[BookmarkEntry]:
        """Detect chapters based on font size throughout the PDF.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            List of BookmarkEntry objects.
        """
        self.entries = []
        doc = fitz.open(pdf_path)

        # 1. 收集所有字体大小，确定基准字体
        self._base_font_size = self._find_base_font_size(doc)

        if self._base_font_size == 0:
            doc.close()
            return self.entries

        # 2. 遍历每页检测章节标题
        for page_num in range(doc.page_count):
            page = doc[page_num]
            self._detect_on_page(page, page_num)

        doc.close()

        # 3. 合理排序和去重
        self._deduplicate_entries()

        return self.entries

    def _find_base_font_size(self, doc: fitz.Document) -> float:
        """Find the base (body text) font size.

        The base font size is typically the most common small font.
        """
        font_sizes: List[float] = []

        # 扫描前 10 页收集字体大小样本
        sample_pages = min(10, doc.page_count)
        for page_num in range(sample_pages):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]

            for block in blocks:
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    for span in line.get("spans", []):
                        size = span.get("size", 0)
                        if size > 0:
                            font_sizes.append(size)

        if not font_sizes:
            return 0

        # 统计字体大小频率，选择最小常见字体作为基准
        # 过滤掉小于 6pt 的异常值（可能是页码、注释等）
        valid_sizes = [s for s in font_sizes if s >= 6]
        if not valid_sizes:
            return min(font_sizes) if font_sizes else 0

        # 找到最常见的字体大小
        size_counts = Counter(valid_sizes)
        most_common_sizes = size_counts.most_common(5)

        # 从最常见的小字体中选择基准
        # 假设正文是出现频率高且较小的字体
        base_candidates = [s for s, c in most_common_sizes if s <= 15]
        if base_candidates:
            return min(base_candidates)

        return most_common_sizes[0][0]

    def _detect_on_page(self, page: fitz.Page, page_num: int) -> None:
        """Detect chapter titles on a single page."""
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" not in block:
                continue

            # 检查块是否在页面顶部区域（通常标题在顶部）
            block_y0 = block.get("bbox", (0, 0, 0, 0))[1]
            page_height = page.rect.height

            # 只检测上半部分的文本块（标题通常在页面上半部分）
            if block_y0 > page_height * 0.7:
                continue

            for line in block["lines"]:
                self._check_line_for_title(line, page_num)

    def _check_line_for_title(self, line: Dict, page_num: int) -> None:
        """Check if a line is a potential chapter title."""
        spans = line.get("spans", [])
        if not spans:
            return

        # 取该行的最大字体大小
        max_size = max(span.get("size", 0) for span in spans)

        # 判断层级
        if max_size >= self._base_font_size + self.CHAPTER_THRESHOLD:
            level = 1  # 章
        elif max_size >= self._base_font_size + self.SECTION_THRESHOLD:
            level = 2  # 节
        else:
            return  # 正文跳过

        # 提取标题文本
        title = self._extract_title(spans)
        if not title or len(title) < 2:
            return

        # 过滤常见的非标题文本
        if self._is_non_title(title):
            return

        self.entries.append(BookmarkEntry(title=title, page=page_num, level=level))

    def _extract_title(self, spans: List[Dict]) -> str:
        """Extract title text from spans."""
        texts = []
        for span in spans:
            text = span.get("text", "").strip()
            if text:
                texts.append(text)
        return " ".join(texts).strip()

    def _is_non_title(self, title: str) -> bool:
        """Check if text is likely not a title."""
        # 过滤页码、日期等
        non_title_patterns = [
            r"^\d+$",  # 纯数字（页码）
            r"^\d+\s*[-/]\s*\d+",  # 日期格式
            r"^Page\s*\d+",  # Page X
            r"^[IVXLC]+\.?$",  # 简单罗马数字
            r"^www\.",  # 网址
            r"^@",  # 邮箱/社交媒体
        ]

        import re
        for pattern in non_title_patterns:
            if re.match(pattern, title, re.IGNORECASE):
                return True

        # 过滤过短的文本
        if len(title) < 3:
            return True

        return False

    def _deduplicate_entries(self) -> None:
        """Remove duplicate entries and sort by page."""
        # 按页码排序
        self.entries.sort(key=lambda e: (e.page, e.level))

        # 去重：同一页的相同标题只保留一个
        seen = set()
        unique_entries = []
        for entry in self.entries:
            key = (entry.page, entry.title)
            if key not in seen:
                seen.add(key)
                unique_entries.append(entry)

        self.entries = unique_entries