# Frontend Context Pack (固定コンテキスト)

## 0) プロジェクト概要

- フロント：Next.js 16 (App Router) + React + TypeScript
- UI：Tailwind CSS + Radix + shadcn/ui
- 通信：TanStack Query + 共通 fetcher（エラー正規化）
- Backend：FastAPI `/api/v1`
- 方針：Doc-in-Code（外部仕様書は育てず、型/ViewState/テストで担保）

---

## 1) 最重要：依存方向（絶対に崩さない）

UI（`frontend/src/modules/*/ui`）
→ PageModel（`frontend/src/modules/*/model`）
→ API（`frontend/src/modules/*/api`）
→ shared/api（`frontend/src/shared/api`）
→ BFF（`frontend/src/app/api`）
→ Backend（`/api/v1`）

ルール：

- UI は PageModel（hooks）だけを見る。API 直叩き禁止。
- API 呼び出しは modules/\*/api に閉じる。
- shared/api は共通 fetch・エラー正規化のみ（機能固有ロジック禁止）。
- Backend 直叩き禁止。必ず BFF（/api/\*）経由。

---

## 2) server/client 混入事故の永久防止（重要）

- server-only 専用ファイルは先頭に `import 'server-only'`
- `modules/*/server.ts`：server-only 専用
- `modules/*/index.ts`：client-safe のみを export（server-only を export しない）
- client component から `next/headers` / server-only を import しない

---

## 3) BFF（app/api）境界の方針

- `/api/auth/*` 等は backend `/api/v1/*` へ proxy
- Route Handler params は Promise になり得るため、`await ctx.params` を統一
- Cookie は upstream/back 両方向で転送（cookie / set-cookie 複数対応）

---

## 4) 認証ガードの原則

- onboarding 配下は `frontend/src/app/(onboarding)/layout.tsx` でガード
- 判定は BFF `/api/auth/me`（backend 直叩き禁止）
- 完成判定：ログイン後に `GET /api/auth/me` が 200

---

## 5) UI 実装の標準（shadcn 前提）

- `<button>` 等の素 HTML より shadcn（Button/Select/Input/Card）を優先
- 共通状態 UI：`PageSkeleton / EmptyState / ErrorState` を shared に置く
- 画面は ViewState の switch で描画（idle/submitting/success/error）
- Error 表示は `toErrorMessage(err: unknown)` で統一（any 禁止）

---

## 6) データ契約（Contract）優先

- request/response の型は contract（Zod schema）に集約
- UI/Model/API は schema 由来の型を import（`as` キャスト禁止）
- 数値入力は RHF `valueAsNumber: true`、schema は `z.number()` を基本

---

## 7) TanStack Query（量産ルール）

- PageModel は `useMutation/useQuery` を持ち、UI に ViewState だけ返す
- `useMutation<TData, TError, TVariables>` で error 型を決める（any 禁止）
- invalidate/queryKey は feature 内に閉じる（shared に散らさない）

---

## 8) ルーティングの注意

- `(group)` は URL に出ない。URL 衝突を作らない

---

## AI への禁止事項（短縮）

- backend 直叩き禁止（必ず `/api/*`）
- UI から API を呼ばない（PageModel 経由）
- server-only を client へ export/import しない
- `any` を導入しない
- `(group)` による URL 衝突を作らない
