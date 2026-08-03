"""
Lightweight equation detection over extracted page text.
Uses heuristics (symbol density) to flag likely mathematical content,
then optionally asks the LLM to reconstruct it into clean notation.
"""
import re

from app.llm.groq_client import chat_completion
from app.llm.prompts import EQUATION_EXPLAIN_PROMPT
from app.utils.helpers import clean_text
from app.utils.logger import logger

# Characters/symbols commonly found in equations
_MATH_SYMBOLS = re.compile(r"[=+\-*/^√∑∫≤≥≠±πθαβγΔ∞]")
_MATH_LINE_PATTERN = re.compile(r"^[\dA-Za-z\s=+\-*/^().,√∑∫≤≥≠±πθαβγΔ∞_{}\[\]]+$")


def extract_candidate_equations(page_text: str) -> list[str]:
    """Scans page text line-by-line for lines that are likely equations
    (high symbol density, short length, minimal natural-language words)."""
    candidates = []
    for line in page_text.splitlines():
        stripped = line.strip()
        if not stripped or len(stripped) > 200:
            continue

        symbol_count = len(_MATH_SYMBOLS.findall(stripped))
        word_count = len(stripped.split())
        if symbol_count >= 2 and symbol_count >= word_count * 0.3:
            candidates.append(stripped)

    return candidates


async def reconstruct_equation(raw_text: str) -> str:
    """Uses the LLM to clean up OCR/text-extracted equation fragments into
    readable notation plus a brief factual description."""
    try:
        result = await chat_completion(
            system_prompt="You are a precise mathematical notation assistant.",
            user_prompt=EQUATION_EXPLAIN_PROMPT.format(raw_text=raw_text),
            max_tokens=256,
        )
        return clean_text(result)
    except Exception as exc:
        logger.error(f"Equation reconstruction failed: {exc}")
        return raw_text
