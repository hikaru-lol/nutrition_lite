# プロジェクト構成ドキュメント

## 概要

栄養管理アプリケーションのフルスタックプロジェクトです。バックエンドは FastAPI、フロントエンドは Next.js で構築されています。クリーンアーキテクチャの原則に基づいた設計で、認証、食事記録、栄養計算、レポート生成、ターゲット管理、課金処理などの機能を提供します。

---

## ディレクトリ構造

```
/workspace
├── .devcontainer/          # 開発環境設定（Docker）
├── .github/                # GitHub Actions CI/CD設定
│   └── workflows/
├── backend/                # バックエンド（FastAPI + Python）
├── frontend/               # フロントエンド（Next.js + TypeScript）
├── docs/                   # プロジェクトドキュメント
│   ├── structure/          # 構成ドキュメント
│   ├── workflow/           # 運用ドキュメント
│   ├── openapi/            # OpenAPI仕様
│   └── 要件&仕様/          # 機能要件・仕様書
├── scripts/                # 補助スクリプト
└── README.md               # プロジェクトルートREADME
```

---

## バックエンド構成 (`/backend`)

### アーキテクチャ

クリーンアーキテクチャの原則に基づき、以下のレイヤーで構成されています：

```
┌─────────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                        │
│  routers/ → schemas/ → dependencies/                            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Application Layer                            │
│  use_cases/ → dto/ → ports/                                     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Domain Layer                             │
│  entities/ → value_objects/ → errors/                           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                         │
│  db/ → llm/ → security/ → storage/ → billing/                   │
└─────────────────────────────────────────────────────────────────┘
```

### ディレクトリ構造

```
backend/
├── app/
│   ├── api/
│   │   └── http/
│   │       ├── routers/           # FastAPI ルーター（7ルーター）
│   │       │   ├── auth_route.py
│   │       │   ├── profile_route.py
│   │       │   ├── target_route.py
│   │       │   ├── meal_route.py
│   │       │   ├── nutrition_route.py
│   │       │   ├── daily_report_route.py
│   │       │   └── billing_route.py
│   │       ├── schemas/           # Pydantic スキーマ
│   │       ├── dependencies/      # 依存性注入（認証等）
│   │       ├── mappers/           # DTOマッパー
│   │       ├── cookies.py         # Cookie処理
│   │       └── errors.py          # エラーハンドリング
│   │
│   ├── application/               # ユースケース層
│   │   ├── auth/
│   │   │   ├── use_cases/
│   │   │   │   ├── account/       # register_user, delete_account
│   │   │   │   ├── session/       # login, logout, refresh
│   │   │   │   └── current_user/  # get_current_user
│   │   │   ├── ports/             # インターフェース定義
│   │   │   └── dto/               # データ転送オブジェクト
│   │   ├── profile/
│   │   │   ├── use_cases/         # get_my_profile, upsert_profile
│   │   │   ├── ports/
│   │   │   └── dto/
│   │   ├── target/
│   │   │   ├── use_cases/         # CRUD, activate, generate
│   │   │   ├── ports/
│   │   │   └── dto/
│   │   ├── meal/
│   │   │   ├── use_cases/         # CRUD, check_daily_completion
│   │   │   ├── ports/
│   │   │   └── dto/
│   │   ├── nutrition/
│   │   │   ├── use_cases/         # compute, generate_report, recommend
│   │   │   ├── ports/
│   │   │   └── dto/
│   │   ├── billing/
│   │   │   ├── use_cases/         # checkout, portal, webhook
│   │   │   └── ports/
│   │   └── common/
│   │       └── ports/             # 共通インターフェース
│   │
│   ├── domain/                    # ドメイン層
│   │   ├── auth/
│   │   │   ├── entities.py        # User
│   │   │   ├── value_objects.py   # TokenPair, Credentials
│   │   │   └── errors.py
│   │   ├── profile/
│   │   │   ├── entities.py        # Profile
│   │   │   ├── value_objects.py
│   │   │   └── errors.py
│   │   ├── target/
│   │   │   ├── entities.py        # Target, TargetNutrient
│   │   │   ├── value_objects.py
│   │   │   └── errors.py
│   │   ├── meal/
│   │   │   ├── entities.py        # FoodEntry
│   │   │   ├── value_objects.py   # MealType, Amount
│   │   │   └── errors.py
│   │   ├── nutrition/
│   │   │   ├── daily_nutrition.py
│   │   │   ├── meal_nutrition.py
│   │   │   ├── daily_report.py
│   │   │   ├── meal_recommendation.py
│   │   │   └── errors.py
│   │   └── billing/
│   │       ├── entities.py        # BillingAccount
│   │       └── errors.py
│   │
│   ├── infra/                     # インフラ層
│   │   ├── db/
│   │   │   ├── models/            # SQLAlchemy モデル（14テーブル）
│   │   │   ├── repositories/      # リポジトリ実装（10リポジトリ）
│   │   │   ├── uow/               # Unit of Work 実装
│   │   │   ├── session.py         # DBセッション管理
│   │   │   └── base.py            # SQLAlchemy Base
│   │   ├── security/
│   │   │   ├── jwt_token_service.py
│   │   │   └── password_hasher.py
│   │   ├── llm/
│   │   │   ├── estimator_openai.py           # 栄養推定
│   │   │   ├── daily_report_generator_openai.py
│   │   │   ├── meal_recommendation_generator_openai.py
│   │   │   ├── target_generator_openai.py
│   │   │   └── stub_*.py                     # スタブ実装
│   │   ├── storage/
│   │   │   └── minio_profile_image_storage.py
│   │   ├── billing/
│   │   │   └── stripe_client.py
│   │   ├── auth/
│   │   │   └── plan_checker_service.py
│   │   ├── meal/
│   │   │   └── meal_entry_query_service.py
│   │   ├── profile/
│   │   │   └── profile_query_service.py
│   │   ├── nutrition/
│   │   │   └── estimator_stub.py
│   │   └── time/
│   │       └── system_clock.py
│   │
│   ├── di/
│   │   └── container.py           # 依存性注入コンテナ
│   │
│   ├── jobs/
│   │   └── generate_meal_recommendations.py
│   │
│   ├── main.py                    # FastAPI エントリーポイント
│   └── settings.py                # 環境変数・設定
│
├── alembic/                       # DBマイグレーション
├── tests/
│   ├── unit/                      # ユニットテスト（53ファイル）
│   │   ├── application/
│   │   └── infra/
│   ├── integration/               # 統合テスト
│   ├── integration_real/          # 実インフラ統合テスト
│   └── fakes/                     # テスト用フェイク実装
└── pyproject.toml                 # 依存関係定義
```

