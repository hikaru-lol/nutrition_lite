from __future__ import annotations


class TargetError(Exception):
    """target ドメインに関する基底エラー。"""


class MaxTargetsReachedError(TargetError):
    """
    ユーザーが作成可能なターゲット数の上限（例: 5件）を超えた場合。
    """


class TargetNotFoundError(TargetError):
    """
    指定されたターゲットが存在しない、またはユーザーに属していない場合。
    """


class NoActiveTargetError(TargetError):
    """
    ユーザーにアクティブなターゲットが存在しない場合。
    """
