"""Configuration constants for PDFNavigator."""

# Keywords to identify table of contents pages
TOC_KEYWORDS = [
    "目录",
    "目 录",
    "目　录",
    "Contents",
    "CONTENTS",
    "Table of Contents",
    "TABLE OF CONTENTS",
    "目次",
]

# Maximum pages to scan for TOC detection
MAX_SCAN_PAGES = 20

# Minimum confidence threshold for TOC detection
MIN_TOC_CONFIDENCE = 0.5