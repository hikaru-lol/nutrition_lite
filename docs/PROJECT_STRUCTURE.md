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
├── backend/                 # バックエンド（FastAPI + Python）
├── frontend/               # フロントエンド（Next.js + TypeScript）
├── docs/                   # プロジェクトドキュメント
├── scripts/                # 補助スクリプト
└── README.md              # プロジェクトルートREADME
```

---

## バックエンド構成 (`/backend`)

### アーキテクチャ

クリーンアーキテクチャの原則に基づき、以下のレイヤーで構成されています：

- **API 層** (`app/api/`): HTTP エンドポイント、リクエスト/レスポンスのスキーマ定義
- **Application 層** (`app/application/`): ユースケース、ビジネスロジック
- **Domain 層** (`app/domain/`): エンティティ、値オブジェクト、ドメインルール
- **Infrastructure 層** (`app/infra/`): データベース、外部サービス、実装詳細

### 主要ディレクトリ

#### `app/api/http/`

- **routers/**: FastAPI ルーター定義
  - `auth_route.py`: 認証関連エンドポイント
  - `profile_route.py`: プロフィール管理
  - `target_route.py`: ターゲット（目標）管理
  - `meal_route.py`: 食事記録
  - `daily_report_route.py`: 日次レポート
  - `nutrition_route.py`: 栄養計算
  - `billing_route.py`: 課金処理
- **schemas/**: Pydantic スキーマ（リクエスト/レスポンス）
- **dependencies/**: FastAPI 依存性注入（認証ミドルウェアなど）
- **errors.py**: エラーハンドリング

#### `app/application/`

各機能ドメインごとにユースケースを定義：

- **auth/**: 認証・セッション管理

  - `use_cases/account/`: ユーザー登録・削除
  - `use_cases/session/`: ログイン・ログアウト・トークンリフレッシュ
  - `use_cases/current_user/`: 現在のユーザー情報取得
  - `ports/`: インターフェース定義（リポジトリ、サービス）
  - `dto/`: データ転送オブジェクト

- **profile/**: プロフィール管理
- **target/**: 栄養目標（ターゲット）管理
- **meal/**: 食事記録
- **nutrition/**: 栄養計算・レポート生成
  - `use_cases/`: 栄養推定、レポート生成、推奨生成
  - `ports/`: 栄養計算、レポート生成、推奨生成のインターフェース
- **billing/**: 課金処理（Stripe 連携）

#### `app/domain/`

ドメインエンティティとビジネスルール：

- **auth/**: ユーザーエンティティ、認証関連の値オブジェクト
- **profile/**: プロフィールエンティティ
- **target/**: ターゲットエンティティ
- **meal/**: 食事エンティティ
- **nutrition/**: 栄養情報、レポート、推奨のエンティティ
- **billing/**: 課金関連エンティティ

#### `app/infra/`

外部サービス・データベースの実装：

- **db/**: SQLAlchemy モデルとリポジトリ実装
  - `models/`: データベースモデル
  - `repositories/`: リポジトリ実装
  - `uow/`: ユニットオブワーク実装
- **security/**: JWT、パスワードハッシュ
- **llm/**: OpenAI 連携（栄養推定、レポート生成、推奨生成、ターゲット生成）
- **storage/**: MinIO 連携（プロフィール画像保存）
- **billing/**: Stripe クライアント実装
- **time/**: 時刻サービス

#### `app/di/`

- `container.py`: 依存性注入コンテナ

#### `app/jobs/`

- `generate_meal_recommendations.py`: バッチジョブ（食事推奨生成）

#### `app/main.py`

FastAPI アプリケーションのエントリーポイント

#### `app/settings.py`

環境変数とアプリケーション設定

### データベース

- **Alembic**: マイグレーション管理
- **SQLAlchemy**: ORM
- 対応 DB: SQLite（開発）、PostgreSQL（本番）

### テスト構成 (`/backend/tests`)

- **unit/**: ユニットテスト（ユースケース、ドメインロジック）
- **integration/**: 統合テスト（API エンドポイント、データベース）
- **integration_real/**: 実インフラを使用する統合テスト
- **fakes/**: テスト用のフェイク実装

---

## フロントエンド構成 (`/frontend`)

### 技術スタック

- **Next.js 16**: React フレームワーク（App Router）
- **TypeScript**: 型安全性
- **Tailwind CSS**: スタイリング
- **Recharts**: グラフ・チャート表示
- **MSW (Mock Service Worker)**: API モック（開発用）

### 主要ディレクトリ

#### `app/`

Next.js App Router のページ定義：

- **(app)/**: 認証済みユーザー向けページ
  - `page.tsx`: ホーム（今日の概要）
  - `meals/page.tsx`: 食事記録ページ
  - `profile/page.tsx`: プロフィール設定
  - `targets/page.tsx`: ターゲット管理
  - `recommendations/today/page.tsx`: 今日の推奨
  - `reports/daily/[date]/page.tsx`: 日次レポート
  - `billing/plan/page.tsx`: プラン一覧
  - `billing/upgrade/page.tsx`: プランアップグレード
- **(onboarding)/**: オンボーディングフロー
  - `onboarding/profile/page.tsx`: プロフィール設定
  - `onboarding/target/page.tsx`: ターゲット設定
- **(public)/**: 公開ページ
  - `auth/login/page.tsx`: ログイン
  - `auth/register/page.tsx`: ユーザー登録

#### `components/`

React コンポーネント：

- **auth/**: 認証関連コンポーネント
- **layout/**: レイアウトコンポーネント（ヘッダー、サイドバー、シェル）
- **meals/**: 食事記録関連
  - `MealsPage.tsx`: メインページ
  - `MealItemDialog.tsx`: 食事アイテム追加/編集ダイアログ
  - `MealNutritionChart.tsx`: 栄養チャート
  - `MealSlotCard.tsx`: 食事スロット（朝食、昼食など）カード
- **profile/**: プロフィール設定
- **targets/**: ターゲット管理
- **recommendations/**: 推奨表示
- **reports/**: レポート表示
- **today/**: 今日の概要
- **billing/**: 課金関連
- **ui/**: 汎用 UI コンポーネント（Button, Card, Input など）

#### `lib/`

ユーティリティと API クライアント：

- **api/**: API クライアント関数
  - `client.ts`: ベース HTTP クライアント
  - `auth.ts`: 認証 API
  - `meals.ts`: 食事記録 API
  - `nutrition.ts`: 栄養計算 API
  - `profile.ts`: プロフィール API
  - `targets.ts`: ターゲット API
  - `dailyReport.ts`: レポート API
  - `recommendation.ts`: 推奨 API
  - `today.ts`: 今日の概要 API
  - `billing.ts`: 課金 API
- **hooks/**: カスタム React フック
  - `useCurrentUser.ts`: 現在のユーザー情報
  - `useMealsByDate.ts`: 日付別食事取得
  - `useDailyReport.ts`: 日次レポート取得
  - `useTodayOverview.ts`: 今日の概要取得
  - `useTodayRecommendation.ts`: 今日の推奨取得
- **mocks/**: MSW ハンドラー（開発用 API モック）
- **utils.ts**: 汎用ユーティリティ関数

#### `types/`

TypeScript 型定義：

- `auth.ts`: 認証関連型
- `meal.ts`: 食事関連型
- `nutrition.ts`: 栄養関連型
- `profile.ts`: プロフィール型
- `target.ts`: ターゲット型
- `report.ts`: レポート型

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

- **Python**: 3.11+
- **パッケージ管理**: `uv` または `pip`
- **依存関係**: `pyproject.toml`で管理
- **起動**: `uvicorn app.main:app --reload`
- **テスト**: `pytest`

### フロントエンド

- **Node.js**: 20+
- **パッケージ管理**: `pnpm`
- **依存関係**: `package.json`で管理
- **起動**: `pnpm dev`
- **ビルド**: `pnpm build`

### 開発コンテナ

`.devcontainer/`に Docker 設定があり、統一された開発環境を提供します。

---

## CI/CD

### GitHub Actions

`.github/workflows/`に以下が定義されています：

- `ci.yml`: 全体の CI
- `backend-ci.yml`: バックエンド専用 CI
- `backend-real-integration.yml`: 実インフラを使用する統合テスト

---

## ドキュメント

`/docs`ディレクトリに以下が含まれます：

- `GIT_WORKFLOW.md`: Git 運用ルール（GitHub Flow）
- `frontend_business_requirements.md`: フロントエンド要件（空）
- `frontend_components.md`: フロントエンドコンポーネント（空）
- `frontend_screen_map.md`: 画面マップ（空）

`/backend/docs`には以下が含まれます：

- `backend_structure.md`: バックエンド構造説明
- `openapi/openapi.yaml`: OpenAPI 仕様
- `要件&仕様/`: 各機能の要件・仕様書

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

- プロフィール画像の保存

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

- **ユニットテスト**: ユースケース、ドメインロジック
- **統合テスト**: API エンドポイント、データベース連携
- **実インフラ統合テスト**: 実際の DB、MinIO、OpenAI を使用

### フロントエンド

- MSW による API モック
- 開発時のモックサーバー

---

## 今後の拡張

- 認証以外の機能追加時も、application 層に新ユースケース、infra 層にリポジトリ実装を追加するだけで API に組み込み可能
- クリーンアーキテクチャにより、テスト容易性と保守性を確保
- ドメイン層の独立性により、ビジネスロジックの変更が容易

---

## 参考情報

- バックエンド詳細: `/backend/README.md`
- Git 運用ルール: `/docs/GIT_WORKFLOW.md`
- OpenAPI 仕様: `/backend/docs/openapi/openapi.yaml`