### データベーステーブル一覧（14テーブル）

| テーブル名 | 説明 |
|-----------|------|
| `users` | ユーザー基本情報（plan, trial_ends_at等） |
| `profiles` | プロフィール（1:1 with users） |
| `billing_accounts` | Stripe連携情報（1:1 with users） |
| `targets` | 栄養目標 |
| `target_nutrients` | 目標栄養素（1:N with targets） |
| `daily_target_snapshots` | 日次目標スナップショット |
| `daily_target_snapshot_nutrients` | スナップショット栄養素 |
| `food_entries` | 食事ログ（ソフトデリート対応） |
| `meal_nutrition_summaries` | 食事栄養サマリ |
| `meal_nutrition_nutrients` | 食事栄養素 |
| `meal_recommendations` | 食事推奨（AI生成） |
| `daily_nutrition_summaries` | 日次栄養サマリ |
| `daily_nutrition_nutrients` | 日次栄養素 |
| `daily_nutrition_reports` | 日次レポート（AI生成） |

---

## フロントエンド構成 (`/frontend`)

### 技術スタック

| カテゴリ | 技術 | バージョン |
|---------|-----|-----------|
| フレームワーク | Next.js | 16.0.7 |
| UIライブラリ | React | 19.2.0 |
| 言語 | TypeScript | 5.x |
| 状態管理 | TanStack Query | 5.90.16 |
| スタイリング | Tailwind CSS | 4.x |
| UIコンポーネント | Radix UI | - |
| チャート | Recharts | 3.5.1 |
| フォーム | React Hook Form + Zod | - |
| パッケージ管理 | pnpm | - |

### ディレクトリ構造

