from __future__ import annotations

from dataclasses import dataclass

from .auth_user_dto import AuthUserDTO
from app.application.auth.ports.token_service_port import TokenPair


@dataclass
class LoginInputDTO:
    email: str
    password: str


@dataclass
class LoginOutputDTO:
    user: AuthUserDTO
    tokens: TokenPair
