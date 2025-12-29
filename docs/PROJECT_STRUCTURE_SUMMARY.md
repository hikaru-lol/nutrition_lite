# プロジェクト構成まとめ

本ドキュメントは、/workspace 配下の現在の構成を整理して要点のみ記載しています。

## 全体概要
- フルスタック構成: バックエンド (FastAPI/Python) + フロントエンド (Next.js/TypeScript)
- ドメイン分割とクリーンアーキテクチャを採用
- 主要機能: 認証、プロフィール、食事記録、栄養計算、日次レポート、ターゲット、課金

## トップレベル構成
```
/workspace
├── backend/   # バックエンド実装とテスト
├── frontend/  # フロントエンド実装
├── .devcontainer/ # 開発コンテナ設定
├── .github/   # GitHub Actions などの設定
├── docs/      # 全体/仕様/運用ドキュメント
├── scripts/   # 初期化/補助スクリプト
└── README.md  # ルートの概要
```

## バックエンド (/backend)
- app/: アプリケーション本体
  - api/: FastAPI ルーター/スキーマ/依存注入
  - application/: ユースケース・DTO・ポート
  - domain/: ドメインエンティティとルール
  - infra/: DB/LLM/ストレージ/セキュリティなどの実装
  - jobs/: バッチ/ジョブ
- alembic/: DBマイグレーション
- tests/: unit/integration/integration_real と fakes
- docs/: バックエンド構成やOpenAPI仕様

## フロントエンド (/frontend)
- app/: App Router ページ (public/app/onboarding)
- components/: 機能別UIと共通UI
- lib/: APIクライアント/フック/ユーティリティ/MSW
- types/: 共有型定義
- public/: 静的アセット

## ドキュメント (/docs)
- PROJECT_STRUCTURE.md: 詳細な構成ドキュメント
- GIT_WORKFLOW.md: 運用ルール
- frontend_*: 画面/要件/コンポーネントの整理

## 開発環境 (.devcontainer)
- Docker を利用した開発コンテナ設定

## CI/CD (.github)
- GitHub Actions のワークフロー定義

## スクリプト (/scripts)
- 初期構成の作成や骨組み生成用のシェルスクリプト

## 参考
- 詳細は `docs/PROJECT_STRUCTURE.md` を参照
- OpenAPI は `backend/docs/openapi/openapi.yaml`
