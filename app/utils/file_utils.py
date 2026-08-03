"""
Filesystem helpers: safe saving of uploads, unique naming, size/type validation.
"""
import hashlib
import os
import uuid
from pathlib import Path

import aiofiles
from fastapi import UploadFile, HTTPException

from app.config import settings
from app.utils.logger import logger


def generate_unique_filename(original_filename: str) -> str:
    ext = Path(original_filename).suffix.lower()
    unique_id = uuid.uuid4().hex
    return f"{unique_id}{ext}"


def validate_extension(filename: str) -> None:
    ext = Path(filename).suffix.lower()
    if ext not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {settings.allowed_extensions_list}",
        )


async def save_upload_file(upload_file: UploadFile, destination_dir: str) -> str:
    """Streams an UploadFile to disk, enforcing max size. Returns the saved path."""
    validate_extension(upload_file.filename)
    Path(destination_dir).mkdir(parents=True, exist_ok=True)

    unique_name = generate_unique_filename(upload_file.filename)
    dest_path = os.path.join(destination_dir, unique_name)

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    total_size = 0

    async with aiofiles.open(dest_path, "wb") as out_file:
        while chunk := await upload_file.read(1024 * 1024):
            total_size += len(chunk)
            if total_size > max_bytes:
                await out_file.close()
                os.remove(dest_path)
                raise HTTPException(
                    status_code=413,
                    detail=f"File exceeds max size of {settings.MAX_UPLOAD_SIZE_MB}MB",
                )
            await out_file.write(chunk)

    logger.info(f"Saved upload '{upload_file.filename}' -> {dest_path} ({total_size} bytes)")
    return dest_path


def file_hash(path: str) -> str:
    """SHA-256 hash of a file's contents, used for de-duplication."""
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def ensure_dir(path: str) -> str:
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def to_image_url(image_path: str | None) -> str | None:
    """Converts an absolute image path under settings.IMAGE_DIR into the
    public URL served by the /static/images mount (see app/main.py).
    Images are stored flatly in IMAGE_DIR, so only the basename is needed."""
    if not image_path:
        return None
    return f"/static/images/{Path(image_path).name}"
