"""
Stripe webhook処理のテスト
"""
import json
import pytest
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient
from stripe import error as stripe_error
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_stripe_webhook_event():
    """モックのStripe webhook event"""
    return {
        "id": "evt_test_webhook",
        "object": "event",
        "type": "customer.subscription.updated",
        "data": {
            "object": {
                "id": "sub_test123",
                "status": "active",
                "customer": "cus_test123",
                "metadata": {
                    "user_id": "user123"
                }
            }
        }
    }


class TestBillingWebhook:
    """課金webhook関連のテスト"""

    @patch('app.infra.billing.stripe_client.stripe.Webhook.construct_event')
    def test_webhook_subscription_updated_success(
        self, mock_construct_event, client, mock_stripe_webhook_event
    ):
        """サブスクリプション更新webhookが正常に処理されること"""
        # モックの設定
        mock_construct_event.return_value = mock_stripe_webhook_event

        # テスト実行
        response = client.post(
            "/api/v1/billing/stripe/webhook",
            headers={
                "stripe-signature": "test_signature",
                "content-type": "application/json"
            },
            content=json.dumps(mock_stripe_webhook_event).encode()
        )

        # 検証
        assert response.status_code == 200
        mock_construct_event.assert_called_once()

    @patch('app.infra.billing.stripe_client.stripe.Webhook.construct_event')
    def test_webhook_invalid_signature(self, mock_construct_event, client):
        """不正なシグネチャでwebhookが拒否されること"""
        # モックで正しいStripeエラーを発生させる
        mock_construct_event.side_effect = stripe_error.SignatureVerificationError(
            "Invalid signature", "test_sig_header"
        )

        # テスト実行
        response = client.post(
            "/api/v1/billing/stripe/webhook",
            headers={
                "stripe-signature": "invalid_signature",
                "content-type": "application/json"
            },
            content=b'{"test": "data"}'
        )

        # 検証
        assert response.status_code == 400

    def test_webhook_missing_signature(self, client):
        """シグネチャなしでwebhookが拒否されること"""
        response = client.post(
            "/api/v1/billing/stripe/webhook",
            headers={"content-type": "application/json"},
            content=b'{"test": "data"}'
        )

        # 検証
        assert response.status_code == 400