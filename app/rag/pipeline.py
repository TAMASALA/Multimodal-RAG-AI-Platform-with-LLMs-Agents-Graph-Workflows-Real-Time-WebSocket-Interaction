"""
Top-level RAG orchestration: retrieves context, decides which specialized
agent (if any) should handle the request, and returns a structured answer
with source citations. This is the single entry point used by both the
REST chat endpoint and the websocket endpoint.
"""
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.fallback import fallback_answer
from app.agents.multimodal_agent import is_multimodal_request, answer_from_image
from app.agents.summarization_agent import is_summarization_request, summarize_content
from app.agents.translation_agent import translate_text
from app.database.models import ChatMessage
from app.rag.generator import generate_answer, generate_answer_stream
from app.rag.prompt_builder import build_rag_prompt
from app.rag.retriever import retrieve, RetrievedChunk
from app.schemas.chat import SourceRef
from app.utils.file_utils import to_image_url
from app.utils.helpers import truncate
from app.utils.logger import logger


@dataclass
class RagResult:
    answer: str
    sources: list[SourceRef] = field(default_factory=list)
    agent_used: str = "rag"


def _to_source_refs(retrieved: list[RetrievedChunk]) -> list[SourceRef]:
    return [
        SourceRef(
            chunk_id=r.chunk.id,
            document_id=r.chunk.document_id,
            document_name=r.chunk.meta.get("document_name", "unknown"),
            page_number=r.chunk.page_number,
            chunk_type=r.chunk.chunk_type,
            snippet=truncate(r.chunk.content, 300),
            score=round(r.score, 4),
            image_url=to_image_url(r.chunk.image_path),
        )
        for r in retrieved
    ]


async def run_rag_pipeline(
    db: AsyncSession,
    query: str,
    document_ids: list[str] | None = None,
    target_language: str | None = None,
    conversation_history: list[ChatMessage] | None = None,
) -> RagResult:
    """Runs the full pipeline: retrieve -> route to agent -> (optional) translate.
    `conversation_history` (prior turns in the session, oldest-first) is used
    only by the default RAG path to resolve references across turns; it is
    intentionally NOT passed to the fallback/multimodal/summarization agents
    since it could bias them away from being purely context/image-grounded."""
    retrieved = await retrieve(db, query, document_ids=document_ids)
    sources = _to_source_refs(retrieved)

    if not retrieved:
        logger.info(f"No relevant chunks found for query: {truncate(query, 80)!r}")
        answer = await fallback_answer(query)
        result = RagResult(answer=answer, sources=[], agent_used="fallback")

    elif is_multimodal_request(query, retrieved):
        answer = await answer_from_image(query, retrieved)
        result = RagResult(answer=answer, sources=sources, agent_used="multimodal")

    elif is_summarization_request(query):
        context = "\n\n".join(r.chunk.content for r in retrieved)
        answer = await summarize_content(context)
        result = RagResult(answer=answer, sources=sources, agent_used="summarization")

    else:
        prompt = build_rag_prompt(query, retrieved, history=conversation_history)
        answer = await generate_answer(prompt)
        result = RagResult(answer=answer, sources=sources, agent_used="rag")

    if target_language:
        result.answer = await translate_text(result.answer, target_language)
        result.agent_used = "translation"

    return result


async def run_rag_pipeline_stream(
    db: AsyncSession,
    query: str,
    document_ids: list[str] | None = None,
    conversation_history: list[ChatMessage] | None = None,
):
    """Streaming variant used by the websocket endpoint. Yields text tokens.
    Sources are retrieved and sent separately by the caller (see
    api/websocket.py) before streaming begins."""
    retrieved = await retrieve(db, query, document_ids=document_ids)

    if not retrieved:
        answer = await fallback_answer(query)
        for token in answer.split(" "):
            yield token + " "
        return

    prompt = build_rag_prompt(query, retrieved, history=conversation_history)
    async for token in generate_answer_stream(prompt):
        yield token
