from __future__ import annotations


class TargetError(Exception):
    """target ドメインに関する基底エラー。"""


class MaxTargetsReachedError(TargetError):
    """
    ユーザーが作成可能なターゲット数の上限（例: 5件）を超えた場合。 
    """


class NoActiveTargetError(TargetError):
    """
    ユーザーにアクティブなターゲットが存在しない場合。
    """


class TargetDomainError(Exception):
    """Target ドメインレベルのベース例外。"""
    pass


class InvalidTargetNutrientError(TargetDomainError):
    """
    不正な NutrientCode や不整合のある栄養素指定が行われたときのエラー。
    """
    pass
