---
description: 開発環境を起動（バックエンド・フロントエンド・Stripe CLI）
---

以下の開発環境を起動してください：

## 起動手順

1. **バックエンドサーバー**を起動
   - ディレクトリ: `backend/`
   - コマンド: `uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
   - ポート: 8000
   - OpenAPIドキュメント: http://localhost:8000/docs

2. **フロントエンドサーバー**を起動
   - ディレクトリ: `frontend/`
   - コマンド: `pnpm dev`
   - ポート: 3000
   - URL: http://localhost:3000

3. **Stripe Webhookリスナー**を起動（オプション）
   - コマンド: `stripe listen --forward-to localhost:8000/api/v1/billing/stripe/webhook`
   - 課金機能のテスト時のみ必要

## 確認事項

- PostgreSQLが起動していること（`docker compose up -d db`）
- MinIOが起動していること（`docker compose up -d minio`）
- 環境変数が設定されていること（`.env`ファイル）

## デモアカウント

- Email: `demo@example.com`
- Password: `demo1234demo`

$ARGUMENTS