from __future__ import annotations


class TargetError(Exception):
    """Target アプリケーション用のベース例外。"""
    pass


class TargetNotFoundError(TargetError):
    """
    指定された Target が存在しない、
    またはログインユーザーに属していないときのエラー。
    """
    pass


class TargetLimitExceededError(TargetError):
    """
    ユーザーが作成できる TargetDefinition の上限を超えたときのエラー。
    """
    pass
