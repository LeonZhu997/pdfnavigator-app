# PDFNavigator

A GUI desktop application that automatically extracts bookmarks from PDF table of contents pages.

## Features

- Auto-detect table of contents pages
- Parse TOC entries with multi-level hierarchy support
- Preview and edit bookmarks before saving
- Generate new PDF with nested bookmarks

## Installation

```bash
pip install -e .
```

## Usage

```bash
python main.py
```

## Requirements

- Python 3.11+
- PySide6
- PyMuPDF
- pdfplumber