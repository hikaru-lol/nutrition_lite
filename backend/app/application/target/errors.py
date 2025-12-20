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


class TargetGenerationFailedError(TargetError):
    """LLM によるターゲット生成に失敗したときのエラー。"""
    pass


class TargetProfileNotFoundError(TargetError):
    """
    ターゲットを生成するためのプロフィールが存在しないときのエラー。
    """
    pass
