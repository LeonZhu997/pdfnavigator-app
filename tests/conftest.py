import pytest
from pathlib import Path

SAMPLES_DIR = Path(__file__).parent / "samples"


@pytest.fixture
def sample_pdf_with_toc():
    """Path to a sample PDF with table of contents."""
    return SAMPLES_DIR / "sample_with_toc.pdf"


@pytest.fixture
def sample_pdf_no_toc():
    """Path to a sample PDF without table of contents."""
    return SAMPLES_DIR / "sample_no_toc.pdf"