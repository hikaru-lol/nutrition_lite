# プロジェクト構成サマリー

本ドキュメントは、/workspace 配下の現在の構成を整理して要点のみ記載しています。
詳細は `PROJECT_STRUCTURE.md` を参照してください。

## 全体概要

- **フルスタック構成**: バックエンド (FastAPI/Python) + フロントエンド (Next.js/TypeScript)
- **アーキテクチャ**: クリーンアーキテクチャ（バックエンド）、Feature Sliced Design（フロントエンド）
- **主要機能**: 認証、プロフィール、食事記録、栄養計算、日次レポート、ターゲット、課金

---

## トップレベル構成

```
/workspace
├── backend/           # バックエンド実装（FastAPI + Python）
├── frontend/          # フロントエンド実装（Next.js + TypeScript）
├── .devcontainer/     # 開発コンテナ設定
├── .github/           # GitHub Actions CI/CD
├── docs/              # プロジェクトドキュメント
│   ├── structure/     # 構成ドキュメント
│   ├── workflow/      # 運用ドキュメント
│   ├── openapi/       # OpenAPI仕様
│   └── 要件&仕様/     # 機能要件・仕様書
├── scripts/           # 補助スクリプト
└── README.md          # ルート概要
```

---

## バックエンド (`/backend`)

### レイヤー構造

```
API層 → Application層 → Domain層 → Infrastructure層
```

### 主要ディレクトリ

| ディレクトリ       | 説明                                    |
| ------------------ | --------------------------------------- |
| `app/api/http/`    | FastAPI ルーター、スキーマ、依存注入    |
| `app/application/` | ユースケース、DTO、ポート（6 ドメイン） |
| `app/domain/`      | エンティティ、値オブジェクト、エラー    |
| `app/infra/`       | DB、LLM、ストレージ、セキュリティ実装   |
| `app/di/`          | 依存性注入コンテナ                      |
| `app/jobs/`        | バッチジョブ                            |
| `tests/`           | unit / integration / integration_real   |
| `alembic/`         | DB マイグレーション                     |

### API ルーター（7 ルーター）

- auth, profile, target, meal, nutrition, daily_report, billing

### データベース（14 テーブル）

- users, profiles, billing_accounts
- targets, target_nutrients, daily_target_snapshots, daily_target_snapshot_nutrients
- food_entries, meal_nutrition_summaries, meal_nutrition_nutrients, meal_recommendations
- daily_nutrition_summaries, daily_nutrition_nutrients, daily_nutrition_reports

---

## フロントエンド (`/frontend`)

### 技術スタック

- Next.js 16 (App Router) + React 19
- TypeScript + TanStack Query
- Tailwind CSS 4 + Radix UI

### 主要ディレクトリ

| ディレクトリ         | 説明                                       |
| -------------------- | ------------------------------------------ |
| `src/app/`           | App Router ページ（public/app/onboarding） |
| `src/modules/`       | 機能モジュール（Feature Sliced Design）    |
| `src/shared/`        | 共有ユーティリティ、API、UI                |
| `src/components/ui/` | 汎用 UI コンポーネント（shadcn/ui）        |
| `src/lib/`           | ユーティリティ関数                         |

### モジュール構造

```
modules/{feature}/
├── api/       # APIクライアント
├── model/     # ビジネスロジック・フック
├── ui/        # Reactコンポーネント
└── index.ts   # Public API
```

### ルートグループ

| グループ     | パス例                          | 説明             |
| ------------ | ------------------------------- | ---------------- |
| (public)     | `/auth/login`, `/auth/register` | 公開ページ       |
| (app)        | `/`, `/meals`, `/billing/plan`  | 認証済みページ   |
| (onboarding) | `/onboarding/target`            | オンボーディング |

---

## 外部サービス

| サービス | 用途                                             |
| -------- | ------------------------------------------------ |
| OpenAI   | 栄養推定、レポート生成、推奨生成、ターゲット生成 |
| Stripe   | サブスクリプション、決済処理                     |
| MinIO    | プロフィール画像保存（S3 互換）                  |

---

## 開発環境

### コマンド

| 環境           | 起動コマンド                                  |
| -------------- | --------------------------------------------- |
| バックエンド   | `cd backend && uvicorn app.main:app --reload` |
| フロントエンド | `cd frontend && pnpm dev`                     |
| テスト（BE）   | `cd backend && pytest`                        |

### 開発コンテナ

- `.devcontainer/` に統一開発環境設定

---

## 参考リンク

- 詳細構成: `docs/structure/PROJECT_STRUCTURE.md`
- Git 運用: `docs/workflow/GIT_WORKFLOW.md`
- OpenAPI: `docs/openapi/openapi.yaml`
- ER 図: `backend/ER_DIAGRAM.md`
