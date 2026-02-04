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


class DailyLogNotCompletedError(NutritionDomainError):
    """
    その日が「記録完了」していないのに日次レポート生成を試みた場合のエラー。

    - レポート生成の前提条件違反。
    """

    pass


class DailyNutritionReportAlreadyExistsError(NutritionDomainError):
    """
    同じ (user_id, date) の DailyNutritionReport が既に存在する場合のエラー。

    - 二重生成を避けるために使用。
    """

    pass


class NotEnoughDailyReportsError(NutritionDomainError):
    """
    提案生成に必要な日次レポート数が足りない場合のエラー。

    - 例: 「直近 5 日分必要だが 3 日分しかない」など。
    """

    pass


class MealRecommendationAlreadyExistsError(NutritionDomainError):
    """
    同じ (user_id, generated_for_date) の提案が既に存在する場合のエラー。

    注意: 新しい制約緩和版では使用されないが、後方互換性のために保持。
    """

    pass


class MealRecommendationCooldownError(NutritionDomainError):
    """
    クールダウン期間中の再生成を試みた場合のエラー。

    Attributes:
        wait_until: 次回生成可能時刻
        remaining_minutes: 残り時間（分）
    """

    def __init__(self, wait_until, remaining_minutes: int = 0):
        self.wait_until = wait_until
        self.remaining_minutes = remaining_minutes
        super().__init__(
            f"Must wait {remaining_minutes} minutes before next generation"
        )


class MealRecommendationDailyLimitError(NutritionDomainError):
    """
    1日の生成上限に達した場合のエラー。

    Attributes:
        current_count: 現在の生成回数
        limit: 上限回数
    """

    def __init__(self, current_count: int, limit: int):
        self.current_count = current_count
        self.limit = limit
        super().__init__(
            f"Daily generation limit reached: {current_count}/{limit}"
        )


class DailyReportGenerationFailedError(NutritionDomainError):
    """
    日次レポート生成（LLM）が失敗した場合のエラー。
    """
