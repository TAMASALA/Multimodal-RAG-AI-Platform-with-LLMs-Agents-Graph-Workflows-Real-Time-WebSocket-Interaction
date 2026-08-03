"""
Reusable retry decorators for flaky I/O (LLM calls, OCR, network, disk).
"""
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
import logging

from app.utils.logger import logger

_std_logger = logging.getLogger("tenacity")


def llm_retry(max_attempts: int = 3):
    """Retry decorator tuned for LLM API calls (network errors, rate limits)."""
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True,
        before_sleep=before_sleep_log(_std_logger, logging.WARNING),
    )


def io_retry(max_attempts: int = 3):
    """Retry decorator for filesystem / parsing operations."""
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        retry=retry_if_exception_type((OSError, IOError)),
        reraise=True,
    )
