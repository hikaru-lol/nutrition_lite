from __future__ import annotations

from datetime import datetime
from typing import Literal

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
    id: str
    email: EmailStr
    name: str | None = None
    plan: UserPlanLiteral
    trialEndsAt: datetime | None = None
    hasProfile: bool
    createdAt: datetime


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
