from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    query: str = Field(..., min_length=1, max_length=4000)
    document_ids: Optional[list[str]] = None  # restrict retrieval to specific docs
    target_language: Optional[str] = None  # if set, triggers translation agent
    stream: bool = False


class SourceRef(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    page_number: int
    chunk_type: str
    snippet: str
    score: float
    image_url: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: list[SourceRef] = []
    agent_used: Literal[
        "rag", "translation", "summarization", "multimodal", "fallback"
    ] = "rag"


class ChatMessageOut(BaseModel):
    id: str
    role: str
    content: str
    sources: dict = {}
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: list[ChatMessageOut]


class WSMessage(BaseModel):
    """Envelope for all websocket traffic (both directions)."""
    type: Literal["query", "token", "sources", "done", "error", "status"]
    payload: dict
