"""
Aggregates all API sub-routers into a single router mounted by main.py.
"""
from fastapi import APIRouter

from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.api.history import router as history_router
from app.api.upload import router as upload_router
from app.api.websocket import router as websocket_router
from app.config import settings
from app.schemas.response import HealthResponse

api_router = APIRouter()

api_router.include_router(upload_router)
api_router.include_router(documents_router)
api_router.include_router(chat_router)
api_router.include_router(history_router)
api_router.include_router(websocket_router)


@api_router.get("/api/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok", app_name=settings.APP_NAME)
