# デプロイメント作業チェックリスト

本番環境（Vercel + Railway + Cloudflare R2）へのデプロイ手順書

**作成日**: 2026-02-10
**対象環境**:
- フロントエンド: Vercel
- バックエンド: Railway
- データベース: Railway PostgreSQL
- ストレージ: Cloudflare R2

---

## 📋 デプロイ作業の全体像

```
Phase 1: コード修正（Git操作必要）
  ↓
Phase 2: 外部サービス準備（R2, Stripe等）
  ↓
Phase 3: Railway設定
  ↓
Phase 4: Vercel設定
  ↓
Phase 5: デプロイ＆動作確認
```

---

## Phase 1: コード修正とコミット 🔧

### 1-1. CORS設定の修正（必須）

**ファイル**: `/workspace/backend/app/main.py`

**修正箇所**: 57-60行目付近

```python
import os  # ファイル冒頭に追加（既にあればスキップ）

# 既存のCORS設定部分を以下に置き換え
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# 本番環境のフロントエンドURLを追加
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 1-2. Git操作

```bash
cd /workspace
git add backend/app/main.py
git commit -m "fix: add production CORS origin support for deployment"
git push origin feature/calendar-ui  # または main ブランチ
```

**確認事項**:
- [ ] main.pyが修正されている
- [ ] コミットが完了している
- [ ] リモートにプッシュされている

---

## Phase 2: 外部サービスの準備 ☁️

### 2-1. Cloudflare R2 バケット作成

1. Cloudflare ダッシュボードにログイン
2. R2 → バケット作成
3. バケット名: `nutrition-production`（任意）
4. API トークン作成
   - アクセスキーID: `<R2_ACCESS_KEY_ID>`
   - シークレットアクセスキー: `<R2_SECRET_ACCESS_KEY>`
   - アカウントID: `<ACCOUNT_ID>`

**メモしておく値**:
```
MINIO_ENDPOINT=<ACCOUNT_ID>.r2.cloudflarestorage.com
MINIO_ACCESS_KEY=<R2_ACCESS_KEY_ID>
MINIO_SECRET_KEY=<R2_SECRET_ACCESS_KEY>
```

### 2-2. Stripe API キー取得

1. Stripe ダッシュボードにログイン
2. 本番モードに切り替え
3. API キー取得:
   - `STRIPE_API_KEY` (sk_live_...)
   - `STRIPE_WEBHOOK_SECRET` (whsec_...)
   - `STRIPE_PRICE_ID` (price_...)

### 2-3. OpenAI API キー確認

- `OPENAI_API_KEY` (sk-...)

### 2-4. JWT Secret 生成

```bash
openssl rand -hex 32
```

**生成された値をメモ**: `JWT_SECRET_KEY=<生成された値>`

**確認事項**:
- [ ] R2バケット作成済み、認証情報取得済み
- [ ] Stripe本番APIキー取得済み
- [ ] OpenAI APIキー確認済み
- [ ] JWT Secretキー生成済み

---

## Phase 3: Railway設定 🚂

### 3-1. プロジェクト作成

1. Railway ダッシュボードにログイン
2. 新規プロジェクト作成
3. GitHub リポジトリを接続
4. ブランチ選択（main または feature/calendar-ui）

### 3-2. PostgreSQL プラグイン追加

1. プロジェクト内で "New" → "Database" → "PostgreSQL"
2. 自動的に `DATABASE_URL` が設定される

### 3-3. バックエンドサービス設定

**Root Directory**: `backend`

**Build Command**:
```bash
uv sync
```

**Start Command**:
```bash
bash -c "uv run alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port \$PORT"
```

### 3-4. 環境変数設定（Railway）

以下の環境変数を設定：

```bash
# ===== 基本設定 =====
ENV=production
USE_FAKE_INFRA=false

# ===== Database（PostgreSQLプラグインから自動設定） =====
DATABASE_URL=${{Postgres.DATABASE_URL}}

# ===== JWT（Phase 2で生成した値） =====
JWT_SECRET_KEY=<Phase2で生成した値>
ACCESS_TOKEN_TTL_MINUTES=15
REFRESH_TOKEN_TTL_DAYS=7

