"""
Unit tests for individual agents, mocking the underlying Groq client so no
real network/API calls are made.
"""
from unittest.mock import AsyncMock, patch

import pytest

from app.agents.fallback import fallback_answer
from app.agents.multimodal_agent import is_multimodal_request
from app.agents.summarization_agent import is_summarization_request, summarize_content
from app.agents.translation_agent import translate_text
from app.database.models import Chunk, ChunkType
from app.llm.prompts import FALLBACK_PROMPT
from app.rag.retriever import RetrievedChunk


def _make_chunk(chunk_type: str, image_path: str | None = None) -> Chunk:
    return Chunk(
        id="c1",
        document_id="d1",
        chunk_type=chunk_type,
        content="sample content",
        page_number=1,
        image_path=image_path,
        faiss_index=0,
        meta={"document_name": "doc.pdf"},
    )


def test_is_summarization_request_detects_trigger_words():
    assert is_summarization_request("Can you summarize this document?")
    assert is_summarization_request("give me a tl;dr")
    assert not is_summarization_request("what is the revenue in Q3?")


def test_is_multimodal_request_requires_visual_keyword_and_image_chunk():
    image_chunk = RetrievedChunk(chunk=_make_chunk(ChunkType.GRAPH.value, "img.png"), score=0.9)
    text_chunk = RetrievedChunk(chunk=_make_chunk(ChunkType.TEXT.value), score=0.9)

    assert is_multimodal_request("what does the chart show?", [image_chunk])
    assert not is_multimodal_request("what does the chart show?", [text_chunk])
    assert not is_multimodal_request("what is the total revenue?", [image_chunk])


@pytest.mark.asyncio
async def test_translate_text_calls_llm_and_returns_result():
    with patch(
        "app.agents.translation_agent.chat_completion", new=AsyncMock(return_value="hola mundo")
    ):
        result = await translate_text("hello world", "Spanish")
        assert result == "hola mundo"


@pytest.mark.asyncio
async def test_translate_text_falls_back_to_original_on_error():
    with patch(
        "app.agents.translation_agent.chat_completion",
        new=AsyncMock(side_effect=RuntimeError("boom")),
    ):
        result = await translate_text("hello world", "Spanish")
        assert result == "hello world"


@pytest.mark.asyncio
async def test_summarize_content_empty_input_returns_message():
    result = await summarize_content("   ")
    assert "no content" in result.lower()


def test_fallback_prompt_instructs_model_to_stay_grounded():
    assert "Do not claim that you have information about the user's project" in FALLBACK_PROMPT
    assert "unless it is explicitly supported by the provided context" in FALLBACK_PROMPT


@pytest.mark.asyncio
async def test_fallback_answer_calls_llm():
    with patch(
        "app.agents.fallback.chat_completion",
        new=AsyncMock(return_value="No relevant info found."),
    ):
        result = await fallback_answer("random unrelated question")
        assert result == "No relevant info found."
