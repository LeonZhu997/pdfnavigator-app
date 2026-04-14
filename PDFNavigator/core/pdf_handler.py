"""PDF file operations wrapper."""

import fitz
from pathlib import Path
from typing import Optional


class PDFHandler:
    """Wrapper for PDF file operations."""

    def __init__(self):
        self._doc: Optional[fitz.Document] = None
        self._path: Optional[Path] = None

    def open(self, path: str | Path) -> None:
        """Open a PDF file."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {path}")
        self._doc = fitz.open(str(path))
        self._path = path

    def close(self) -> None:
        """Close the current PDF."""
        if self._doc is not None:
            self._doc.close()
            self._doc = None
            self._path = None

    @property
    def is_open(self) -> bool:
        return self._doc is not None

    @property
    def page_count(self) -> int:
        if self._doc is None:
            return 0
        return self._doc.page_count

    def get_page_text(self, page_num: int) -> str:
        if self._doc is None:
            raise RuntimeError("No PDF is open")
        return self._doc[page_num].get_text()

    def is_encrypted(self) -> bool:
        if self._doc is None:
            return False
        return self._doc.is_encrypted