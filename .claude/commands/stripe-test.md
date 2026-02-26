---
description: Stripe決済機能のテスト環境をセットアップ
---

Stripe決済機能のテスト環境をセットアップしてください。

## 1. Stripe CLIの起動

```bash
# Webhook転送を開始
stripe listen --forward-to localhost:8000/api/v1/billing/stripe/webhook
```

生成された`Webhook signing secret`を環境変数に設定：
```bash
# backend/.env
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
```

## 2. テストカード情報

### 成功するカード
- カード番号: `4242 4242 4242 4242`
- 有効期限: 任意の未来の日付
- CVC: 任意の3桁
- 郵便番号: 任意の5桁

### 失敗するカード
- 残高不足: `4000 0000 0000 9995`
- カード拒否: `4000 0000 0000 0002`
- 有効期限切れ: `4000 0000 0000 0069`

## 3. サブスクリプションのテストフロー

### 新規登録
1. `/billing/plan`ページにアクセス
2. プラン（月額/年額）を選択
3. 「購読を開始」をクリック
4. Stripe Checkoutでテストカードを入力
5. 成功後`/billing/success`にリダイレクト

### 管理ポータル
1. `/billing/plan`ページの「プランを管理」をクリック
2. Stripe Customer Portalが開く
3. プラン変更、キャンセル、支払い方法変更が可能

## 4. Webhookイベントのテスト

### イベント送信（Stripe CLI）
```bash
# サブスクリプション作成
stripe trigger customer.subscription.created

# サブスクリプション更新
stripe trigger customer.subscription.updated

# サブスクリプション削除
stripe trigger customer.subscription.deleted

# 支払い成功
stripe trigger payment_intent.succeeded
```

### ログ確認
```bash
# バックエンドログ
tail -f backend/logs/app.log

# Stripe CLIログ
# stripe listen実行中のターミナルで確認
```

## 5. テストシナリオ

### シナリオ1: 新規購読
1. デモアカウントでログイン
2. プラン選択
3. Checkout完了
4. DBでsubscription確認

### シナリオ2: プラン変更
1. Customer Portalでプラン変更
2. Webhookイベント受信確認
3. DBの更新確認

### シナリオ3: キャンセル
1. Customer Portalでキャンセル
2. 期限まで有効を確認
3. 期限後に無効化を確認

## 6. トラブルシューティング

### Webhookが届かない
- Stripe CLIが起動しているか確認
- STRIPE_WEBHOOK_SECRETが正しいか確認
- ファイアウォール/プロキシの設定確認

### Checkoutが開かない
- STRIPE_API_KEYが設定されているか確認
- Price IDが正しいか確認
- フロントエンド環境変数の確認

### 環境変数の確認
```bash
# バックエンド
cat backend/.env | grep STRIPE

# 必要な環境変数
STRIPE_API_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_PRICE_ID_MONTHLY=price_xxx
STRIPE_PRICE_ID_YEARLY=price_xxx
```

$ARGUMENTS