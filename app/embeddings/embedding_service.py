"""
Wraps a sentence-transformers model as a singleton to avoid reloading weights
on every request. Provides sync encode used by both ingestion and retrieval.
"""
from threading import Lock
from typing import Optional

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.utils.logger import logger

_model: Optional[SentenceTransformer] = None
_lock = Lock()


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                logger.info(f"Loading embedding model '{settings.EMBEDDING_MODEL_NAME}'...")
                _model = SentenceTransformer(
                    settings.EMBEDDING_MODEL_NAME, device=settings.EMBEDDING_DEVICE
                )
                logger.info("Embedding model loaded.")
    return _model


def embed_texts(texts: list[str]) -> np.ndarray:
    """Encodes a list of texts into L2-normalized float32 embeddings (cosine-ready)."""
    if not texts:
        return np.empty((0, settings.EMBEDDING_DIM), dtype="float32")

    model = get_model()
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=False,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    return embeddings.astype("float32")


def embed_query(query: str) -> np.ndarray:
    """Encodes a single query string. Returns shape (1, dim)."""
    return embed_texts([query])
