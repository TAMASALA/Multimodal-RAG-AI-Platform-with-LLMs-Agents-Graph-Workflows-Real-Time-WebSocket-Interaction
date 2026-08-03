"""
Extracts embedded raster images from PDF pages and renders full-page images
(used for tables/graphs that are hard to parse structurally).
"""
import os

import fitz  # PyMuPDF

from app.utils.helpers import new_id
from app.utils.logger import logger

MIN_IMAGE_DIM = 60  # ignore tiny icons/bullets


def extract_page_images(pdf_path: str, page_index: int, output_dir: str) -> list[str]:
    """Extracts embedded images from a single PDF page. Returns saved file paths."""
    saved_paths: list[str] = []
    try:
        doc = fitz.open(pdf_path)
        page = doc[page_index]
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            ext = base_image.get("ext", "png")
            width = base_image.get("width", 0)
            height = base_image.get("height", 0)

            if width < MIN_IMAGE_DIM or height < MIN_IMAGE_DIM:
                continue

            filename = f"{new_id()}_p{page_index}_{img_index}.{ext}"
            out_path = os.path.join(output_dir, filename)
            with open(out_path, "wb") as f:
                f.write(image_bytes)
            saved_paths.append(out_path)

        doc.close()
    except Exception as exc:
        logger.error(f"Image extraction failed on page {page_index} of {pdf_path}: {exc}")

    return saved_paths


def render_page_as_image(pdf_path: str, page_index: int, output_dir: str, dpi: int = 200) -> str:
    """Renders an entire page to a PNG (useful as fallback context for graphs/complex layouts)."""
    doc = fitz.open(pdf_path)
    page = doc[page_index]
    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=matrix)

    filename = f"{new_id()}_page_{page_index}_full.png"
    out_path = os.path.join(output_dir, filename)
    pix.save(out_path)
    doc.close()
    return out_path
