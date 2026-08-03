"""
Table extraction using pdfplumber, serialized into markdown-like text so it can
be embedded and retrieved like any other text chunk while preserving structure.
"""
import pdfplumber

from app.utils.helpers import clean_text
from app.utils.logger import logger


def _rows_to_markdown(rows: list[list[str | None]]) -> str:
    if not rows:
        return ""
    cleaned_rows = [[(cell or "").strip() for cell in row] for row in rows]
    header, *body = cleaned_rows

    lines = ["| " + " | ".join(header) + " |"]
    lines.append("| " + " | ".join(["---"] * len(header)) + " |")
    for row in body:
        # pad/truncate row to header length for consistent markdown
        row = (row + [""] * len(header))[: len(header)]
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def extract_tables_from_page(pdf_path: str, page_index: int) -> list[str]:
    """Returns a list of markdown-formatted table strings found on the page."""
    tables_md: list[str] = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if page_index >= len(pdf.pages):
                return []
            page = pdf.pages[page_index]
            tables = page.extract_tables()

            for table in tables:
                if not table or len(table) < 2:  # need header + at least one row
                    continue
                md = _rows_to_markdown(table)
                if md:
                    tables_md.append(clean_text(md))
    except Exception as exc:
        logger.error(f"Table extraction failed on page {page_index} of {pdf_path}: {exc}")

    return tables_md
