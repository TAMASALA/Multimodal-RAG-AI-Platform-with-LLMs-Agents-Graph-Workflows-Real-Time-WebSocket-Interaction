from typing import Any, Optional

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "ok"
    app_name: str
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None


class GenericResponse(BaseModel):
    success: bool = True
    message: str = ""
    data: Optional[Any] = None
