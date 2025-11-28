from __future__ import annotations

from typing import Protocol

from app.application.common.ports.unit_of_work_port import UnitOfWorkPort
from app.application.profile.ports.profile_repository_port import ProfileRepositoryPort


class ProfileUnitOfWorkPort(UnitOfWorkPort, Protocol):
    """
    profile ドメイン用の Unit of Work。
    """
    profile_repo: ProfileRepositoryPort
