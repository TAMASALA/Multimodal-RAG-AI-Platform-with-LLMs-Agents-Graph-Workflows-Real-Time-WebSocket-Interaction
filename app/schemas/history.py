"""
Pydantic schemas for the Chat History feature: creating sessions, renaming,
searching, and listing sessions with their associated document and message
counts for the history sidebar.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.chat import ChatMessageOut


class CreateChatSessionRequest(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)
    document_id: Optional[str] = None


class RenameChatSessionRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)


class SearchChatSessionsRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=255)


class ChatSessionSummary(BaseModel):
    """Lightweight session representation used in list/search results —
    everything the history sidebar needs without fetching full messages."""
    id: str
    title: str
    document_id: Optional[str] = None
    document_name: Optional[str] = None
    message_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionListResponse(BaseModel):
    sessions: list[ChatSessionSummary]


class ChatSessionDetailResponse(BaseModel):
    id: str
    title: str
    document_id: Optional[str] = None
    document_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: list[ChatMessageOut]

    model_config = {"from_attributes": True}


class ChatSessionActionResponse(BaseModel):
    success: bool = True
    message: str = ""
    session_id: Optional[str] = None