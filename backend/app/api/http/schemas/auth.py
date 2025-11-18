from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


UserPlanLiteral = Literal["trial", "free", "paid"]


class UserSummary(BaseModel):
    id: UUID
    email: EmailStr
    name: Optional[str] = None

    # trial / free / paid の 3 パターンに絞る
    plan: Literal["trial", "free", "paid"]

    trial_ends_at: Optional[datetime] = None
    has_profile: bool
    created_at: datetime


class AuthUserResponse(BaseModel):
    user: UserSummary


class RefreshResponse(BaseModel):
    ok: bool
    user: UserSummary


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