```
frontend/
├── src/
│   ├── app/                           # Next.js App Router
│   │   ├── (app)/                     # 認証済みルート
│   │   │   ├── layout.tsx             # 認証済みレイアウト
│   │   │   ├── billing/
│   │   │   │   └── plan/page.tsx
│   │   │   └── meals/                 # 食事記録（予定）
│   │   │
│   │   ├── (onboarding)/              # オンボーディング
│   │   │   ├── layout.tsx
│   │   │   └── target/page.tsx        # ターゲット設定
│   │   │
│   │   ├── (public)/                  # 公開ルート
│   │   │   └── auth/
│   │   │       ├── layout.tsx
│   │   │       ├── login/page.tsx
│   │   │       └── register/page.tsx
│   │   │
│   │   ├── api/                       # API Routes (BFF)
│   │   │   ├── auth/[...path]/route.ts
│   │   │   └── target/route.ts
│   │   │
│   │   ├── layout.tsx                 # ルートレイアウト
│   │   ├── providers.tsx              # React Providers
│   │   └── globals.css                # グローバルスタイル
│   │
│   ├── modules/                       # 機能モジュール（Feature Sliced Design）
│   │   ├── auth/
│   │   │   ├── api/
│   │   │   │   ├── authClient.ts      # クライアント側API
│   │   │   │   └── authServer.ts      # サーバー側API
│   │   │   ├── model/
│   │   │   │   ├── schema.ts          # Zod スキーマ
│   │   │   │   ├── useLoginPageModel.ts
│   │   │   │   └── useRegisterPageModel.ts
│   │   │   ├── ui/
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   └── RegisterForm.tsx
│   │   │   ├── server.ts              # Server Actions
│   │   │   └── index.ts               # Public API
│   │   │
│   │   ├── target/
│   │   │   ├── api/
│   │   │   │   └── targetClient.ts
│   │   │   ├── contract/
│   │   │   │   └── targetContract.ts  # API契約定義
│   │   │   ├── model/
│   │   │   │   └── useTargetGeneratorPageModel.ts
│   │   │   ├── ui/
│   │   │   │   └── TargetGeneratorPage.tsx
│   │   │   └── index.ts
│   │   │
│   │   ├── today/
│   │   │   ├── hooks/
│   │   │   │   └── useToday.ts
│   │   │   ├── infra/
│   │   │   │   └── api.ts
│   │   │   └── ui/
│   │   │       └── NutritionSummary.tsx
│   │   │
│   │   ├── meals/                     # 食事モジュール
│   │   │   ├── api/
│   │   │   ├── model/
│   │   │   └── ui/
│   │   │
│   │   ├── profile/                   # プロフィールモジュール
│   │   │   ├── api/
│   │   │   ├── model/
│   │   │   └── ui/
│   │   │
│   │   ├── nutrition/                 # 栄養モジュール
│   │   │   ├── api/
│   │   │   └── model/
│   │   │
│   │   └── report/                    # レポートモジュール
│   │       ├── api/
│   │       └── model/
│   │
│   ├── shared/                        # 共有リソース
│   │   ├── api/
│   │   │   ├── client.ts              # HTTPクライアント
│   │   │   ├── bffServer.ts           # BFFサーバー通信
│   │   │   ├── proxy.ts               # APIプロキシ
│   │   │   ├── errors.ts              # エラー定義
│   │   │   └── contracts/             # API契約
│   │   │       ├── auth.ts
│   │   │       ├── target.ts
│   │   │       └── index.ts
│   │   │
│   │   ├── config/
│   │   │   └── env.ts                 # 環境変数
│   │   │
│   │   ├── lib/
│   │   │   ├── errors.ts              # エラーユーティリティ
│   │   │   └── query/
│   │   │       ├── queryClient.ts     # TanStack Query設定
│   │   │       ├── keys.ts            # Query Keys
│   │   │       └── invalidate.ts      # キャッシュ無効化
│   │   │
│   │   └── ui/                        # 共有UIコンポーネント
│   │       ├── EmptyState.tsx
│   │       ├── ErrorState.tsx
│   │       ├── PageSkeleton.tsx
│   │       └── Toast.ts
│   │
│   ├── components/                    # 汎用UIコンポーネント
│   │   └── ui/                        # shadcn/ui ベース
│   │       ├── alert.tsx
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── input.tsx
│   │       ├── label.tsx
│   │       ├── select.tsx
│   │       ├── separator.tsx
│   │       ├── skeleton.tsx
│   │       └── textarea.tsx
│   │
│   └── lib/
│       └── utils.ts                   # ユーティリティ（cn関数等）
│
├── public/                            # 静的アセット
├── package.json
├── tsconfig.json
├── next.config.ts
├── tailwind.config.cjs
├── postcss.config.mjs
└── components.json                    # shadcn/ui 設定
```

### アーキテクチャパターン

#### Feature Sliced Design (FSD)

モジュールは以下の構造で整理されています：

