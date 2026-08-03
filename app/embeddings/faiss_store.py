"""
Persistent FAISS vector store. Uses IndexFlatIP (inner product) over
L2-normalized embeddings, which is equivalent to cosine similarity.

The store is a process-wide singleton so ingestion (writes) and retrieval
(reads) share the same in-memory index, periodically flushed to disk.
"""
import os
import threading

import faiss
import numpy as np

from app.config import settings
from app.utils.logger import logger

_index_lock = threading.Lock()


class FaissStore:
    def __init__(self, dim: int, index_path: str):
        self.dim = dim
        self.index_path = index_path
        self.index: faiss.Index = self._load_or_create()

    def _load_or_create(self) -> faiss.Index:
        if os.path.exists(self.index_path):
            logger.info(f"Loading existing FAISS index from {self.index_path}")
            return faiss.read_index(self.index_path)
        logger.info(f"Creating new FAISS index (dim={self.dim}) at {self.index_path}")
        return faiss.IndexFlatIP(self.dim)

    @property
    def ntotal(self) -> int:
        return self.index.ntotal

    def add(self, vectors: np.ndarray) -> tuple[int, int]:
        """Adds vectors to the index. Returns (start_index, end_index) of the
        newly assigned positions, which callers persist alongside chunk rows."""
        if vectors.shape[0] == 0:
            start = self.index.ntotal
            return start, start

        with _index_lock:
            start = self.index.ntotal
            self.index.add(vectors)
            end = self.index.ntotal
        return start, end

    def search(self, query_vector: np.ndarray, top_k: int) -> tuple[np.ndarray, np.ndarray]:
        """Returns (scores, indices) for the top_k nearest neighbors."""
        if self.index.ntotal == 0:
            return np.empty((1, 0)), np.empty((1, 0), dtype="int64")
        with _index_lock:
            scores, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))
        return scores, indices

    def save(self) -> None:
        with _index_lock:
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            faiss.write_index(self.index, self.index_path)
        logger.debug(f"FAISS index saved to {self.index_path} ({self.ntotal} vectors)")


_store: FaissStore | None = None
_store_lock = threading.Lock()


def get_faiss_store() -> FaissStore:
    global _store
    if _store is None:
        with _store_lock:
            if _store is None:
                index_path = os.path.join(settings.FAISS_INDEX_DIR, settings.FAISS_INDEX_NAME)
                _store = FaissStore(dim=settings.EMBEDDING_DIM, index_path=index_path)
    return _store
