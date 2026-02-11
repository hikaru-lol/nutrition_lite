# 環境変数設定一覧

本番環境デプロイ時に必要な環境変数の完全なリスト

**作成日**: 2026-02-10

---

## Railway（バックエンド）環境変数

### 基本設定

| 変数名 | 値 | 説明 |
|--------|-----|------|
| `ENV` | `production` | 環境名 |
| `USE_FAKE_INFRA` | `false` | 本番では実インフラを使用 |

### データベース

| 変数名 | 値 | 説明 |
|--------|-----|------|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` | PostgreSQL接続文字列（自動設定） |

### JWT認証

| 変数名 | 値 | 説明 |
|--------|-----|------|
| `JWT_SECRET_KEY` | `<openssl rand -hex 32で生成>` | JWT署名用シークレットキー |
| `ACCESS_TOKEN_TTL_MINUTES` | `15` | アクセストークンの有効期限（分） |
| `REFRESH_TOKEN_TTL_DAYS` | `7` | リフレッシュトークンの有効期限（日） |

### Cookie設定

| 変数名 | 値 | 説明 |
|--------|-----|------|
| `COOKIE_SECURE` | `true` | HTTPS必須にする |
| `COOKIE_SAMESITE` | `none` | クロスドメインCookie許可 |

### CORS設定

| 変数名 | 値 | 説明 |
|--------|-----|------|
| `FRONTEND_URL` | `https://your-app.vercel.app` | フロントエンドのURL（Vercel確定後に設定） |

### OpenAI

| 変数名 | 値 | 説明 |
|--------|-----|------|
| `OPENAI_API_KEY` | `sk-...` | OpenAI APIキー |
| `USE_REAL_OPENAI` | `true` | OpenAI使用フラグ |
| `USE_OPENAI_DAILY_REPORT` | `true` | 日次レポート生成にOpenAI使用 |
| `USE_OPENAI_MEAL_RECOMMENDATION` | `true` | 食事推薦にOpenAI使用 |
| `USE_OPENAI_TARGET_GENERATION` | `true` | 目標生成にOpenAI使用 |

### Cloudflare R2（ストレージ）

| 変数名 | 値 | 説明 |
|--------|-----|------|
| `MINIO_ENDPOINT` | `<ACCOUNT_ID>.r2.cloudflarestorage.com` | R2エンドポイント |
| `MINIO_ACCESS_KEY` | `<R2_ACCESS_KEY_ID>` | R2アクセスキーID |
| `MINIO_SECRET_KEY` | `<R2_SECRET_ACCESS_KEY>` | R2シークレットアクセスキー |
| `MINIO_USE_SSL` | `true` | SSL/TLS使用 |
| `MINIO_BUCKET_NAME` | `nutrition-production` | バケット名 |

### Stripe（決済）

| 変数名 | 値 | 説明 |
|--------|-----|------|
| `STRIPE_API_KEY` | `sk_live_...` | Stripe本番APIキー |
| `STRIPE_WEBHOOK_SECRET` | `whsec_...` | Webhook署名検証用シークレット |
| `STRIPE_PRICE_ID` | `price_...` | サブスクリプション価格ID |

---

## Vercel（フロントエンド）環境変数

### 基本設定

| 変数名 | 値 | 説明 |
|--------|-----|------|
| `NODE_ENV` | `production` | Node.js環境 |
| `NEXT_PUBLIC_USE_MOCK` | `false` | モックAPI無効化 |
| `NEXT_PUBLIC_API_MOCKING` | `disabled` | MSW無効化 |

### API設定（BFF経由）

| 変数名 | 値 | 説明 |
|--------|-----|------|
| `NEXT_PUBLIC_API_BASE_URL` | `/api` | クライアントサイドAPI呼び出しのベースURL |
| `BACKEND_INTERNAL_ORIGIN` | `https://your-backend.up.railway.app` | サーバーサイドからバックエンドへの接続URL |

---

## 環境変数設定テンプレート

### Railway用 .env テンプレート

