"""
Tests for the RAG pipeline orchestration logic (routing between fallback,
multimodal, summarization, and default RAG generation), with retrieval and
LLM calls mocked so tests run offline and deterministically.
"""
from unittest.mock import AsyncMock, patch

import pytest

from app.database.models import Chunk, ChunkType
from app.ingestion.chunking import split_text
from app.rag.pipeline import run_rag_pipeline
from app.rag.retriever import RetrievedChunk


def _make_retrieved(chunk_type: str = ChunkType.TEXT.value, score: float = 0.8) -> RetrievedChunk:
    chunk = Chunk(
        id="c1",
        document_id="d1",
        chunk_type=chunk_type,
        content="The quarterly revenue was $5M.",
        page_number=2,
        faiss_index=0,
        meta={"document_name": "report.pdf"},
    )
    return RetrievedChunk(chunk=chunk, score=score)


@pytest.mark.asyncio
async def test_pipeline_uses_fallback_when_no_chunks_retrieved():
    with patch("app.rag.pipeline.retrieve", new=AsyncMock(return_value=[])), patch(
        "app.rag.pipeline.fallback_answer", new=AsyncMock(return_value="no info found")
    ):
        result = await run_rag_pipeline(db=None, query="unrelated question")
        assert result.agent_used == "fallback"
        assert result.sources == []
        assert result.answer == "no info found"


@pytest.mark.asyncio
async def test_pipeline_uses_summarization_agent_on_trigger_words():
    retrieved = [_make_retrieved()]
    with patch("app.rag.pipeline.retrieve", new=AsyncMock(return_value=retrieved)), patch(
        "app.rag.pipeline.summarize_content", new=AsyncMock(return_value="Summary text.")
    ):
        result = await run_rag_pipeline(db=None, query="please summarize this report")
        assert result.agent_used == "summarization"
        assert result.answer == "Summary text."
        assert len(result.sources) == 1


@pytest.mark.asyncio
async def test_pipeline_default_rag_path_generates_answer():
    retrieved = [_make_retrieved()]
    with patch("app.rag.pipeline.retrieve", new=AsyncMock(return_value=retrieved)), patch(
        "app.rag.pipeline.generate_answer", new=AsyncMock(return_value="The revenue was $5M [Source 1].")
    ):
        result = await run_rag_pipeline(db=None, query="what was the revenue?")
        assert result.agent_used == "rag"
        assert "5M" in result.answer


@pytest.mark.asyncio
async def test_pipeline_translates_final_answer_when_target_language_set():
    retrieved = [_make_retrieved()]
    with patch("app.rag.pipeline.retrieve", new=AsyncMock(return_value=retrieved)), patch(
        "app.rag.pipeline.generate_answer", new=AsyncMock(return_value="The revenue was $5M.")
    ), patch(
        "app.rag.pipeline.translate_text", new=AsyncMock(return_value="Los ingresos fueron $5M.")
    ):
        result = await run_rag_pipeline(db=None, query="what was the revenue?", target_language="Spanish")
        assert result.agent_used == "translation"
        assert result.answer == "Los ingresos fueron $5M."


def test_split_text_respects_chunk_size_and_overlap():
    text = "Sentence one. Sentence two. Sentence three. " * 20
    chunks = split_text(text, chunk_size=100, chunk_overlap=20)
    assert len(chunks) > 1
    assert all(len(c) <= 140 for c in chunks)  # allow slack for overlap+sentence boundaries
