from __future__ import annotations

from dataclasses import dataclass
from app.application.auth.dto.auth_user_dto import AuthUserDTO
from app.application.auth.ports.token_service_port import TokenPair


@dataclass
class RefreshInputDTO:
    refresh_token: str


@dataclass
class RefreshOutputDTO:
    user: AuthUserDTO
    tokens: TokenPair
