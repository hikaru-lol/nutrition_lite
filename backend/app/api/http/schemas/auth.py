from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# === Auth: Request Schemas ==================================================


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# === User / Auth: Common Schemas ===========================================

# trial / free / paid の 3 パターンに限定したプラン種別
UserPlanLiteral = Literal["trial", "free", "paid"]


class UserSummary(BaseModel):
    id: UUID
    email: EmailStr
    name: Optional[str] = None

    plan: UserPlanLiteral
    trial_ends_at: Optional[datetime] = None

    has_profile: bool
    created_at: datetime


class AuthUserResponse(BaseModel):
    user: UserSummary


class RefreshResponse(BaseModel):
    ok: bool
    user: UserSummary


# === Error Schemas ==========================================================


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
