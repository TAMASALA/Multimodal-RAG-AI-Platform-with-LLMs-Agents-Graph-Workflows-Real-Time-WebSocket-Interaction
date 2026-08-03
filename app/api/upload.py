"""
Handles PDF upload: saves the file, deduplicates by content hash, creates a
Document row, and schedules the ingestion pipeline as a background task.
"""
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.crud import create_document, get_document_by_hash
from app.database.database import get_db
from app.database.models import DocumentStatus
from app.ingestion.pipeline import process_document
from app.schemas.upload import UploadResponse
from app.utils.file_utils import save_upload_file, file_hash
from app.utils.logger import logger

router = APIRouter(prefix="/api/upload", tags=["upload"])


@router.post("", response_model=UploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> UploadResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    saved_path = await save_upload_file(file, settings.UPLOAD_DIR)
    hash_value = file_hash(saved_path)

    existing = await get_document_by_hash(db, hash_value)
    if existing:
        logger.info(f"Duplicate upload detected, reusing document {existing.id}")
        return UploadResponse(
            document_id=existing.id,
            filename=existing.filename,
            status=existing.status.value,
            message="This document was already uploaded previously.",
        )

    document = await create_document(
        db, filename=file.filename, file_path=saved_path, file_hash=hash_value
    )

    background_tasks.add_task(
        process_document, document.id, saved_path, file.filename
    )

    return UploadResponse(
        document_id=document.id,
        filename=document.filename,
        status=DocumentStatus.PENDING.value,
    )
