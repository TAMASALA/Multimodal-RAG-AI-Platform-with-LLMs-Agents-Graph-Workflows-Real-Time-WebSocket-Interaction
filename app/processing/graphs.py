"""
Graph/chart understanding: uses a vision-capable LLM to turn an extracted
chart/graph image into a factual textual description that can be embedded
and retrieved like any text chunk.
"""
from app.llm.groq_client import vision_completion
from app.llm.prompts import MULTIMODAL_VISION_SYSTEM_PROMPT, GRAPH_CAPTION_PROMPT
from app.utils.helpers import clean_text
from app.utils.logger import logger

# Simple heuristic keywords that suggest an image is a chart/graph rather than
# a decorative image or photo — used to decide whether to spend an LLM call on it.
GRAPH_KEYWORDS = ("chart", "graph", "plot", "figure", "diagram")


async def describe_graph_image(image_path: str) -> str:
    """Calls the vision LLM to produce a factual caption/description of a chart image."""
    try:
        description = await vision_completion(
            system_prompt=MULTIMODAL_VISION_SYSTEM_PROMPT,
            user_prompt=GRAPH_CAPTION_PROMPT,
            image_path=image_path,
        )
        return clean_text(description)
    except Exception as exc:
        logger.error(f"Graph description failed for {image_path}: {exc}")
        return ""


def looks_like_graph(width: int, height: int, ocr_text: str = "") -> bool:
    """Lightweight heuristic to flag likely chart/graph images before spending an LLM call.
    Charts tend to be wider-than-tall or contain axis-like short numeric OCR tokens."""
    aspect_ratio = width / max(height, 1)
    has_axis_like_text = any(k in ocr_text.lower() for k in GRAPH_KEYWORDS)
    return 0.8 <= aspect_ratio <= 3.0 or has_axis_like_text
