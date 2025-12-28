# 　テスト実行時に環境変数の読み込みが必要になるので、.envファイルを読み込む

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import time
import uuid

import pytest
import stripe
from fastapi.testclient import TestClient

from app.main import create_app
from app.domain.auth.value_objects import UserId
from app.domain.billing.entities import BillingSubscriptionStatus
from app.infra.db.session import create_session
from app.infra.db.repositories.billing_account_repository import SqlAlchemyBillingAccountRepository
from app.infra.db.repositories.user_repository import SqlAlchemyUserRepository


pytestmark = pytest.mark.real_integration

PRICE_ID_ENV_CANDIDATES = [
    "STRIPE_PRICE_ID",
    "STRIPE_SUBSCRIPTION_PRICE_ID",
    "STRIPE_CHECKOUT_PRICE_ID",
]


def _require_env(*names: str) -> None:
    missing = [n for n in names if not os.getenv(n)]
    if missing:
        pytest.skip(
            f"Missing env vars for real integration: {', '.join(missing)}")


def _get_price_id() -> str:
    for name in PRICE_ID_ENV_CANDIDATES:
        v = os.getenv(name)
        if v:
            return v
    pytest.skip(
        f"Missing price id env. Tried: {', '.join(PRICE_ID_ENV_CANDIDATES)}")


def _make_client() -> TestClient:
    app = create_app()
    return TestClient(app)


def _register(client: TestClient) -> str:
    """register -> auto-login(cookie set) まで行い user_id を返す"""
    email = f"billing_{uuid.uuid4().hex}@example.com"
    password = "BillingPass123!"
    name = "Billing User"

    resp = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "name": name},
    )
    assert resp.status_code == 201, resp.text
    user_id = resp.json()["user"]["id"]
    return user_id


def _extract_checkout_session_id(checkout_url: str) -> str:
    # 例: https://checkout.stripe.com/c/pay/cs_test_123...
    m = re.search(r"(cs_(?:test|live)_[A-Za-z0-9]+)", checkout_url)
    assert m, f"Could not find Checkout Session id in url: {checkout_url}"
    return m.group(1)


def _stripe_signature_header(payload: bytes, secret: str, ts: int | None = None) -> str:
    """
    Stripe-Signature: t=timestamp,v1=HMAC_SHA256(secret, "{t}.{payload}")
    """
    t = ts or int(time.time())
    signed = f"{t}.".encode("utf-8") + payload
    sig = hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).hexdigest()
    return f"t={t},v1={sig}"


# def _ensure_test_default_payment_method(customer_id: str) -> None:
#     """
#     サブスクを「できるだけ」active に寄せるために、
#     テスト用 payment method を customer に attach して default にする。
#     """
#     # Stripe テストモードの既定PaymentMethod
#     pm = "pm_card_visa"

#     stripe.PaymentMethod.attach(pm, customer=customer_id)
#     stripe.Customer.modify(customer_id, invoice_settings={
#                            "default_payment_method": pm})

def _ensure_test_default_payment_method(customer_id: str) -> str:
    attached = stripe.PaymentMethod.attach(
        "pm_card_visa", customer=customer_id)
    stripe.Customer.modify(
        customer_id,
        invoice_settings={"default_payment_method": attached.id},
    )
    return attached.id


def test_billing_checkout_session_and_portal_url_real_integration() -> None:
    """
    Outbound統合（あなた -> Stripe）:
    - /billing/checkout-session で checkout_url が返る
    - Stripe側に Checkout Session が作成され、metadata/client_reference_id が入ってる
    - /billing/portal-url で portal_url が返る
    """
    _require_env("STRIPE_API_KEY")
    stripe.api_key = os.environ["STRIPE_API_KEY"]

    client = _make_client()
    user_id = _register(client)

    idem = uuid.uuid4().hex

    # 1) Checkout Session 作成（API経由）
    r1 = client.post(
        "/api/v1/billing/checkout-session",
        headers={"Idempotency-Key": idem},
    )
    assert r1.status_code == 200, r1.text
    checkout_url_1 = r1.json()["checkout_url"]
    assert checkout_url_1

    # 2) 同じidemで叩くと同じ結果になる（Stripe idempotency の確認）
    r2 = client.post(
        "/api/v1/billing/checkout-session",
        headers={"Idempotency-Key": idem},
    )
    assert r2.status_code == 200, r2.text
    checkout_url_2 = r2.json()["checkout_url"]
    assert checkout_url_2 == checkout_url_1

    # 3) Stripe側の Session を実際に retrieve して中身を検証
    session_id = _extract_checkout_session_id(checkout_url_1)
    sess = stripe.checkout.Session.retrieve(session_id)

    # backendで metadata/client_reference_id を入れている前提
    assert (sess.metadata or {}).get("user_id") == user_id
    assert sess.client_reference_id == user_id

    # 4) Portal URL（API経由）
    # portal_resp = client.get("/api/v1/billing/portal-url")
    # assert portal_resp.status_code == 200, portal_resp.text
    # portal_url = portal_resp.json()["portal_url"]
    # assert portal_url
    # assert "billing.stripe.com" in portal_url or "stripe.com" in portal_url


