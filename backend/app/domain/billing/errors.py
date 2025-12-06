from __future__ import annotations


class BillingError(Exception):
    """Billing コンテキスト共通のベースエラー。"""


class BillingAccountNotFoundError(BillingError):
    """指定ユーザーに対応する BillingAccount が存在しない。"""


class StripeCustomerNotFoundError(BillingError):
    """Stripe 上の Customer が見つからない / ひも付けできない。"""


class BillingInconsistentStateError(BillingError):
    """内部の BillingAccount と Stripe 側の状態が矛盾している。"""
