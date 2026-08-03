"""
Retrieves the most relevant chunks for a query by combining FAISS similarity
search with a DB lookup to hydrate full chunk content/metadata.
"""
import re
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.crud import get_chunks_by_faiss_indices, get_chunks_for_document
from app.database.models import Chunk
from app.embeddings.embedding_service import embed_query
from app.embeddings.faiss_store import get_faiss_store
from app.utils.logger import logger


@dataclass
class RetrievedChunk:
    chunk: Chunk
    score: float


async def retrieve(
    db: AsyncSession,
    query: str,
    top_k: int | None = None,
    document_ids: list[str] | None = None,
    score_threshold: float | None = None,
) -> list[RetrievedChunk]:
    """Runs semantic search over the FAISS index and hydrates results with
    full chunk rows from the database. It also adds a keyword-based fallback
    for project/resume-style questions when semantic similarity is too weak."""
    top_k = top_k or settings.TOP_K
    score_threshold = score_threshold if score_threshold is not None else settings.SCORE_THRESHOLD

    store = get_faiss_store()
    if store.ntotal == 0:
        logger.warning("Retrieval requested but FAISS index is empty.")
        return []

    query_vector = embed_query(query)
    fetch_k = (top_k * 8) if document_ids else (top_k * 8)
    scores, indices = store.search(query_vector, fetch_k)

    flat_indices = [int(i) for i in indices[0] if i != -1]
    flat_scores = {int(i): float(s) for i, s in zip(indices[0], scores[0]) if i != -1}

    if not flat_indices:
        return []

    chunks = await get_chunks_by_faiss_indices(db, flat_indices)

    results: list[RetrievedChunk] = []
    for chunk in chunks:
        score = flat_scores.get(chunk.faiss_index, 0.0)
        if document_ids and chunk.document_id not in document_ids:
            continue
        text = (chunk.content or "").lower()
        query_terms = re.findall(r"[a-z0-9]+", query.lower())
        keyword_hits = sum(1 for term in query_terms if term and term in text)
        boosted_score = score + (0.03 * keyword_hits)
        if boosted_score < score_threshold:
            continue
        results.append(RetrievedChunk(chunk=chunk, score=boosted_score))

    results.sort(key=lambda r: r.score, reverse=True)
    results = results[: top_k * 2]

    if len(results) < top_k:
        fallback_terms = [term for term in re.findall(r"[a-z0-9]+", query.lower()) if len(term) > 2]
        if fallback_terms:
            keyword_matches: list[Chunk] = []
            for chunk in await get_chunks_for_document(db, document_ids[0]) if document_ids and len(document_ids) == 1 else []:
                text = (chunk.content or "").lower()
                match_count = sum(1 for term in fallback_terms if term in text)
                if match_count:
                    keyword_matches.append(chunk)
            if keyword_matches:
                keyword_matches = sorted(keyword_matches, key=lambda c: len(c.content), reverse=True)
                for chunk in keyword_matches[:top_k]:
                    results.append(RetrievedChunk(chunk=chunk, score=0.2))

    results.sort(key=lambda r: r.score, reverse=True)
    return results[:top_k]

   
