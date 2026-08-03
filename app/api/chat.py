"""
REST chat endpoint: runs the RAG pipeline synchronously and returns the full
answer with sources. For token-by-token streaming, see api/websocket.py.
Conversation memory (recent prior turns) is automatically included so
follow-up questions ("what about page 2?") resolve correctly within a session.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.crud import (
    create_chat_session,
    get_chat_session,
    add_chat_message,
    get_messages_for_session,
    get_recent_messages_for_memory,
    list_chat_sessions,
)
from app.database.database import get_db
from app.rag.pipeline import run_rag_pipeline
from app.schemas.chat import ChatRequest, ChatResponse, ChatHistoryResponse, ChatMessageOut
from app.websocket.manager import manager

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)) -> ChatResponse:
    session_id = request.session_id
    if session_id:
        session = await get_chat_session(db, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found.")
    else:
        # Auto-title from the first query; associate the session with a single
        # uploaded document when the request scopes to exactly one.
        implied_document_id = (
            request.document_ids[0]
            if request.document_ids and len(request.document_ids) == 1
            else None
        )
        session = await create_chat_session(
            db, title=request.query[:60], document_id=implied_document_id
        )
        session_id = session.id

    # Conversation memory: prior turns in this session, used for reference
    # resolution only (see build_history_block) — fetched BEFORE the new
    # user message is persisted so it doesn't duplicate the current turn.
    conversation_history = await get_recent_messages_for_memory(db, session_id)

    await add_chat_message(db, session_id, role="user", content=request.query)

    result = await run_rag_pipeline(
        db,
        query=request.query,
        document_ids=request.document_ids,
        target_language=request.target_language,
        conversation_history=conversation_history,
    )

    await add_chat_message(
        db,
        session_id,
        role="assistant",
        content=result.answer,
        sources={"items": [s.model_dump() for s in result.sources]},
    )

    await manager.broadcast(
        {"type": "history_updated", "payload": {"action": "message", "session_id": session_id}}
    )

    return ChatResponse(
        session_id=session_id,
        answer=result.answer,
        sources=result.sources,
        agent_used=result.agent_used,
    )


@router.get("/sessions")
async def get_sessions(db: AsyncSession = Depends(get_db)):
    """Legacy lightweight session list. Prefer /api/history/sessions for the
    full Chat History sidebar (includes document name and message counts)."""
    sessions = await list_chat_sessions(db)
    return {"sessions": [{"id": s.id, "title": s.title, "created_at": s.created_at} for s in sessions]}


@router.get("/sessions/{session_id}/messages", response_model=ChatHistoryResponse)
async def get_session_messages(
    session_id: str, db: AsyncSession = Depends(get_db)
) -> ChatHistoryResponse:
    session = await get_chat_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found.")

    messages = await get_messages_for_session(db, session_id)
    return ChatHistoryResponse(
        session_id=session_id,
        messages=[ChatMessageOut.model_validate(m) for m in messages],
    )
