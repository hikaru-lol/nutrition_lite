from __future__ import annotations


class TargetNotFoundError(Exception):
    """
    指定された Target が存在しない、またはログインユーザーに属していないときのエラー。
    API 層で 404 にマッピングする想定。
    """
    pass


class TargetLimitExceededError(Exception):
    """
    ユーザーが作成できる TargetDefinition の上限を超えたときのエラー。
    API 層で 400 などにマッピングする想定。
    """
    pass