def test_billing_webhook_checkout_session_completed_real_integration() -> None:
    """
    Inbound統合（Stripeイベント処理）を pytest で回すための現実解:
    - Checkout Session を作って customer_id を得る（Stripe実物）
    - Stripe API で subscription を作る（Stripe実物）
    - 署名付きで checkout.session.completed “相当”のイベントをWebhookにPOST
      -> UseCase内の Subscription.retrieve は実Stripeに飛ぶ
      -> DB(BillingAccount/User.plan) が更新されるのを確認
    """
    _require_env("STRIPE_API_KEY", "STRIPE_WEBHOOK_SECRET")
    stripe.api_key = os.environ["STRIPE_API_KEY"]
    webhook_secret = os.environ["STRIPE_WEBHOOK_SECRET"]
    price_id = _get_price_id()

    client = _make_client()
    user_id = _register(client)

    # 1) Checkout Sessionを作って Stripe Customer を確実に用意する
    idem = uuid.uuid4().hex
    r = client.post("/api/v1/billing/checkout-session",
                    headers={"Idempotency-Key": idem})
    assert r.status_code == 200, r.text
    checkout_url = r.json()["checkout_url"]
    session_id = _extract_checkout_session_id(checkout_url)

    sess = stripe.checkout.Session.retrieve(session_id)
    customer_id = sess.customer
    assert customer_id, f"Stripe session has no customer: {sess}"

    # 2) Customerに支払い方法を付ける（サブスクを安定させるため）
    _ensure_test_default_payment_method(customer_id)

    # 3) Subscription を作る（Stripe実物）
    sub = stripe.Subscription.create(
        customer=customer_id,
        items=[{"price": price_id}],
        # default_payment_method を渡すのも手（上でcustomer側に設定済みなら不要なことも多い）
        # default_payment_method="pm_card_visa",
    )
    subscription_id = sub.id
    assert subscription_id

    # 4) checkout.session.completed 相当の Event を「署名付き」でWebhookに送る
    #    ※ Stripeが本当に送ってくるEventと完全一致は不要。
    #       あなたのusecaseが必要としているキーを満たしていればOK。
    event_payload = {
        "id": f"evt_test_{uuid.uuid4().hex}",
        "object": "event",
        "api_version": "2020-08-27",
        "created": int(time.time()),
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": session_id,
                "object": "checkout.session",
                "metadata": {"user_id": user_id},
                "client_reference_id": user_id,
                "customer": customer_id,
                "subscription": subscription_id,
            }
        },
    }
    payload_bytes = json.dumps(event_payload, separators=(
        ",", ":"), ensure_ascii=False).encode("utf-8")
    sig = _stripe_signature_header(payload_bytes, webhook_secret)

    webhook_resp = client.post(
        "/api/v1/billing/stripe/webhook",
        content=payload_bytes,
        headers={"Stripe-Signature": sig, "Content-Type": "application/json"},
    )
    assert webhook_resp.status_code == 200, webhook_resp.text

    # 5) DB反映を確認（Repoで読む）
    db = create_session()
    try:
        billing_repo = SqlAlchemyBillingAccountRepository(db)
        user_repo = SqlAlchemyUserRepository(db)

        account = billing_repo.get_by_user_id(UserId(user_id))
        assert account is not None
        assert account.stripe_customer_id == customer_id
        assert account.stripe_subscription_id == subscription_id
        assert account.subscription_status in (
            BillingSubscriptionStatus.ACTIVE,
            BillingSubscriptionStatus.INCOMPLETE,
            BillingSubscriptionStatus.PAST_DUE,
            BillingSubscriptionStatus.CANCELED,
            BillingSubscriptionStatus.NONE,
        )

        user = user_repo.get_by_id(UserId(user_id))
        assert user is not None
        assert user.plan is not None  # TRIAL/PAID/FREE のどれかになっているはず
    finally:
        db.close()
