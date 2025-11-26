from __future__ import annotations


class NutritionDomainError(Exception):
    """
    Nutrition ドメイン共通の基底例外。
    """
    pass


class NutritionEstimationFailedError(NutritionDomainError):
    """
    栄養推定ロジック内部で致命的なエラーが発生した場合の例外。

    例:
      - 外部APIエラー
      - LLMからの異常応答
      - 想定外のデータ形式
    """
    pass
