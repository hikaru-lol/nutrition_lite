# 🥗 Nutrition Tracker

**AI駆動の栄養管理SaaS** — 日々の食事記録・栄養分析・目標管理・食事推薦を提供するフルスタックWebアプリケーション

[![Backend Unit Tests](https://github.com/{your-username}/nutrition-tracker/actions/workflows/backend-unit-tests.yml/badge.svg)](https://github.com/{your-username}/nutrition-tracker/actions)
[![Backend Integration Tests](https://github.com/{your-username}/nutrition-tracker/actions/workflows/backend-integration-tests.yml/badge.svg)](https://github.com/{your-username}/nutrition-tracker/actions)
[![Backend Real Integration](https://github.com/{your-username}/nutrition-tracker/actions/workflows/backend-real-integration.yml/badge.svg)](https://github.com/{your-username}/nutrition-tracker/actions)

---

## Tech Stack

**Frontend:** Next.js 16 (App Router) / React 19 / TypeScript 5 / TailwindCSS v4 / TanStack Query v5

**Backend:** FastAPI / SQLAlchemy 2.0 / PostgreSQL 16 / Pydantic v2

**AI:** OpenAI API（栄養推定・目標生成・日次レポート・食事推薦）

**Infra:** Docker Compose / GitHub Actions (CI 3ワークフロー) / Vercel / Railway

**Other:** Stripe（サブスクリプション課金） / MinIO（S3互換ストレージ） / JWT認証（Cookieベース）

---

## Architecture

### システム全体構成

```
Browser (React 19)
    ↕
Next.js BFF (API Routes)  ← Cookie中継・プロキシ
    ↕
FastAPI REST API
    ↕
┌────────────┬────────────┬────────────┐
│ PostgreSQL │   MinIO    │  OpenAI    │
│     16     │  (S3互換)  │   API      │
└────────────┴────────────┴────────────┘
                                │
                            Stripe
```

### バックエンド：クリーンアーキテクチャ + ポート&アダプター

```
┌──────────────────────────────────────────────┐
│  api/http    ← HTTP層（Router / Schema）      │
├──────────────────────────────────────────────┤
│  application ← ユースケース層（UseCase / DTO） │
├──────────────────────────────────────────────┤
│  domain      ← ドメイン層（Entity / VO）       │
├──────────────────────────────────────────────┤
│  infra       ← インフラ層（DB / LLM / Stripe）│
└──────────────────────────────────────────────┘

依存方向:  api/http → application → domain ← infra
```

- **Unit of Work** でトランザクション管理
- **Repository パターン** でポート定義 → SQLAlchemy実装
- **DI（依存性注入）** で FastAPI Depends() による自動解決
- **Feature Flags** で環境変数により OpenAI / Stub 実装を切替

### フロントエンド：5層レイヤードアーキテクチャ

```
Layer 1: UI Presentation     ← 純粋な表現コンポーネント
Layer 2: UI Orchestration     ← イベントハンドリング
Layer 3: Page Aggregation     ← ページレベルの機能統合
Layer 4: Feature Logic        ← React Query + 状態管理
Layer 5: Domain Services      ← API呼び出し + ビジネスロジック
```

---

## Features

| 機能 | 説明 | 技術的ポイント |
|------|------|---------------|
| 🔐 認証 | Cookie JWT + BFFプロキシ | HttpOnly / SameSite=Lax / XSS防止 |
| 🎯 栄養目標 | AI生成 + 手動設定 | OpenAI → ポート抽象化 → Stub切替 |
| 🍽️ 食事記録 | 日次記録 + AI栄養推定 | 10種栄養素の自動計算 |
| 📊 日次レポート | AI分析レポート生成 | 目標との差分分析 + 改善提案 |
| 🤖 食事推薦 | 個人最適化された提案 | レート制限（30分間隔 / 日次5回） |
| 💳 課金 | Stripe サブスクリプション | Checkout / Portal / Webhook |
| 📅 カレンダー | 月間記録一覧 | 記録完了ステータス可視化 |

---

## Testing Strategy

**3層テストアーキテクチャ** で段階的に品質を検証。

```
┌──────────────────────────────────────┐
│  Real Integration Tests              │  ← PostgreSQL + MinIO 実接続
│  tests/integration_real/             │
├──────────────────────────────────────┤
│  Integration Tests (Fake Infra)      │  ← インメモリ実装で高速実行
│  tests/integration/                  │
├──────────────────────────────────────┤
│  Unit Tests                          │  ← モック / フェイクで独立実行
│  tests/unit/                         │
└──────────────────────────────────────┘
```

- 全ドメインに **Fake実装** を用意（InMemoryRepository, FakePasswordHasher, FixedClock）
- GitHub Actions で **3ワークフロー** が自動実行
- Real Integration テストでは PostgreSQL 16 + MinIO をサービスコンテナで起動

---

## Project Structure

```
/workspace
├── frontend/src/
│   ├── app/                    # Next.js App Router（22 BFF Routes）
│   ├── modules/                # 機能モジュール（12モジュール）
│   │   ├── auth/    meal/    nutrition/    target/
│   │   ├── billing/ profile/ calendar/     today/
│   │   └── reports/ tutorial/ meal-recommendation/
│   ├── components/ui/          # shadcn/ui（13コンポーネント）
│   └── shared/                 # API Client / Providers / Hooks
│
├── backend/app/
│   ├── api/http/               # 10 Router / Schemas / Mappers
│   ├── application/            # 35 UseCases / DTOs / Ports
│   ├── domain/                 # 7 Domains / Entities / VOs
│   ├── infra/                  # DB(14テーブル) / LLM / Stripe / Storage
│   └── di/container.py         # DIコンテナ
│
├── .github/workflows/          # CI/CD（3ワークフロー）
└── .devcontainer/              # Docker Compose 開発環境
```

---

## Design Decisions

| 設計判断 | 選択 | 理由 |
|---------|------|------|
| 認証方式 | Cookie JWT + BFF | XSS防止。フロントエンドにトークンを露出させない |
| AI統合 | ポート&アダプター | 環境変数でOpenAI/Stub切替。テスト時に外部API不要 |
| トランザクション | Unit of Work | 成功時commit/失敗時rollback を一元管理 |
| フロントエンド状態 | TanStack Query | サーバー状態のキャッシュ・再検証を宣言的に管理 |
| API通信 | BFFプロキシ | CORS回避 + Cookie中継 + バックエンドURL隠蔽 |
| テスト | 3層構造 | 速度と信頼性のトレードオフを段階的に解決 |
| 課金 | Stripe Checkout | PCI DSS準拠不要。Webhook で状態同期 |

---

## Getting Started

### 前提条件

- Docker & Docker Compose
- Node.js 20+（pnpm 10+）
- Python 3.11+（uv）

### セットアップ

```bash
# リポジトリのクローン
git clone https://github.com/{your-username}/nutrition-tracker.git
cd nutrition-tracker

# devcontainerで起動（推奨）
# VSCodeで開く → "Reopen in Container" を選択

# または手動起動
docker compose up -d db minio

# バックエンド
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000

# フロントエンド
cd frontend
pnpm install
pnpm dev
```

### テスト実行

```bash
# Unit Tests
uv run pytest tests/unit/

# Integration Tests（Fake Infra）
uv run pytest tests/integration/

# Real Integration Tests（要 PostgreSQL + MinIO）
uv run pytest -m "real_integration"
```

---

## 規模感

| 項目 | 数値 |
|------|------|
| バックエンド ドメイン | 7 |
| API エンドポイント | 35 |
| DBテーブル | 14 |
| ユースケース | 35 |
| フロントエンド モジュール | 12 |
| BFF Routes | 22 |
| CI ワークフロー | 3 |
| AI機能（ポート抽象化） | 4 |