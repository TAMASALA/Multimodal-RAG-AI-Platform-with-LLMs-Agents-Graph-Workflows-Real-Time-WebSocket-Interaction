"""
Core PDF parsing: extracts per-page plain text and page count using PyMuPDF.
Image/table/graph/equation extraction is delegated to the `processing` package
and orchestrated by `ingestion.pipeline`.
"""
from dataclasses import dataclass, field

import fitz  # PyMuPDF

from app.utils.helpers import clean_text
from app.utils.logger import logger


@dataclass
class PageContent:
    page_number: int
    text: str
    image_paths: list[str] = field(default_factory=list)


def get_page_count(pdf_path: str) -> int:
    doc = fitz.open(pdf_path)
    count = doc.page_count
    doc.close()
    return count


def extract_page_text(pdf_path: str, page_index: int) -> str:
    """Extracts plain text from a single page."""
    doc = fitz.open(pdf_path)
    try:
        page = doc[page_index]
        text = page.get_text("text")
        return clean_text(text)
    finally:
        doc.close()


def iter_pages(pdf_path: str):
    """Generator yielding (page_index, raw_text) for every page in the PDF."""
    doc = fitz.open(pdf_path)
    try:
        for i in range(doc.page_count):
            page = doc[i]
            yield i, clean_text(page.get_text("text"))
    finally:
        doc.close()


def is_page_text_sparse(text: str, min_words: int = 15) -> bool:
    """Detects pages with little/no extractable text — likely scanned images
    requiring OCR fallback."""
    return len(text.split()) < min_words
