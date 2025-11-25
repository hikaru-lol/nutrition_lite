from __future__ import annotations


class MealDomainError(Exception):
    """Meal ドメイン共通の基底例外。"""
    pass


class InvalidMealTypeError(MealDomainError):
    """
    不正な meal_type が指定された場合のエラー。
    （通常は MealType Enum で防げるので、実際に使う場面は少ない想定）
    """
    pass


class InvalidMealIndexError(MealDomainError):
    """
    meal_type と meal_index の組み合わせが不正な場合のエラー。

    例:
      - meal_type == main なのに meal_index が None または 1 未満
      - meal_type == snack なのに meal_index が None 以外
    """
    pass


class InvalidFoodAmountError(MealDomainError):
    """
    食事の量指定が不正な場合のエラー。

    ルール:
      - 「amount_value + amount_unit」か「serving_count」のどちらかは必須
      - amount_value が指定されている場合は 0 より大きい必要がある
      - serving_count が指定されている場合は 0 より大きい必要がある
      - amount_value だけ、amount_unit だけ、といった片方だけ指定は NG
    """
    pass


class FoodEntryNotFoundError(MealDomainError):
    """
    指定された FoodEntry が見つからない場合のエラー。
    Repository からの取得時などに使用する想定。
    """
    pass
