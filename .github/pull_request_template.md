## 目的

-

## 変更概要

-

## 受け入れ条件（AC）

- [ ]

## 検証

- [ ] Frontend: `cd frontend && pnpm lint`（必要なら）
- [ ] Frontend: `cd frontend && pnpm test`（必要なら）
- [ ] Backend: `cd backend && pytest`（必要なら）
- [ ] 手動確認:

## アーキテクチャチェック

- [ ] FE: UI が PageModel 経由（API 直叩きなし）
- [ ] FE: backend 直叩きなし（BFF `/api/*` 経由）
- [ ] FE: server-only 混入なし
- [ ] FE: `any` を導入していない
- [ ] FE: URL 衝突（(group)）を作っていない
- [ ] BE: 依存方向（API→App→Domain→Infra）を崩していない
- [ ] Cross: OpenAPI / Contract / BFF / Client の同期が取れている
