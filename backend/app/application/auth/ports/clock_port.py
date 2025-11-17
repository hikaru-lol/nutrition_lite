from __future__ import annotations

from datetime import datetime
from typing import Protocol


class ClockPort(Protocol):
    """
    現在時刻を取得するためのポート。
    テスト時に差し替え可能にするために用意。
    """

    def now(self) -> datetime:
        ...
