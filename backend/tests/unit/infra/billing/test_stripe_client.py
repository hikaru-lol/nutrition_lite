from types import SimpleNamespace
from pytest_mock import MockerFixture
import pytest

from app.infra.billing.stripe_client import StripeClient


@pytest.fixture
def restore_stripe_api_key():
    import stripe
    old = getattr(stripe, "api_key", None)
    yield
    stripe.api_key = old


def test_init_sets_api_key(restore_stripe_api_key):
    import stripe
    c = StripeClient(api_key="sk_test_x", webhook_secret="whsec_x")
    assert stripe.api_key == "sk_test_x"


def test_create_customer_calls_stripe(mocker: MockerFixture, restore_stripe_api_key):
    # ★ StripeClient のあるモジュールの stripe をパッチするのがコツ
    mock_create = mocker.patch(
        "app.infra.billing.stripe_client.stripe.Customer.create",
        return_value=SimpleNamespace(id="cus_123")
    )

    client = StripeClient(api_key="sk_test_x", webhook_secret="whsec_x")
    out = client.create_customer(
        email="a@example.com",
        user_id="user_1",
        idempotency_key="idem_1",
    )

    assert out == "cus_123"
    mock_create.assert_called_once_with(
        email="a@example.com",
        metadata={"user_id": "user_1"},
        idempotency_key="idem_1",
    )


def test_create_checkout_session_calls_stripe(mocker: MockerFixture, restore_stripe_api_key):
    mock_create = mocker.patch(
        "app.infra.billing.stripe_client.stripe.checkout.Session.create",
        return_value=SimpleNamespace(url="https://checkout.stripe.test/s/abc"),
    )

    client = StripeClient(api_key="sk_test_x", webhook_secret="whsec_x")
    out = client.create_checkout_session(
        customer_id="cus_123",
        price_id="price_123",
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel",
        user_id="user_1",
        idempotency_key="idem_2",
    )

    assert out == "https://checkout.stripe.test/s/abc"
    mock_create.assert_called_once_with(
        mode="subscription",
        customer="cus_123",
        line_items=[{"price": "price_123", "quantity": 1}],
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel",
        metadata={"user_id": "user_1"},
        client_reference_id="user_1",
        idempotency_key="idem_2",
    )


def test_create_billing_portal_session_calls_stripe(mocker: MockerFixture, restore_stripe_api_key):
    mock_create = mocker.patch(
        "app.infra.billing.stripe_client.stripe.billing_portal.Session.create",
        return_value=SimpleNamespace(url="https://billing.stripe.test/p/xyz"),
    )

    client = StripeClient(api_key="sk_test_x", webhook_secret="whsec_x")
    out = client.create_billing_portal_session(
        customer_id="cus_123",
        return_url="https://example.com/return",
    )

    assert out == "https://billing.stripe.test/p/xyz"
    mock_create.assert_called_once_with(
        customer="cus_123",
        return_url="https://example.com/return",
    )


def test_construct_event_passes_secret(mocker: MockerFixture, restore_stripe_api_key):
    mock_construct = mocker.patch(
        "app.infra.billing.stripe_client.stripe.Webhook.construct_event",
        return_value={"id": "evt_123"},
    )

    client = StripeClient(api_key="sk_test_x", webhook_secret="whsec_TEST")
    payload = b'{"type":"ping"}'
    sig = "t=123,v1=abc"  # 中身はこのテストでは重要でない（モックなので）

    evt = client.construct_event(payload=payload, sig_header=sig)
    assert evt == {"id": "evt_123"}

    mock_construct.assert_called_once_with(
        payload=payload,
        sig_header=sig,
        secret="whsec_TEST",
    )


def test_retrieve_subscription(mocker: MockerFixture, restore_stripe_api_key):
    mock_retrieve = mocker.patch(
        "app.infra.billing.stripe_client.stripe.Subscription.retrieve",
        return_value=SimpleNamespace(id="sub_123", status="active"),
    )

    client = StripeClient(api_key="sk_test_x", webhook_secret="whsec_x")
    info = client.retrieve_subscription("sub_123")

    assert info.id == "sub_123"
    assert info.status == "active"
    mock_retrieve.assert_called_once_with("sub_123")
