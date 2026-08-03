"""
Builds structured metadata dicts attached to each chunk for filtering,
citation display, and debugging.
"""
from typing import Any


def build_chunk_metadata(
    document_id: str,
    document_name: str,
    page_number: int,
    chunk_type: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    meta = {
        "document_id": document_id,
        "document_name": document_name,
        "page_number": page_number,
        "chunk_type": chunk_type,
    }
    if extra:
        meta.update(extra)
    return meta
