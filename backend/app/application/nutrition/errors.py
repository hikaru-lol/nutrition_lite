from __future__ import annotations


class NutritionApplicationError(Exception):
    """
    Nutrition アプリケーション層の基底例外。
    """
    pass


class DailyReportGenerationFailedError(NutritionApplicationError):
    """
    DailyReport の生成に失敗したときのエラー。
    """
