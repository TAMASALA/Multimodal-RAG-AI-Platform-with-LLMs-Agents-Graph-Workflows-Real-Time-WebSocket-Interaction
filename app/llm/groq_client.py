"""
Thin, resilient wrapper around the Groq chat completions API.
Centralizes model selection, retries, and streaming so callers never
touch the Groq SDK directly.
"""
import base64
from typing import AsyncIterator, Optional

from groq import AsyncGroq

from app.config import settings
from app.utils.logger import logger
from app.utils.retry import llm_retry

_client: Optional[AsyncGroq] = None


def get_client() -> AsyncGroq:
    global _client
    if _client is None:
        if not settings.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY is not set. LLM calls will fail until configured.")
        _client = AsyncGroq(api_key=settings.GROQ_API_KEY)
    return _client


@llm_retry(max_attempts=3)
async def chat_completion(
    system_prompt: str,
    user_prompt: str,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> str:
    """Single-shot, non-streaming chat completion. Returns the full text response."""
    client = get_client()
    response = await client.chat.completions.create(
        model=model or settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature if temperature is not None else settings.GROQ_TEMPERATURE,
        max_tokens=max_tokens or settings.GROQ_MAX_TOKENS,
    )
    return response.choices[0].message.content or ""


async def chat_completion_stream(
    system_prompt: str,
    user_prompt: str,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> AsyncIterator[str]:
    """Streaming chat completion. Yields incremental text tokens/chunks."""
    client = get_client()
    stream = await client.chat.completions.create(
        model=model or settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature if temperature is not None else settings.GROQ_TEMPERATURE,
        max_tokens=max_tokens or settings.GROQ_MAX_TOKENS,
        stream=True,
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta
        if delta and delta.content:
            yield delta.content


def _encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


@llm_retry(max_attempts=3)
async def vision_completion(
    system_prompt: str,
    user_prompt: str,
    image_path: str,
    model: Optional[str] = None,
    max_tokens: Optional[int] = None,
) -> str:
    """Vision-capable chat completion for image/graph/chart understanding."""
    client = get_client()
    b64_image = _encode_image(image_path)

    response = await client.chat.completions.create(
        model=model or settings.GROQ_VISION_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64_image}"},
                    },
                ],
            },
        ],
        max_tokens=max_tokens or settings.GROQ_MAX_TOKENS,
    )
    return response.choices[0].message.content or ""
