"""
OCR extraction for images embedded in or rendered from PDF pages.
"""
import pytesseract
from PIL import Image

from app.config import settings
from app.utils.helpers import clean_text
from app.utils.logger import logger

pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD


def extract_text_from_image(image_path: str, lang: str = "eng") -> str:
    """Runs Tesseract OCR on an image file and returns cleaned text."""
    try:
        image = Image.open(image_path)
        if image.mode != "RGB":
            image = image.convert("RGB")
        raw_text = pytesseract.image_to_string(image, lang=lang)
        return clean_text(raw_text)
    except Exception as exc:
        logger.error(f"OCR failed for {image_path}: {exc}")
        return ""


def has_meaningful_text(text: str, min_chars: int = 8) -> bool:
    """Heuristic: decides whether OCR output is worth keeping as a chunk."""
    return len(text.strip()) >= min_chars
