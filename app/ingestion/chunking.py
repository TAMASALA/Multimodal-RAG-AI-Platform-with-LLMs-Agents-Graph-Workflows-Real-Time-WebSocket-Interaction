"""
Splits page-level text into overlapping chunks suitable for embedding.
Uses a simple, dependency-free recursive character splitter that tries to
break on paragraph/sentence boundaries before falling back to hard splits.
"""
import re

from app.config import settings

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def split_text(
    text: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[str]:
    """Splits `text` into chunks of ~chunk_size characters with chunk_overlap
    characters of overlap between consecutive chunks. Prefers to break on
    sentence boundaries."""
    chunk_size = chunk_size or settings.CHUNK_SIZE
    chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    if not text or not text.strip():
        return []

    sentences = _SENTENCE_SPLIT.split(text.strip())
    chunks: list[str] = []
    current = ""

    for sentence in sentences:
        candidate = f"{current} {sentence}".strip() if current else sentence

        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(current)
            # start next chunk with overlap from the tail of the previous chunk
            overlap_text = current[-chunk_overlap:] if chunk_overlap else ""
            current = f"{overlap_text} {sentence}".strip()
        else:
            # single sentence longer than chunk_size: hard split
            for i in range(0, len(sentence), chunk_size - chunk_overlap):
                chunks.append(sentence[i : i + chunk_size])
            current = ""

    if current:
        chunks.append(current)

    return [c for c in chunks if c.strip()]
