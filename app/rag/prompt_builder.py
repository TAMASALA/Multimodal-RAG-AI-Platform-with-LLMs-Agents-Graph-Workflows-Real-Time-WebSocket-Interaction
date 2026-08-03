"""
Builds the final LLM prompt from retrieved chunks, numbering sources so the
model can cite them and the frontend can map citations back to sources.
Also formats recent conversation history so the model can resolve
pronouns/references ("it", "that chart") without treating history as fact.
"""
from app.database.models import ChatMessage
from app.llm.prompts import RAG_USER_TEMPLATE, HISTORY_BLOCK_TEMPLATE
from app.rag.retriever import RetrievedChunk

MAX_HISTORY_CHARS_PER_MESSAGE = 400


def build_context_block(retrieved: list[RetrievedChunk]) -> str:
    blocks = []
    for i, item in enumerate(retrieved, start=1):
        chunk = item.chunk
        header = (
            f"[Source {i}] (document: {chunk.meta.get('document_name', 'unknown')}, "
            f"page: {chunk.page_number}, type: {chunk.chunk_type})"
        )
        blocks.append(f"{header}\n{chunk.content}")
    return "\n\n---\n\n".join(blocks)


def build_history_block(history: list[ChatMessage] | None) -> str:
    """Formats recent turns as `Role: content` lines, truncating long
    messages so history never dominates the prompt's token budget."""
    if not history:
        return ""

    lines = []
    for msg in history:
        role_label = "User" if msg.role == "user" else "Assistant"
        content = msg.content.strip()
        if len(content) > MAX_HISTORY_CHARS_PER_MESSAGE:
            content = content[:MAX_HISTORY_CHARS_PER_MESSAGE] + "..."
        lines.append(f"{role_label}: {content}")

    return HISTORY_BLOCK_TEMPLATE.format(history="\n".join(lines))


def build_rag_prompt(
    question: str,
    retrieved: list[RetrievedChunk],
    history: list[ChatMessage] | None = None,
) -> str:
    context = build_context_block(retrieved)
    history_block = build_history_block(history)
    return RAG_USER_TEMPLATE.format(
        history_block=history_block, context=context, question=question
    )
