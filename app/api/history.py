"""
History API

Database-backed chat session management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.database.crud import (
    create_chat_session,
    list_chat_sessions,
    get_chat_session_with_document,
    get_messages_for_session,
    rename_chat_session,
    delete_chat_session,
    clear_chat_session,
    search_chat_sessions,
    count_messages_in_session,
)

router = APIRouter(
    prefix="/api/history",
    tags=["History"],
)


# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------
async def summary(db: AsyncSession, session):
    return {
        "id": session.id,
        "title": session.title,
        "document_id": session.document_id,
        "document_name": (
            session.document.filename
            if session.document
            else None
        ),
        "message_count": await count_messages_in_session(
            db,
            session.id,
        ),
        "created_at": session.created_at,
        "updated_at": session.updated_at,
    }




# --------------------------------------------------------------------
# Create Session
# --------------------------------------------------------------------

@router.post("/sessions")
async def create_session(
    body: dict,
    db: AsyncSession = Depends(get_db),
):
    title = body.get("title", "New Chat")
    document_id = body.get("document_id")

    session = await create_chat_session(
        db,
        title=title,
        document_id=document_id,
    )

    session = await get_chat_session_with_document(db, session.id)

    return await summary(db, session)


# --------------------------------------------------------------------
# List Sessions
# --------------------------------------------------------------------

@router.get("/sessions")
async def list_sessions(
    db: AsyncSession = Depends(get_db),
):
    sessions = await list_chat_sessions(db)

    return [
    await summary(db, s)
    for s in sessions
]


# --------------------------------------------------------------------
# Search Sessions
# --------------------------------------------------------------------

@router.get("/sessions/search")
async def search_sessions(
    q: str = Query(""),
    db: AsyncSession = Depends(get_db),
):
    sessions = await search_chat_sessions(db, q)

    return [
    await summary(db, s)
    for s in sessions
]


# --------------------------------------------------------------------
# Get One Session
# --------------------------------------------------------------------

@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    session = await get_chat_session_with_document(
        db,
        session_id,
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    messages = await get_messages_for_session(
        db,
        session_id,
    )

    return {
        "id": session.id,
        "title": session.title,
        "document_id": session.document_id,
        "document_name": (
            session.document.filename
            if session.document
            else None
        ),
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "sources": (
                    m.sources.get("items", [])
                    if isinstance(m.sources, dict)
                    else m.sources
                ),
                "created_at": m.created_at,
            }
            for m in messages
        ],
    }


# --------------------------------------------------------------------
# Rename Session
# --------------------------------------------------------------------

@router.patch("/sessions/{session_id}")
async def rename_session(
    session_id: str,
    body: dict,
    db: AsyncSession = Depends(get_db),
):
    session = await rename_chat_session(
        db,
        session_id,
        body.get("title", ""),
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    session = await get_chat_session_with_document(
        db,
        session.id,
    )

    
    return await summary(db, session)


# --------------------------------------------------------------------
# Delete Session
# --------------------------------------------------------------------

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    ok = await delete_chat_session(
        db,
        session_id,
    )

    if not ok:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    return {"success": True}


# --------------------------------------------------------------------
# Clear Messages
# --------------------------------------------------------------------

@router.delete("/sessions/{session_id}/messages")
async def clear_messages(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    ok = await clear_chat_session(
        db,
        session_id,
    )

    if not ok:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    return {"success": True}