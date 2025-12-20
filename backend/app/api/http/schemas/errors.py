from __future__ import annotations

from pydantic import BaseModel

# === Error Schemas ==========================================================


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