# ===== Cookie設定 =====
COOKIE_SECURE=true
COOKIE_SAMESITE=none

# ===== CORS（Vercel URLが決まってから設定） =====
FRONTEND_URL=https://your-app.vercel.app  # Phase 4で確定

# ===== OpenAI =====
OPENAI_API_KEY=<Phase2で確認した値>
USE_REAL_OPENAI=true
USE_OPENAI_DAILY_REPORT=true
USE_OPENAI_MEAL_RECOMMENDATION=true
USE_OPENAI_TARGET_GENERATION=true

# ===== Cloudflare R2（Phase 2で取得した値） =====
MINIO_ENDPOINT=<ACCOUNT_ID>.r2.cloudflarestorage.com
MINIO_ACCESS_KEY=<R2_ACCESS_KEY_ID>
MINIO_SECRET_KEY=<R2_SECRET_ACCESS_KEY>
MINIO_USE_SSL=true
MINIO_BUCKET_NAME=nutrition-production

# ===== Stripe（Phase 2で取得した値） =====
STRIPE_API_KEY=<sk_live_...>
STRIPE_WEBHOOK_SECRET=<whsec_...>
STRIPE_PRICE_ID=<price_...>
```

### 3-5. デプロイ実行

1. Railway が自動的にデプロイを開始
2. ログを確認してエラーがないか確認
3. デプロイ完了後、Railway のドメインをメモ
   - 例: `your-backend.up.railway.app`

**確認事項**:
- [ ] PostgreSQLプラグイン追加済み
- [ ] Build/Start Command設定済み
- [ ] すべての環境変数設定済み
- [ ] デプロイ成功
- [ ] Railway ドメイン取得済み

---

## Phase 4: Vercel設定 ▲

### 4-1. プロジェクト作成

1. Vercel ダッシュボードにログイン
2. 新規プロジェクト作成
3. GitHub リポジトリを接続

### 4-2. プロジェクト設定

**Root Directory**: `frontend`

**Framework Preset**: Next.js（自動検出）

**Build Command**: `pnpm build`（自動設定）

**Output Directory**: `.next`（自動設定）

**Install Command**: `pnpm install`（自動設定）

### 4-3. 環境変数設定（Vercel）

```bash
# ===== 基本設定 =====
NODE_ENV=production
NEXT_PUBLIC_USE_MOCK=false
NEXT_PUBLIC_API_MOCKING=disabled

