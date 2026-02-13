# 🚀 デプロイ作業タスクリスト（ストレージなし版）

**作成日**: 2026-02-11
**対象環境**: Vercel (Frontend) + Railway (Backend) + PostgreSQL
**特記事項**: Cloudflare R2なし（USE_FAKE_INFRA=true使用）

---

## Phase 1: コード修正 ✅ 完了

- [x] CORS設定（main.py）

---

## Phase 2: 外部サービス準備

### 2-1. JWT Secret生成（必須）

```bash
openssl rand -hex 32
```

**結果をメモ**: `JWT_SECRET_KEY=<生成された値>`

### 2-2. OpenAI APIキー確認（必須）

- 既存のAPIキーを確認
- または https://platform.openai.com/api-keys で新規作成

**結果をメモ**: `OPENAI_API_KEY=sk-...`

### 2-3. Stripe設定（必須）

1. Stripe ダッシュボードにログイン
2. 本番モードに切り替え
3. API キー取得:
   - `STRIPE_API_KEY` (sk_live_...)
   - `STRIPE_PRICE_ID` (price_...)
4. Webhook設定（後ほど、Railwayデプロイ後）
5. Checkout成功/キャンセルURL、ポータル戻りURLは Phase 4 で確定後に設定

### ~~2-4. Cloudflare R2~~

- ❌ **スキップ**（`USE_FAKE_INFRA=true` 使用）
- プロフィール画像はインメモリで動作
- アプリ再起動で画像は消える（MVP段階はこれで問題なし）

---

## Phase 3: Railway設定（バックエンド）

### 3-1. プロジェクト作成

