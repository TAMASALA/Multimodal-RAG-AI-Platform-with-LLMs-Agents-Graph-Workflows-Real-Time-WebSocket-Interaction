"""
CRUD operations for documents, chunks, chat sessions, and chat messages.
Keeps all raw SQLAlchemy query logic in one place.
"""
import datetime as dt
from typing import Optional, Sequence

from sqlalchemy import select, delete, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import Document, Chunk, ChatSession, ChatMessage, DocumentStatus
from app.utils.helpers import new_id


# ---------- Documents ----------

async def create_document(
    db: AsyncSession, filename: str, file_path: str, file_hash: str
) -> Document:
    doc = Document(
        id=new_id(),
        filename=filename,
        file_path=file_path,
        file_hash=file_hash,
        status=DocumentStatus.PENDING,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


async def get_document(db: AsyncSession, document_id: str) -> Optional[Document]:
    result = await db.execute(select(Document).where(Document.id == document_id))
    return result.scalar_one_or_none()


async def get_document_by_hash(db: AsyncSession, file_hash: str) -> Optional[Document]:
    result = await db.execute(select(Document).where(Document.file_hash == file_hash))
    return result.scalar_one_or_none()


async def list_documents(db: AsyncSession) -> Sequence[Document]:
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    return result.scalars().all()


async def update_document_status(
    db: AsyncSession, document_id: str, status: DocumentStatus, error_message: str | None = None
) -> None:
    doc = await get_document(db, document_id)
    if doc:
        doc.status = status
        doc.error_message = error_message
        await db.commit()


async def update_document_pages(db: AsyncSession, document_id: str, num_pages: int) -> None:
    doc = await get_document(db, document_id)
    if doc:
        doc.num_pages = num_pages
        await db.commit()


async def delete_document(db: AsyncSession, document_id: str) -> bool:
    doc = await get_document(db, document_id)
    if not doc:
        return False
    # Preserve chat history: detach any sessions pointing at this document
    # rather than letting a dangling foreign key remain.
    await db.execute(
        update(ChatSession).where(ChatSession.document_id == document_id).values(document_id=None)
    )
    await db.execute(delete(Chunk).where(Chunk.document_id == document_id))
    await db.delete(doc)
    await db.commit()
    return True


# ---------- Chunks ----------

async def create_chunk(
    db: AsyncSession,
    document_id: str,
    chunk_type: str,
    content: str,
    page_number: int,
    faiss_index: int,
    image_path: str | None = None,
    meta: dict | None = None,
) -> Chunk:
    chunk = Chunk(
        id=new_id(),
        document_id=document_id,
        chunk_type=chunk_type,
        content=content,
        page_number=page_number,
        faiss_index=faiss_index,
        image_path=image_path,
        meta=meta or {},
    )
    db.add(chunk)
    await db.commit()
    await db.refresh(chunk)
    return chunk


async def get_chunks_by_faiss_indices(
    db: AsyncSession, indices: list[int]
) -> Sequence[Chunk]:
    if not indices:
        return []
    result = await db.execute(select(Chunk).where(Chunk.faiss_index.in_(indices)))
    return result.scalars().all()


async def get_chunks_for_document(db: AsyncSession, document_id: str) -> Sequence[Chunk]:
    result = await db.execute(
        select(Chunk).where(Chunk.document_id == document_id).order_by(Chunk.page_number)
    )
    return result.scalars().all()


# ---------- Chat sessions & messages (Chat History feature) ----------

async def create_chat_session(
    db: AsyncSession, title: str = "New Chat", document_id: str | None = None
) -> ChatSession:
    """Creates a new chat session, optionally associated with an uploaded document.
    A session can exist without a document (general Q&A across all documents)."""
    session = ChatSession(id=new_id(), title=title, document_id=document_id)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_chat_session(db: AsyncSession, session_id: str) -> Optional[ChatSession]:
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    return result.scalar_one_or_none()


async def get_chat_session_with_document(
    db: AsyncSession, session_id: str
) -> Optional[ChatSession]:
    """Fetches a session with its associated document eagerly loaded, so the
    document filename can be shown in history lists without an extra query."""
    result = await db.execute(
        select(ChatSession)
        .options(selectinload(ChatSession.document))
        .where(ChatSession.id == session_id)
    )
    return result.scalar_one_or_none()


async def list_chat_sessions(
    db: AsyncSession, include_archived: bool = False
) -> Sequence[ChatSession]:
    """Lists all chat sessions (most recently active first), with the
    associated document eagerly loaded for display in the history sidebar."""
    stmt = select(ChatSession).options(selectinload(ChatSession.document))
    if not include_archived:
        stmt = stmt.where(ChatSession.is_archived.is_(False))
    stmt = stmt.order_by(ChatSession.updated_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


async def search_chat_sessions(db: AsyncSession, query: str) -> Sequence[ChatSession]:
    """Searches chat sessions by title match OR by matching content within
    their messages, returning distinct sessions ordered by recency."""
    like_pattern = f"%{query.strip()}%"

    stmt = (
        select(ChatSession)
        .options(selectinload(ChatSession.document))
        .outerjoin(ChatMessage, ChatMessage.session_id == ChatSession.id)
        .where(
            ChatSession.is_archived.is_(False),
            or_(
                ChatSession.title.ilike(like_pattern),
                ChatMessage.content.ilike(like_pattern),
            ),
        )
        .distinct()
        .order_by(ChatSession.updated_at.desc())
    )
    result = await db.execute(stmt)
    return result.unique().scalars().all()


async def rename_chat_session(
    db: AsyncSession, session_id: str, new_title: str
) -> Optional[ChatSession]:
    session = await get_chat_session(db, session_id)
    if not session:
        return None
    session.title = new_title.strip() or session.title
    await db.commit()
    await db.refresh(session)
    return session


async def touch_chat_session(db: AsyncSession, session_id: str) -> None:
    """Bumps updated_at so the session floats to the top of the history list
    after new activity (used on every new message)."""
    await db.execute(
        update(ChatSession)
        .where(ChatSession.id == session_id)
        .values(updated_at=dt.datetime.utcnow())
    )
    await db.commit()


async def set_session_document(
    db: AsyncSession, session_id: str, document_id: str | None
) -> Optional[ChatSession]:
    session = await get_chat_session(db, session_id)
    if not session:
        return None
    session.document_id = document_id
    await db.commit()
    await db.refresh(session)
    return session


async def delete_chat_session(db: AsyncSession, session_id: str) -> bool:
    session = await get_chat_session(db, session_id)
    if not session:
        return False
    await db.execute(delete(ChatMessage).where(ChatMessage.session_id == session_id))
    await db.delete(session)
    await db.commit()
    return True


async def clear_chat_session(db: AsyncSession, session_id: str) -> bool:
    """Deletes all messages in a session but keeps the session itself (and its
    title/document association) intact — equivalent to ChatGPT's 'clear chat'."""
    session = await get_chat_session(db, session_id)
    if not session:
        return False
    await db.execute(delete(ChatMessage).where(ChatMessage.session_id == session_id))
    await db.commit()
    return True


async def add_chat_message(
    db: AsyncSession, session_id: str, role: str, content: str, sources: dict | None = None
) -> ChatMessage:
    message = ChatMessage(
        id=new_id(), session_id=session_id, role=role, content=content, sources=sources or {}
    )
    db.add(message)
    await touch_chat_session(db, session_id)
    await db.commit()
    await db.refresh(message)
    return message


async def get_messages_for_session(
    db: AsyncSession, session_id: str, limit: int = 200
) -> Sequence[ChatMessage]:
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
    )
    return result.scalars().all()


async def get_recent_messages_for_memory(
    db: AsyncSession, session_id: str, max_messages: int = 12
) -> Sequence[ChatMessage]:
    """Fetches the most recent N messages (oldest-first) for use as
    conversation memory/context when building the next LLM prompt."""
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(max_messages)
    )
    messages = result.scalars().all()
    return list(reversed(messages))


from sqlalchemy import func

async def count_messages_in_session(
    db: AsyncSession,
    session_id: str,
) -> int:
    result = await db.execute(
        select(func.count(ChatMessage.id))
        .where(ChatMessage.session_id == session_id)
    )
    return result.scalar_one()
