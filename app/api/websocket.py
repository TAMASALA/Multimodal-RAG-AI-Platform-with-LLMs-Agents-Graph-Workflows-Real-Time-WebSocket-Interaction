"""
WebSocket endpoints.

1. /ws/chat/{session_id}
2. /ws/history
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.database.database import AsyncSessionLocal
from app.database.crud import (
    add_chat_message,
    create_chat_session,
    get_chat_session,
    get_recent_messages_for_memory,
)

from app.rag.pipeline import (
    run_rag_pipeline_stream,
    _to_source_refs,
)

from app.rag.retriever import retrieve

from app.websocket.manager import (
    manager,
    HISTORY_CHANNEL,
)

from app.utils.logger import logger

router = APIRouter(tags=["websocket"])


# ---------------------------------------------------------
# History websocket
# ---------------------------------------------------------

@router.websocket("/ws/history")
async def websocket_history(websocket: WebSocket):

    await manager.connect(HISTORY_CHANNEL, websocket)

    try:

        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        pass

    finally:
        manager.disconnect(HISTORY_CHANNEL, websocket)


# ---------------------------------------------------------
# Chat websocket
# ---------------------------------------------------------

@router.websocket("/ws/chat/{session_id}")
async def websocket_chat(
    websocket: WebSocket,
    session_id: str,
):

    #
    # Validate session BEFORE accepting websocket
    #

    async with AsyncSessionLocal() as db:

        session = await get_chat_session(db, session_id)

        if session is None:

            session = await create_chat_session(
                db,
                title="New Chat",
            )

            session_id = session.id

    #
    # Accept websocket ONLY ONCE
    #

    await manager.connect(session_id, websocket)

    try:

        while True:

            message = await websocket.receive_json()

            if message.get("type") != "query":

                await manager.send_json(
                    session_id,
                    {
                        "type": "error",
                        "payload": {
                            "detail": "Unsupported message type."
                        },
                    },
                )

                continue

            payload = message.get("payload", {})

            query = payload.get("query", "").strip()

            document_ids = payload.get("document_ids")

            if not query:

                await manager.send_json(
                    session_id,
                    {
                        "type": "error",
                        "payload": {
                            "detail": "Empty query."
                        },
                    },
                )

                continue

            async with AsyncSessionLocal() as db:

                history = await get_recent_messages_for_memory(
                    db,
                    session_id,
                )

                await add_chat_message(
                    db,
                    session_id,
                    role="user",
                    content=query,
                )

                retrieved = await retrieve(
                    db,
                    query,
                    document_ids=document_ids,
                )

                sources = _to_source_refs(retrieved)

                await manager.send_json(
                    session_id,
                    {
                        "type": "sources",
                        "payload": {
                            "items": [
                                s.model_dump()
                                for s in sources
                            ]
                        },
                    },
                )

                answer = ""

                async for token in run_rag_pipeline_stream(
                    db=db,
                    query=query,
                    document_ids=document_ids,
                    conversation_history=history,
                ):

                    answer += token

                    await manager.send_json(
                        session_id,
                        {
                            "type": "token",
                            "payload": {
                                "text": token,
                            },
                        },
                    )

                await add_chat_message(
                    db,
                    session_id,
                    role="assistant",
                    content=answer,
                    sources={
                        "items": [
                            s.model_dump()
                            for s in sources
                        ]
                    },
                )

            await manager.send_json(
                session_id,
                {
                    "type": "done",
                    "payload": {},
                },
            )

            await manager.broadcast(
                {
                    "type": "history_updated",
                    "payload": {
                        "action": "message",
                        "session_id": session_id,
                    },
                },
                exclude_key=session_id,
            )

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")

    except Exception as exc:

        logger.exception(exc)

        try:
            await websocket.send_json(
                {
                    "type": "error",
                    "payload": {
                        "detail": str(exc),
                    },
                }
            )
        except Exception:
            pass

    finally:
        manager.disconnect(session_id, websocket)