```bash
# ===== 基本設定 =====
ENV=production
USE_FAKE_INFRA=false

# ===== Database =====
DATABASE_URL=${{Postgres.DATABASE_URL}}

# ===== JWT =====
JWT_SECRET_KEY=
ACCESS_TOKEN_TTL_MINUTES=15
REFRESH_TOKEN_TTL_DAYS=7

# ===== Cookie =====
COOKIE_SECURE=true
COOKIE_SAMESITE=none

# ===== CORS =====
FRONTEND_URL=

# ===== OpenAI =====
OPENAI_API_KEY=
USE_REAL_OPENAI=true
USE_OPENAI_DAILY_REPORT=true
USE_OPENAI_MEAL_RECOMMENDATION=true
USE_OPENAI_TARGET_GENERATION=true

# ===== Cloudflare R2 =====
MINIO_ENDPOINT=
MINIO_ACCESS_KEY=
MINIO_SECRET_KEY=
MINIO_USE_SSL=true
MINIO_BUCKET_NAME=nutrition-production

# ===== Stripe =====
STRIPE_API_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_PRICE_ID=
```

### Vercel用 .env テンプレート

```bash
# ===== 基本設定 =====
NODE_ENV=production
NEXT_PUBLIC_USE_MOCK=false
NEXT_PUBLIC_API_MOCKING=disabled

# ===== API設定 =====
NEXT_PUBLIC_API_BASE_URL=/api
BACKEND_INTERNAL_ORIGIN=
```

---

## 設定値の生成方法

### JWT_SECRET_KEY

強力なランダム文字列を生成：

```bash
openssl rand -hex 32
```

出力例: `a3f5b2c8d1e9f0a7b4c6d8e2f3a5b7c9d1e3f5a7b9c1d3e5f7a9b1c3d5e7f9a1`

### Cloudflare R2 認証情報

1. Cloudflare ダッシュボードにログイン
2. R2 → API トークン → トークン作成
3. 以下の値を取得：
   - アカウントID: `<ACCOUNT_ID>`
   - アクセスキーID: `<R2_ACCESS_KEY_ID>`
   - シークレットアクセスキー: `<R2_SECRET_ACCESS_KEY>`

エンドポイント形式: `<ACCOUNT_ID>.r2.cloudflarestorage.com`

### Stripe 認証情報

1. Stripe ダッシュボードにログイン
2. 本番モードに切り替え
3. API キー → 表示
   - シークレットキー: `sk_live_...`
4. Webhook → エンドポイント追加
   - URL: `https://your-backend.up.railway.app/api/v1/billing/webhook`
   - イベント選択: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`
   - 署名シークレット: `whsec_...`
5. 商品 → 価格ID取得: `price_...`

---

## セキュリティチェックリスト

- [ ] JWT_SECRET_KEY は32バイト以上のランダム文字列
- [ ] 本番環境の認証情報をGitリポジトリにコミットしていない
- [ ] `.env.local` / `.env` をGitignoreに追加済み
- [ ] RailwayとVercelの環境変数設定画面で直接入力
- [ ] APIキーに適切な権限のみを付与
- [ ] 不要なAPIキーは無効化・削除

---

## 環境変数の優先順位

### Railway

1. Railway ダッシュボードで設定した環境変数（最優先）
2. `.env` ファイル（開発環境のみ）

### Vercel

1. Vercel ダッシュボードで設定した環境変数（最優先）
2. `.env.production` ファイル
3. `.env.local` ファイル（開発環境のみ）
4. `.env` ファイル（開発環境のみ）

**重要**: 本番環境では必ずプラットフォームのダッシュボードで環境変数を設定してください。`.env`ファイルをGitにコミットしないでください。

---

## トラブルシューティング

### 環境変数が反映されない場合

**Railway**:
1. 環境変数を変更後、自動的に再デプロイされるまで待つ
2. 手動で再デプロイ: `Deployments` → `Redeploy`

**Vercel**:
1. 環境変数を変更後、再デプロイが必要
2. `Deployments` → 最新デプロイ → `Redeploy`

### DATABASE_URL の形式

Railway PostgreSQL プラグインが自動設定する形式:

```
postgresql+psycopg2://user:password@host:port/database
```

手動設定する場合は上記の形式を確認してください。

### MINIO_ENDPOINT の形式

**正しい形式**:
```
<ACCOUNT_ID>.r2.cloudflarestorage.com
```

**誤った形式**:
```
https://<ACCOUNT_ID>.r2.cloudflarestorage.com  # ❌ https:// は不要
<ACCOUNT_ID>.r2.cloudflarestorage.com:443      # ❌ ポート番号は不要
```

---

**最終更新**: 2026-02-10
