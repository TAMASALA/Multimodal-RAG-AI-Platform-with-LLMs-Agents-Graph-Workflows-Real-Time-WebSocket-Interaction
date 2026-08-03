"""
Centralized logging configuration using loguru.
Import `logger` anywhere in the app for consistent, structured logs.
"""
import sys

from loguru import logger

from app.config import settings

logger.remove()
logger.add(
    sys.stdout,
    level=settings.LOG_LEVEL,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    ),
    colorize=True,
    backtrace=False,
    diagnose=False,
)
logger.add(
    "./storage/cache/app.log",
    level="DEBUG",
    rotation="10 MB",
    retention="7 days",
    compression="zip",
    enqueue=True,
)

__all__ = ["logger"]
