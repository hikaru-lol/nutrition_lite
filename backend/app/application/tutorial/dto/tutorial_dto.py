"""チュートリアル機能のDTO定義"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TutorialCompletionDTO:
    """チュートリアル完了記録のDTO"""
    user_id: str
    tutorial_id: str
    completed_at: datetime


@dataclass(frozen=True)
class GetTutorialStatusInputDTO:
    """チュートリアル状況取得の入力DTO"""
    user_id: str


@dataclass(frozen=True)
class GetTutorialStatusOutputDTO:
    """チュートリアル状況取得の出力DTO"""
    completed_tutorial_ids: list[str]


@dataclass(frozen=True)
class CompleteTutorialInputDTO:
    """チュートリアル完了の入力DTO"""
    user_id: str
    tutorial_id: str


@dataclass(frozen=True)
class CompleteTutorialOutputDTO:
    """チュートリアル完了の出力DTO"""
    tutorial_id: str
    completed_at: datetime