#!/usr/bin/env python
"""
開発環境用: テストサブスクリプションを手動で作成するスクリプト
"""
import os
import sys
sys.path.append('/workspace/backend')

from app.infra.db.base import SessionLocal
from app.infra.db.models.billing_account import BillingAccountModel
from app.infra.db.models.user import UserModel
from datetime import datetime, timezone
import stripe

# Stripe APIキーを環境変数から設定
stripe.api_key = os.getenv("STRIPE_API_KEY")
if not stripe.api_key:
    print("❌ Error: STRIPE_API_KEY environment variable is required")
    sys.exit(1)

def create_test_subscription(user_email: str):
    """指定されたユーザーにテスト用のサブスクリプションを作成"""

    session = SessionLocal()

    try:
        # ユーザーを検索
        user = session.query(UserModel).filter_by(email=user_email).first()
        if not user:
            print(f"❌ User not found: {user_email}")
            return

        print(f"✅ Found user: {user.id} ({user.email})")

        # BillingAccountを取得または作成
        account = session.query(BillingAccountModel).filter_by(user_id=user.id).first()

        if not account:
            print("Creating new billing account...")
            account = BillingAccountModel(
                user_id=user.id,
                updated_at=datetime.now(timezone.utc)
            )
            session.add(account)
            session.flush()

        # Stripe Customerが無い場合は作成
        if not account.stripe_customer_id:
            print("Creating Stripe customer...")
            customer = stripe.Customer.create(
                email=user.email,
                metadata={"user_id": str(user.id)}
            )
            account.stripe_customer_id = customer.id
            print(f"✅ Created customer: {customer.id}")

        # テスト用の支払い方法を作成・アタッチ（テストトークンを使用）
        print("Creating test payment method...")
        payment_method = stripe.PaymentMethod.create(
            type="card",
            card={"token": "tok_visa"}  # Stripeのテストトークンを使用
        )

        # 支払い方法をカスタマーにアタッチ
        stripe.PaymentMethod.attach(
            payment_method.id,
            customer=account.stripe_customer_id
        )

        # デフォルト支払い方法として設定
        stripe.Customer.modify(
            account.stripe_customer_id,
            invoice_settings={"default_payment_method": payment_method.id}
        )
        print(f"✅ Attached payment method: {payment_method.id}")

        # テスト用のサブスクリプションを作成
        if not account.stripe_subscription_id:
            print("Creating test subscription...")

            # テストモードで即座に有効になるサブスクリプションを作成
            subscription = stripe.Subscription.create(
                customer=account.stripe_customer_id,
                items=[{
                    "price": os.getenv("STRIPE_PRICE_ID", "price_1SKEzREtFPyGVVQrQObHjS89")
                }],
                default_payment_method=payment_method.id,
                trial_period_days=0,  # トライアルなし
                metadata={"user_id": str(user.id)}
            )

            account.stripe_subscription_id = subscription.id
            account.subscription_status = subscription.status
            account.current_plan = "paid"
            print(f"✅ Created subscription: {subscription.id} (status: {subscription.status})")
        else:
            print(f"ℹ️  Subscription already exists: {account.stripe_subscription_id}")

            # 既存のサブスクリプションのステータスを更新
            sub = stripe.Subscription.retrieve(account.stripe_subscription_id)
            account.subscription_status = sub.status
            if sub.status == "active":
                account.current_plan = "paid"
            print(f"   Status: {sub.status}")

        # ユーザーのプランも更新
        if account.subscription_status == "active":
            user.plan = "paid"
            print("✅ Updated user plan to: paid")

        account.updated_at = datetime.now(timezone.utc)
        session.commit()

        print("\n=== Summary ===")
        print(f"User ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Plan: {user.plan}")
        print(f"Customer ID: {account.stripe_customer_id}")
        print(f"Subscription ID: {account.stripe_subscription_id}")
        print(f"Subscription Status: {account.subscription_status}")

    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_test_subscription.py <user_email>")
        print("Example: python create_test_subscription.py test@example.com")
        sys.exit(1)

    user_email = sys.argv[1]
    create_test_subscription(user_email)