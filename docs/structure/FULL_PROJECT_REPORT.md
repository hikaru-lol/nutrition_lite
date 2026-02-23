# 栄養トラッカー - フルプロジェクト構成レポート

## 概要

栄養管理アプリケーション。フロントエンド（Next.js）とバックエンド（FastAPI）のモノレポ構成。

## プロジェクト構造

```
/workspace
├── frontend/          # Next.js アプリケーション
├── backend/           # FastAPI API サーバー
├── docs/              # ドキュメント
├── .devcontainer/     # 開発コンテナ設定
└── .github/           # CI/CD ワークフロー
```

## 最近の主要な変更

### Stripe決済統合
- Stripe CLI統合による課金機能実装
- Webhook処理によるサブスクリプション状態同期
- テスト用サブスクリプション作成スクリプト

### UI/UX改善
- ダブルスクロールバー問題修正
- 通知ベルアイコン削除
- レスポンシブデザイン調整

### 栄養分析フロー改善
- 食事記録後の栄養分析フロー分析
- ユーザビリティ改善計画策定中

### セキュリティ強化
- 環境変数による秘密情報管理
- GitHub Secret Scanning対応

## 技術スタック

### フロントエンド
- Next.js 16 + React 19
- TypeScript 5
- TailwindCSS v4
- React Query 5

### バックエンド
- FastAPI + Uvicorn
- SQLAlchemy 2.0
- PostgreSQL
- Stripe API

### 開発環境
- Docker + devcontainer
- GitHub Actions
- ESLint + Prettier

## 現在の課題と今後の計画

1. **栄養分析フロー改善**
   - 食事追加後の自動栄養分析
   - ローディング状態の明確化
   - 完了通知の実装

2. **GitHub Secret Scanning対応**
   - 環境変数による秘密情報管理徹底
   - セキュアな開発フロー確立

3. **テスト範囲拡充**
   - E2Eテスト実装
   - 決済フロー統合テスト

## 開発者向け情報

詳細な技術仕様については以下を参照：
- フロントエンド: `/frontend/CLAUDE.md`
- バックエンド: `/backend/CLAUDE.md`
- プロジェクト全体: `/CLAUDE.md`