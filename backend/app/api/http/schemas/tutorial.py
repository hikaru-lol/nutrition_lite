"""チュートリアル機能のPydanticスキーマ"""

from __future__ import annotations

from pydantic import BaseModel


class TutorialStatusResponse(BaseModel):
    """チュートリアル完了状況レスポンス"""
    completed: list[str]

    model_config = {
        "json_schema_extra": {
            "example": {
                "completed": ["onboarding_profile", "feature_today"]
            }
        }
    }


class TutorialCompleteResponse(BaseModel):
    """チュートリアル完了レスポンス"""
    tutorial_id: str
    completed_at: str  # ISO8601 format

    model_config = {
        "json_schema_extra": {
            "example": {
                "tutorial_id": "onboarding_profile",
                "completed_at": "2024-02-01T10:30:00+00:00"
            }
        }
    }