1. Railway ダッシュボードにログイン (https://railway.app)
2. 新規プロジェクト作成
3. GitHubリポジトリを接続
4. ブランチ選択（**main**）

### 3-2. PostgreSQL追加

1. プロジェクト内で "New" → "Database" → "PostgreSQL"
2. 自動的に `DATABASE_URL` が設定される

### 3-3. ビルド・起動設定

- **Root Directory**: `backend`
- **Build Command**: `uv sync`
- **Start Command**:
  ```bash
  bash -c "uv run alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
  ```

### 3-4. 環境変数設定（Railway）

以下の環境変数をRailwayダッシュボードで設定：

```bash
# === 基本設定 ===
ENV=production
USE_FAKE_INFRA=true

# === Database（PostgreSQLプラグインから自動設定） ===
DATABASE_URL=${{Postgres.DATABASE_URL}}

# === JWT（Phase 2で生成） ===
JWT_SECRET_KEY=<Phase2で生成した値>
ACCESS_TOKEN_TTL_MINUTES=15
REFRESH_TOKEN_TTL_DAYS=7

# === Cookie設定 ===
COOKIE_SECURE=true
COOKIE_SAMESITE=none

# === CORS（Vercel URLが決まってから設定） ===
FRONTEND_URL=https://your-app.vercel.app  # Phase 4で確定後に更新

# === OpenAI ===
OPENAI_API_KEY=<Phase2で確認した値>
USE_OPENAI_TARGET_GENERATOR=true
USE_OPENAI_NUTRITION_ESTIMATOR=true
USE_OPENAI_DAILY_REPORT_GENERATOR=true
USE_OPENAI_MEAL_RECOMMENDATION_GENERATOR=true

# === 食事推薦レート制限（任意） ===
MEAL_RECOMMENDATION_COOLDOWN_MINUTES=30
MEAL_RECOMMENDATION_DAILY_LIMIT=5

# === Stripe ===
STRIPE_API_KEY=<Phase2で取得した値>
STRIPE_WEBHOOK_SECRET=<後で設定、Phase5で更新>
STRIPE_PRICE_ID=<Phase2で取得した値>
STRIPE_CHECKOUT_SUCCESS_URL=https://your-app.vercel.app/billing/success  # Phase 4で確定後に更新
STRIPE_CHECKOUT_CANCEL_URL=https://your-app.vercel.app/billing/cancel    # Phase 4で確定後に更新
STRIPE_PORTAL_RETURN_URL=https://your-app.vercel.app/settings            # Phase 4で確定後に更新
```

**環境変数数**: 20項目

### 3-5. デプロイ実行

1. Railway が自動的にデプロイ開始
2. ログを確認してエラーがないか確認
3. デプロイ完了後、Railway ドメインをメモ
   - 例: `nutrition-backend-production.up.railway.app`

**確認事項**:
- [ ] ビルドが成功している
- [ ] マイグレーションが実行されている
- [ ] アプリが起動している

---

## Phase 4: Vercel設定（フロントエンド）

### 4-1. プロジェクト作成

1. Vercel ダッシュボードにログイン (https://vercel.com)
2. 新規プロジェクト作成
3. GitHubリポジトリを接続

### 4-2. プロジェクト設定

- **Root Directory**: `frontend`
- **Framework Preset**: Next.js（自動検出）
- **Build Command**: `pnpm build`（自動設定）
- **Output Directory**: `.next`（自動設定）
- **Install Command**: `pnpm install`（自動設定）

### 4-3. 環境変数設定（Vercel）

以下の環境変数をVercelダッシュボードで設定：

```bash
# === 基本設定 ===
NODE_ENV=production
NEXT_PUBLIC_USE_MOCK=false
NEXT_PUBLIC_API_MOCKING=disabled

# === API設定（BFF経由） ===
NEXT_PUBLIC_API_BASE_URL=/api
BACKEND_INTERNAL_ORIGIN=<Phase3のRailwayドメイン>
# 例: https://nutrition-backend-production.up.railway.app
```

**環境変数数**: 4項目

### 4-4. デプロイ実行

1. Vercel が自動的にデプロイ開始
2. デプロイ完了後、Vercel ドメインをメモ
   - 例: `nutrition-app.vercel.app`

**確認事項**:
- [ ] ビルドが成功している
- [ ] デプロイが完了している
- [ ] ドメインが有効になっている

### 4-5. Railway の環境変数を更新

**重要**: Vercel のドメインが確定したら、Railway に戻って環境変数を更新

1. Railway ダッシュボードを開く
2. 以下の環境変数を更新:
   ```bash
   FRONTEND_URL=https://nutrition-app.vercel.app
   STRIPE_CHECKOUT_SUCCESS_URL=https://nutrition-app.vercel.app/billing/success
   STRIPE_CHECKOUT_CANCEL_URL=https://nutrition-app.vercel.app/billing/cancel
   STRIPE_PORTAL_RETURN_URL=https://nutrition-app.vercel.app/settings
   ```
3. Railway が自動的に再デプロイされる

---

## Phase 5: デプロイ後の動作確認

### 5-1. バックエンドヘルスチェック

```bash
curl https://nutrition-backend-production.up.railway.app/api/v1/health
```

**期待される応答**:
```json
{"status":"ok"}
```

### 5-2. フロントエンドアクセス確認

1. ブラウザで Vercel URL にアクセス
2. ログインページが表示されることを確認

### 5-3. 新規登録・ログインテスト

1. 新規ユーザー登録
2. プロフィール設定
3. 目標設定
4. ダッシュボード表示確認

### 5-4. API通信・CORS確認

ブラウザの開発者ツール（F12）で確認：

- [ ] CORSエラーがない
- [ ] Cookieが設定されている（ACCESS_TOKEN, REFRESH_TOKEN）
- [ ] API呼び出しが成功している（200番台のレスポンス）

### 5-5. AI機能確認（オプション）

1. 目標生成（OpenAI）
2. 食事推薦（OpenAI）
3. 日次レポート生成（OpenAI）

### 5-6. Stripe Webhook設定

1. Stripe ダッシュボード → Webhook
2. エンドポイント追加:
   - **URL**: `https://nutrition-backend-production.up.railway.app/api/v1/billing/webhook`
   - **イベント選択**:
     - `checkout.session.completed`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
3. 署名シークレットを取得: `whsec_...`
4. Railway の環境変数 `STRIPE_WEBHOOK_SECRET` を更新
5. Railway が自動的に再デプロイ

---

## 📊 チェックリスト

### Phase 2: 外部サービス準備
- [ ] JWT Secret生成
- [ ] OpenAI APIキー確認
- [ ] Stripe APIキー取得（sk_live_...）
- [ ] Stripe 価格ID取得（price_...）

### Phase 3: Railway設定
- [ ] プロジェクト作成
- [ ] PostgreSQL追加
- [ ] Root Directory設定（backend）
- [ ] Build Command設定（uv sync）
- [ ] Start Command設定（alembic + uvicorn）
- [ ] 環境変数設定（20項目）
- [ ] デプロイ成功
- [ ] Railway ドメイン取得

### Phase 4: Vercel設定
- [ ] プロジェクト作成
- [ ] Root Directory設定（frontend）
- [ ] 環境変数設定（4項目）
- [ ] デプロイ成功
- [ ] Vercel ドメイン取得
- [ ] Railway FRONTEND_URL + Stripe URL更新

### Phase 5: 動作確認
- [ ] バックエンドヘルスチェック
- [ ] フロントエンド表示確認
- [ ] ユーザー登録・ログイン確認
- [ ] CORS確認
- [ ] AI機能確認（オプション）
- [ ] Stripe Webhook設定

---

## 🚨 トラブルシューティング

### CORSエラーが出る場合

1. Railway の `FRONTEND_URL` が正しく設定されているか確認
2. Railway が再デプロイされているか確認
3. ブラウザのキャッシュをクリア

### マイグレーションエラーが出る場合

```bash
# Railway コンソールで手動実行
railway run uv run alembic upgrade head
```

### Cookie が設定されない場合

1. `COOKIE_SECURE=true` が設定されているか確認
2. `COOKIE_SAMESITE=none` が設定されているか確認
3. HTTPS接続されているか確認（Railway/Vercelは自動的にHTTPS）

### Vercel ビルドエラーが出る場合

1. `BACKEND_INTERNAL_ORIGIN` が正しく設定されているか確認
2. Vercel のビルドログを確認
3. `pnpm install` が成功しているか確認

---

## 📝 重要な注意事項

### セキュリティ

- [ ] JWT_SECRET_KEY は強力なランダム文字列を使用（32バイト以上）
- [ ] 本番環境の認証情報をGitにコミットしない
- [ ] 環境変数は各プラットフォームのシークレット管理機能を使用

### データベース

- [ ] 初回デプロイ時は自動マイグレーションが実行される
- [ ] データベースバックアップの設定を検討
- [ ] Railway PostgreSQL の料金プランを確認

### ストレージ（インメモリ使用）

- [ ] プロフィール画像はアプリ再起動で消える
- [ ] 本番運用時は後でCloudflare R2に移行を検討
- [ ] 複数インスタンスでデータ共有不可（Railway は通常1インスタンス）

### コスト管理

- [ ] Vercel: Hobby（無料）/ Pro（$20/月）
- [ ] Railway: 利用量に応じた従量課金（$5クレジット/月）
- [ ] OpenAI API: 使用量に応じた課金
- [ ] Stripe: トランザクション手数料

---

## 🔄 デプロイ後のメンテナンス

### 継続的デプロイ

- GitHub へのプッシュで自動デプロイ（Vercel, Railway 両方）
- main ブランチへのマージで本番環境に反映

### モニタリング

- Railway: ログとメトリクスの確認
- Vercel: Analytics とログの確認
- Sentry等のエラートラッキングツールの導入を検討

### 将来の拡張

- Cloudflare R2の追加（画像ストレージ）
- カスタムドメインの設定
- CDNの設定（Vercelは自動）
- データベースのスケーリング

---

**最終更新**: 2026-02-11
