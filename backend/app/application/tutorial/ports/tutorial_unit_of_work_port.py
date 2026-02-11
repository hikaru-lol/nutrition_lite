"""チュートリアル機能のUnit of Workポート"""

from __future__ import annotations

from typing import Protocol

from app.application.common.ports.unit_of_work_port import UnitOfWorkPort
from app.application.tutorial.ports.tutorial_repository_port import TutorialRepositoryPort


class TutorialUnitOfWorkPort(UnitOfWorkPort, Protocol):
    """チュートリアル機能のUnit of Workインターフェース"""

    tutorial_repo: TutorialRepositoryPort