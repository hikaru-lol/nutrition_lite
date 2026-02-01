# Nutrition Tracker

## 概要

栄養管理アプリケーション。フロントエンド（Next.js 15）とバックエンド（FastAPI）のモノレポ構成。

## 技術スタック

### フロントエンド

- **フレームワーク**: Next.js 16, React 19, TypeScript 5
- **スタイリング**: TailwindCSS v4, Radix UI, shadcn/ui
- **状態管理**: TanStack React Query, react-hook-form
- **バリデーション**: Zod
- **API クライアント**: openapi-fetch, Axios
- **テスト**: MSW (Mock Service Worker)
- **パッケージマネージャ**: pnpm

### バックエンド

- **フレームワーク**: FastAPI, Uvicorn
- **ORM**: SQLAlchemy 2.0, Alembic (マイグレーション)
- **バリデーション**: Pydantic v2
- **認証**: JWT (python-jose), bcrypt
- **ストレージ**: MinIO (S3 互換)
- **AI**: OpenAI API
- **決済**: Stripe
- **パッケージマネージャ**: uv

## 開発時の参照ドキュメント

必要に応じて以下のファイルを参照してください

- アーキテクチャ: `docs/ai/clean-architecture.md`
- フロントエンド: `docs/ai/fsd-patterns.md`
- OpenAPI: `docs/ai/openapi-spec.md`

### インフラ

- **データベース**: PostgreSQL 16
- **オブジェクトストレージ**: MinIO
- **コンテナ**: Docker Compose (devcontainer)

## ディレクトリ構成

```
/workspace
├── frontend/          # Next.js アプリケーション
├── backend/           # FastAPI API サーバー
├── docs/              # ドキュメント (OpenAPI 仕様など)
├── .devcontainer/     # 開発コンテナ設定
└── .github/           # CI/CD ワークフロー
```

### フロントエンド構成 (Feature-Sliced Design)

```
frontend/src/
├── app/                # Next.js App Router
│   ├── (app)/         # 認証済みユーザー向けページ
│   ├── (onboarding)/  # オンボーディングフロー
│   ├── (public)/      # 公開ページ (ログイン等)
│   └── api/           # BFF API ルート (バックエンドへのプロキシ)
├── modules/           # 機能モジュール (ドメイン別)
│   ├── auth/          # 認証
│   ├── meal/          # 食事管理
│   ├── nutrition/     # 栄養トラッキング
│   ├── profile/       # ユーザープロフィール
│   ├── target/        # 栄養目標
│   └── today/         # 今日のサマリー
├── components/ui/     # 共通 UI コンポーネント (Radix UI)
└── shared/            # 共有ユーティリティ
```

### バックエンド構成 (Clean Architecture)

```
backend/app/
├── api/http/          # HTTP インターフェース (ルート、スキーマ)
├── application/       # ユースケース、DTO、ポート定義
├── domain/            # ビジネスロジック、ドメインエラー
├── infra/             # リポジトリ、セキュリティ、外部サービス
│   ├── db/           # SQLAlchemy モデル、リポジトリ
│   ├── security/     # JWT、パスワードハッシュ
│   ├── storage/      # MinIO/S3
│   └── llm/          # OpenAI 統合
└── di/                # 依存性注入コンテナ
```

@docs/ai/frontend-guidelines.md

## 共通ルール

- コミットメッセージは Conventional Commits 形式（feat:, fix:, docs:など）
- PR は日本語で記述
- 環境変数は各パッケージの `.env.local` / `.env` で管理

## よく使うコマンド

### フロントエンド

```bash
cd frontend
pnpm dev              # 開発サーバー起動 (localhost:3000)
pnpm build            # プロダクションビルド
pnpm lint             # ESLint 実行
```

### バックエンド

```bash
cd backend
uv sync                                    # 依存関係インストール
uv run uvicorn app.main:app --reload       # 開発サーバー起動 (localhost:8000)
uv run alembic upgrade head                # マイグレーション実行
uv run pytest -m "not real_integration" tests/unit/        # ユニットテスト
uv run pytest -m "not real_integration" tests/integration  # 統合テスト
uv run ruff check                          # Lint
uv run mypy app                            # 型チェック
```

### Docker (devcontainer)

```bash
# .devcontainer/docker-compose.dev.yml で以下のサービスが起動
# - dev: 開発コンテナ
# - db: PostgreSQL 16
# - minio: MinIO (S3 互換ストレージ)
```

## API 仕様

- **ベース URL**: `http://localhost:8000/api/v1`
- **OpenAPI ドキュメント**: `http://localhost:8000/docs`
- **OpenAPI 仕様**: `docs/openapi/openapi.yaml`

### 主要エンドポイント

| 機能         | エンドポイント                                           |
| ------------ | -------------------------------------------------------- |
| 認証         | `POST /auth/register`, `/login`, `/refresh`, `/logout`   |
| プロフィール | `GET /profile/me`, `POST /profile`, `PUT /profile`       |
| 目標         | `GET /targets`, `POST /targets`, `GET /targets/active`   |
| 食事         | `POST /meals`, `GET /meals/{date}`, `DELETE /meals/{id}` |
| 栄養         | `GET /nutrition/daily`, `GET /nutrition/summary`         |
| 課金         | `POST /billing/checkout`, `GET /billing/portal`          |

## 認証

- **方式**: Cookie ベースの JWT (AccessToken + RefreshToken)
- **トークン有効期限**: Access 15 分、Refresh 7 日
- **Cookie 設定**: HttpOnly, SameSite=Lax

## テスト

### バックエンド

- **ユニットテスト**: `tests/unit/` - フェイク実装を使用
- **統合テスト**: `tests/integration/` - フェイク or 実インフラ
- **実統合テスト**: `tests/integration_real/` - 実際の PostgreSQL, MinIO
- **マーカー**: `@pytest.mark.real_integration` で実インフラテストを区別

### フロントエンド

- **API モック**: MSW (Mock Service Worker) で開発時のモック

## 環境変数

### バックエンド主要設定

```bash
DATABASE_URL=postgresql+psycopg2://app:app@db:5432/app
JWT_SECRET_KEY=your-secret-key
USE_FAKE_INFRA=true           # true: インメモリ実装, false: 実インフラ
OPENAI_API_KEY=sk-...
STRIPE_API_KEY=sk_test_...
MINIO_ENDPOINT=minio:9000
```

### フロントエンド主要設定

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_USE_MOCK=true
NEXT_PUBLIC_API_MOCKING=enabled
```

## CI/CD

GitHub Actions で以下を実行:

- `backend-unit-tests.yml` - バックエンドユニットテスト
- `backend-integration-tests.yml` - バックエンド統合テスト
- `backend-real-integration.yml` - 実インフラ統合テスト (PostgreSQL, MinIO)