# ===== API設定（BFF経由） =====
NEXT_PUBLIC_API_BASE_URL=/api
BACKEND_INTERNAL_ORIGIN=<Phase3のRailwayドメイン>
# 例: BACKEND_INTERNAL_ORIGIN=https://your-backend.up.railway.app
```

### 4-4. デプロイ実行

1. Vercel が自動的にデプロイを開始
2. デプロイ完了後、Vercel のドメインをメモ
   - 例: `your-app.vercel.app`

### 4-5. Railway の FRONTEND_URL を更新

**重要**: Vercel のドメインが確定したら、Railway に戻って環境変数を更新

1. Railway ダッシュボードを開く
2. 環境変数 `FRONTEND_URL` を更新
   ```bash
   FRONTEND_URL=https://your-app.vercel.app
   ```
3. Railway が自動的に再デプロイされる

**確認事項**:
- [ ] Vercel プロジェクト作成済み
- [ ] 環境変数設定済み
- [ ] デプロイ成功
- [ ] Vercel ドメイン取得済み
- [ ] Railway の FRONTEND_URL を更新済み
- [ ] Railway 再デプロイ完了

---

## Phase 5: デプロイ後の動作確認 ✅

### 5-1. バックエンドヘルスチェック

```bash
curl https://your-backend.up.railway.app/api/v1/health
# 期待される応答: {"status":"ok"}
```

### 5-2. フロントエンドアクセス確認

1. ブラウザで Vercel URL にアクセス
2. ログインページが表示されることを確認

### 5-3. 新規登録テスト

1. 新規ユーザー登録
2. プロフィール設定
3. 目標設定
4. ダッシュボード表示確認

### 5-4. API通信確認

ブラウザの開発者ツール（F12）で確認：
- [ ] CORS エラーがない
- [ ] Cookie が設定されている（ACCESS_TOKEN, REFRESH_TOKEN）
- [ ] API呼び出しが成功している（200番台のレスポンス）

### 5-5. 画像アップロード確認（R2）

1. プロフィール画像をアップロード
2. 正常に保存・表示されることを確認

### 5-6. AI機能確認

1. 目標生成（OpenAI）
2. 食事推薦（OpenAI）
3. 日次レポート生成（OpenAI）

**確認事項**:
- [ ] バックエンドヘルスチェック成功
- [ ] フロントエンドアクセス可能
- [ ] ユーザー登録〜ログインの動作確認
- [ ] CORSエラーなし
- [ ] 画像アップロード（R2）動作確認
- [ ] AI機能動作確認

---

## 📊 作業チェックリスト（全体サマリー）

### Phase 1: コード修正 ✏️
- [ ] main.py CORS設定修正
- [ ] Git commit & push

### Phase 2: 外部サービス準備 ☁️
- [ ] Cloudflare R2 バケット作成
- [ ] Stripe 本番APIキー取得
- [ ] OpenAI APIキー確認
- [ ] JWT Secret生成

### Phase 3: Railway設定 🚂
- [ ] プロジェクト作成
- [ ] PostgreSQL追加
- [ ] Build/Start Command設定
- [ ] 環境変数設定（15項目）
- [ ] デプロイ成功

### Phase 4: Vercel設定 ▲
- [ ] プロジェクト作成
- [ ] 環境変数設定（4項目）
- [ ] デプロイ成功
- [ ] Railway FRONTEND_URL更新

### Phase 5: 動作確認 ✅
- [ ] バックエンドヘルスチェック
- [ ] フロントエンド表示確認
- [ ] ユーザー登録・ログイン確認
- [ ] CORS確認
- [ ] R2画像アップロード確認
- [ ] AI機能確認

---

## 🚨 トラブルシューティング

### CORSエラーが出る場合
1. Railway の `FRONTEND_URL` が正しく設定されているか確認
2. Railway が再デプロイされているか確認
3. ブラウザのキャッシュをクリア
4. `main.py` のCORS設定が正しく修正されているか確認

### マイグレーションエラーが出る場合
```bash
# Railway コンソールで手動実行
railway run uv run alembic upgrade head
```

### Cookie が設定されない場合
1. `COOKIE_SECURE=true` が設定されているか確認
2. `COOKIE_SAMESITE=none` が設定されているか確認
3. HTTPS接続されているか確認（Railway/Vercelは自動的にHTTPS）

### R2接続エラーが出る場合
1. `MINIO_ENDPOINT` の形式確認: `<ACCOUNT_ID>.r2.cloudflarestorage.com`
2. `MINIO_USE_SSL=true` が設定されているか確認
3. R2のアクセスキー・シークレットキーが正しいか確認

### OpenAI APIエラーが出る場合
1. `OPENAI_API_KEY` が正しく設定されているか確認
2. OpenAI APIの利用制限・残高を確認
3. `USE_REAL_OPENAI=true` が設定されているか確認

---

## 📝 重要な注意事項

### セキュリティ
- [ ] JWT_SECRET_KEY は強力なランダム文字列を使用
- [ ] 本番環境の認証情報をGitにコミットしない
- [ ] 環境変数は各プラットフォームのシークレット管理機能を使用

### データベース
- [ ] 初回デプロイ時は自動マイグレーションが実行される
- [ ] データベースバックアップの設定を検討
- [ ] Railway PostgreSQL の料金プランを確認

### ストレージ
- [ ] R2のストレージ容量制限を確認
- [ ] R2の料金体系を確認（Freeプランの制限）

### コスト管理
- [ ] Vercel: Hobby（無料）/ Pro（$20/月）
- [ ] Railway: 利用量に応じた従量課金
- [ ] Cloudflare R2: 10GB/月まで無料
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

### バックアップ
- Railway PostgreSQL の定期バックアップ設定
- R2 に保存された画像のバックアップ戦略

---

## 📚 参考リンク

- [Railway Documentation](https://docs.railway.app/)
- [Vercel Documentation](https://vercel.com/docs)
- [Cloudflare R2 Documentation](https://developers.cloudflare.com/r2/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)

---

**最終更新**: 2026-02-10
