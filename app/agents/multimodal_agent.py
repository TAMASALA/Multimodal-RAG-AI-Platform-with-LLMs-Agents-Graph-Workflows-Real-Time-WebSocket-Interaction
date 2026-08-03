"""
Multimodal agent: handles questions that specifically reference a visual
element (chart, graph, image, figure) by re-running vision inference on the
most relevant retrieved image chunk rather than relying solely on its cached
OCR/caption text.
"""
from app.llm.groq_client import vision_completion
from app.llm.prompts import MULTIMODAL_VISION_SYSTEM_PROMPT
from app.rag.retriever import RetrievedChunk
from app.utils.logger import logger

VISUAL_TRIGGER_WORDS = ("chart", "graph", "figure", "image", "diagram", "picture", "plot")


def is_multimodal_request(query: str, retrieved: list[RetrievedChunk]) -> bool:
    lowered = query.lower()
    mentions_visual = any(trigger in lowered for trigger in VISUAL_TRIGGER_WORDS)
    has_image_chunk = any(
        r.chunk.chunk_type in ("image", "graph") and r.chunk.image_path for r in retrieved
    )
    return mentions_visual and has_image_chunk


async def answer_from_image(query: str, retrieved: list[RetrievedChunk]) -> str:
    """Picks the top-scoring image/graph chunk and asks the vision model
    the user's actual question directly against that image."""
    image_chunk = next(
        (r for r in retrieved if r.chunk.chunk_type in ("image", "graph") and r.chunk.image_path),
        None,
    )
    if not image_chunk:
        return "No relevant image was found to answer this question."

    try:
        return await vision_completion(
            system_prompt=MULTIMODAL_VISION_SYSTEM_PROMPT,
            user_prompt=query,
            image_path=image_chunk.chunk.image_path,
        )
    except Exception as exc:
        logger.error(f"Multimodal agent failed: {exc}")
        return "I found a relevant image but was unable to analyze it due to an internal error."
