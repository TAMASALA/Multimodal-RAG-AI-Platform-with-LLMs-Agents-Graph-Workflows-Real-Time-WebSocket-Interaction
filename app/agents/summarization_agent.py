"""
Summarization agent: condenses retrieved context or full document chunks
into a structured summary. Used when the user explicitly asks to
"summarize" a document/topic.
"""
from app.llm.groq_client import chat_completion
from app.llm.prompts import SUMMARIZATION_SYSTEM_PROMPT
from app.utils.logger import logger

SUMMARIZE_TRIGGER_WORDS = ("summarize", "summary", "tl;dr", "overview of", "recap")


def is_summarization_request(query: str) -> bool:
    lowered = query.lower()
    return any(trigger in lowered for trigger in SUMMARIZE_TRIGGER_WORDS)


async def summarize_content(content: str) -> str:
    if not content.strip():
        return "There is no content available to summarize."
    try:
        return await chat_completion(
            system_prompt=SUMMARIZATION_SYSTEM_PROMPT,
            user_prompt=content,
            max_tokens=600,
        )
    except Exception as exc:
        logger.error(f"Summarization agent failed: {exc}")
        return "Summarization failed due to an internal error."
