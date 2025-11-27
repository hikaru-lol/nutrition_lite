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


class DailyLogNotCompletedError(Exception):
    """
    その日が「記録完了」していないのに日次レポート生成を試みた場合のエラー。

    - レポート生成の前提条件違反。
    """

    pass


class DailyNutritionReportAlreadyExistsError(Exception):
    """
    同じ (user_id, date) の DailyNutritionReport が既に存在する場合のエラー。

    - 二重生成を避けるために使用。
    """

    pass
