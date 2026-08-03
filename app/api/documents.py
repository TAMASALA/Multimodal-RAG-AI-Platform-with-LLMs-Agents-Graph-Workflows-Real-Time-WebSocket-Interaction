"""
Document management endpoints: list, get status, delete, and serve the
original PDF file (for the frontend PDFViewer).
"""
import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.crud import list_documents, get_document, delete_document
from app.database.database import get_db
from app.schemas.upload import DocumentOut, DocumentListResponse
from app.schemas.response import GenericResponse
from app.utils.logger import logger

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("", response_model=DocumentListResponse)
async def get_documents(db: AsyncSession = Depends(get_db)) -> DocumentListResponse:
    docs = await list_documents(db)
    return DocumentListResponse(documents=[DocumentOut.model_validate(d) for d in docs])


@router.get("/{document_id}", response_model=DocumentOut)
async def get_document_status(document_id: str, db: AsyncSession = Depends(get_db)) -> DocumentOut:
    doc = await get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return DocumentOut.model_validate(doc)


@router.get("/{document_id}/file")
async def get_document_file(document_id: str, db: AsyncSession = Depends(get_db)) -> FileResponse:
    """Streams the original uploaded PDF, used by the frontend PDFViewer
    (e.g. embedded in an <iframe src="/api/documents/{id}/file">)."""
    doc = await get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=410, detail="Source file is no longer available on disk.")
    return FileResponse(doc.file_path, media_type="application/pdf", filename=doc.filename)


@router.delete("/{document_id}", response_model=GenericResponse)
async def remove_document(document_id: str, db: AsyncSession = Depends(get_db)) -> GenericResponse:
    doc = await get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    file_path = doc.file_path
    deleted = await delete_document(db, document_id)

    if deleted and file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError as exc:
            logger.warning(f"Could not remove file {file_path}: {exc}")

    # Note: corresponding FAISS vectors are left in place (FAISS doesn't support
    # cheap deletion); they simply become unreachable since their Chunk rows
    # are gone. A periodic reindex job (see scripts/build_index.py) reclaims space.
    return GenericResponse(success=True, message="Document deleted.")
