from __future__ import annotations

from typing import Protocol

from app.domain.auth.value_objects import UserId
from app.domain.billing.entities import BillingAccount


class BillingRepositoryPort(Protocol):
    """
    BillingAccount を読み書きするためのリポジトリポート。
    """

    def get_by_user_id(self, user_id: UserId) -> BillingAccount | None:
        """
        ユーザーに対応する BillingAccount を取得する。

        - 存在しなければ None。
        """
        ...

    def save(self, account: BillingAccount) -> None:
        """
        BillingAccount を保存する。

        - insert / update を吸収する形で実装する想定。
        - トランザクション管理は UoW 側で行う。
        """
        ...
