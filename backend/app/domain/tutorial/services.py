"""チュートリアルドメインサービス"""

from __future__ import annotations

from .errors import InvalidTutorialIdError
from .value_objects import TutorialId

# 有効なチュートリアルIDの定義
VALID_TUTORIAL_IDS = {
    "onboarding_profile",    # プロフィール設定オンボーディング
    "onboarding_target",     # 目標設定オンボーディング
    "feature_today",         # 食事記録機能紹介
    "feature_calendar",      # カレンダー機能紹介
    "feature_nutrition",     # 栄養分析機能紹介
}


def validate_tutorial_id(tutorial_id: str) -> TutorialId:
    """チュートリアルID検証

    Args:
        tutorial_id: 検証対象のチュートリアルID

    Returns:
        TutorialId: 検証済みのチュートリアルID

    Raises:
        InvalidTutorialIdError: 無効なチュートリアルIDの場合
    """
    if tutorial_id not in VALID_TUTORIAL_IDS:
        raise InvalidTutorialIdError(tutorial_id)

    return TutorialId(tutorial_id)


def get_all_tutorial_ids() -> set[str]:
    """すべての有効なチュートリアルIDを取得"""
    return VALID_TUTORIAL_IDS.copy()