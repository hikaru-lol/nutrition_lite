from __future__ import annotations

from typing import Protocol

from app.application.common.ports.unit_of_work_port import UnitOfWorkPort
from app.application.auth.ports.user_repository_port import UserRepositoryPort


class AuthUnitOfWorkPort(UnitOfWorkPort, Protocol):
    """
    auth ドメイン用の Unit of Work。
    """
    user_repo: UserRepositoryPort