```
modules/{feature}/
├── api/           # APIクライアント（Server/Client分離）
├── model/         # ビジネスロジック、カスタムフック
├── ui/            # Reactコンポーネント
├── contract/      # API契約定義（オプション）
└── index.ts       # Public API（再エクスポート）
```

#### BFF (Backend for Frontend) パターン

- `src/app/api/` にNext.js API Routesを配置
- サーバーサイドでバックエンドAPIを呼び出し、クライアントに適切な形式で返却
- Cookie認証のプロキシ処理を担当

### ルーティング構造

| パス | ルートグループ | 説明 |
|------|---------------|------|
| `/auth/login` | (public) | ログインページ |
| `/auth/register` | (public) | ユーザー登録ページ |
| `/` | (app) | ホーム（ダッシュボード） |
| `/meals` | (app) | 食事記録ページ |
| `/billing/plan` | (app) | プラン一覧 |
| `/onboarding/target` | (onboarding) | ターゲット設定 |

---

## 主要機能

### 認証・セッション管理

- ユーザー登録・ログイン・ログアウト
- Cookie ベースの JWT トークン管理（アクセストークン・リフレッシュトークン）
- 自動トークンリフレッシュ

### プロフィール管理

- ユーザー情報の登録・更新
- プロフィール画像のアップロード（MinIO）

### ターゲット管理

- 栄養目標（カロリー、タンパク質、脂質、炭水化物）の設定
- アクティブターゲットの管理
- OpenAI によるターゲット自動生成

### 食事記録

- 食事の記録（朝食、昼食、夕食、間食）
- 食事アイテムの追加・編集・削除
- 栄養情報の自動計算

### 栄養計算・分析

- 食事からの栄養推定（OpenAI 連携）
- 日次栄養サマリー
- ターゲット達成度の可視化

### レポート生成

- 日次レポートの自動生成（OpenAI 連携）
- 栄養摂取状況の分析
- 改善提案

### 推奨機能

- 食事推奨の自動生成（OpenAI 連携）
- ターゲットに基づいた提案

### 課金処理

- Stripe 連携によるサブスクリプション管理
- プラン管理（無料プラン・有料プラン）
- アップグレード・ダウングレード処理

---

## 開発環境

### バックエンド

| 項目 | 内容 |
|------|------|
| Python | 3.11+ |
| パッケージ管理 | `uv` または `pip` |
| 依存関係 | `pyproject.toml` |
| 起動 | `uvicorn app.main:app --reload` |
| テスト | `pytest` |
| Linter | `ruff` |
| 型チェック | `mypy` |

### フロントエンド

| 項目 | 内容 |
|------|------|
| Node.js | 20+ |
| パッケージ管理 | `pnpm` |
| 依存関係 | `package.json` |
| 起動 | `pnpm dev` |
| ビルド | `pnpm build` |
| Linter | `eslint` |

### 開発コンテナ

`.devcontainer/` に Docker 設定があり、統一された開発環境を提供します。

---

## CI/CD

### GitHub Actions

`.github/workflows/` に以下が定義されています：

| ワークフロー | 説明 |
|-------------|------|
| `backend-unit-tests.yml` | バックエンドユニットテスト |
| `backend-integration-tests.yml` | バックエンド統合テスト |
| `backend-real-integration.yml` | 実インフラ統合テスト |

---

## 外部サービス連携

### OpenAI

- 栄養推定
- 日次レポート生成
- 食事推奨生成
- ターゲット自動生成

### Stripe

- サブスクリプション管理
- 決済処理
- Webhook 処理

### MinIO

- プロフィール画像の保存（S3互換）

---

## セキュリティ

- JWT トークンベースの認証
- HTTP-only Cookie によるトークン管理
- パスワードの bcrypt ハッシュ化
- CORS 設定
- 環境変数による機密情報管理

---

## テスト戦略

### バックエンド

| テスト種別 | 内容 |
|-----------|------|
| ユニットテスト | ユースケース、ドメインロジック（53ファイル） |
| 統合テスト | API エンドポイント、データベース連携 |
| 実インフラテスト | 実際の DB、MinIO、OpenAI を使用 |

### フロントエンド

- TanStack Query によるサーバー状態管理
- Zod によるランタイム型検証
- （今後）E2Eテスト導入予定

---

## 参考情報

- バックエンド詳細: `/backend/README.md`
- Git 運用ルール: `/docs/workflow/GIT_WORKFLOW.md`
- OpenAPI 仕様: `/docs/openapi/openapi.yaml`
- ER図: `/backend/ER_DIAGRAM.md`
