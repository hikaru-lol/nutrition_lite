from __future__ import annotations

from dataclasses import dataclass

from .auth_user_dto import AuthUserDTO
from app.application.auth.ports.token_service_port import TokenPair


@dataclass
class RegisterInputDTO:
    email: str
    password: str
    name: str | None = None


@dataclass
class RegisterOutputDTO:
    user: AuthUserDTO
    tokens: TokenPair
