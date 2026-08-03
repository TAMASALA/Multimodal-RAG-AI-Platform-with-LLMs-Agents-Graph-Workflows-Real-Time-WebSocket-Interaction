"""
Fallback agent: invoked when retrieval yields no chunks above the similarity
threshold. Avoids hallucinating a confident answer from the RAG system prompt
by using a distinct, more cautious prompt.
"""
from app.llm.groq_client import chat_completion
from app.llm.prompts import FALLBACK_PROMPT
from app.utils.logger import logger


async def fallback_answer(query: str) -> str:
    try:
        return await chat_completion(
            system_prompt="You are a careful, honest assistant.",
            user_prompt=FALLBACK_PROMPT.format(question=query),
            max_tokens=300,
        )
    except Exception as exc:
        logger.error(f"Fallback agent failed: {exc}")
        return (
            "I couldn't find relevant information in your uploaded documents, "
            "and I ran into an internal error trying to help further. "
            "Please try rephrasing your question or upload a relevant document."
        )
