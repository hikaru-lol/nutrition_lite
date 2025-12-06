from __future__ import annotations

from typing import Protocol

from app.domain.auth.value_objects import UserId


class PlanCheckerPort(Protocol):
    """
    ユーザーのプラン状態をチェックするためのポート。

    - UseCase 側は Auth の内部構造を知らずに、このポート越しにプラン判定だけを依頼する。
    """

    def ensure_premium_feature(self, user_id: UserId) -> None:
        """
        栄養計算 / 日次レポート / 提案などのプレミアム機能が利用可能かチェックする。

        - 利用できない場合は PremiumFeatureRequiredError を投げる。
        - 利用できる場合は何も返さない。
        """
        ...
