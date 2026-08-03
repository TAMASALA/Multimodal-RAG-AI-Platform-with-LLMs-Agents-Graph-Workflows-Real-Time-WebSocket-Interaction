from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: str
    filename: str
    status: str
    num_pages: int
    error_message: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    message: str = "Document accepted and queued for processing."


class DocumentListResponse(BaseModel):
    documents: list[DocumentOut]
