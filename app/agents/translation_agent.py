"""
Translation agent: translates a generated answer (or arbitrary text) into a
target language using the LLM. Kept as a distinct agent so it can be swapped
for a dedicated MT model later without touching the RAG pipeline.
"""
from app.llm.groq_client import chat_completion
from app.llm.prompts import TRANSLATION_SYSTEM_PROMPT
from app.utils.logger import logger


async def translate_text(text: str, target_language: str) -> str:
    if not text.strip():
        return text
    try:
        system_prompt = TRANSLATION_SYSTEM_PROMPT.format(target_language=target_language)
        return await chat_completion(system_prompt=system_prompt, user_prompt=text)
    except Exception as exc:
        logger.error(f"Translation agent failed: {exc}")
        return text
