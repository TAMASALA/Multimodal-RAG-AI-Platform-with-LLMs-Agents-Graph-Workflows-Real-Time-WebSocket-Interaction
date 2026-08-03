"""
Miscellaneous small helpers shared across modules.
"""
import re
import time
import uuid
from contextlib import contextmanager
from typing import Generator

from app.utils.logger import logger


def new_id() -> str:
    return uuid.uuid4().hex


def clean_text(text: str) -> str:
    """Normalize whitespace and strip control characters from extracted text."""
    if not text:
        return ""
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def truncate(text: str, max_chars: int = 400) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "..."


@contextmanager
def timed(label: str) -> Generator[None, None, None]:
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        logger.debug(f"[timing] {label} took {elapsed:.3f}s")


def chunked_iterable(iterable, size: int):
    """Yield successive chunks of `size` from an iterable/list."""
    for i in range(0, len(iterable), size):
        yield iterable[i : i + size]
