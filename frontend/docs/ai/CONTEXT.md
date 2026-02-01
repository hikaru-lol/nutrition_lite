# 固定コンテキスト（Project Context Pack）— Frontend

## 0) プロジェクト概要

- フロント：Next.js（App Router）+ TypeScript + Tailwind CSS + shadcn/ui + lucide-react
- 状態/通信：TanStack Query（server state）+ 自前 fetcher（共通エラー正規化）
- バックエンド：FastAPI（/api/v1）
- 方針：Doc-in-Code（外部仕様書を育てず、型と ViewState とテストで品質担保）

---

## 1) 最重要：依存方向（絶対に崩さない）

UI（modules/_/ui） → PageModel（modules/_/model） → API（modules/\*/api） → shared/api（fetcher） → BFF（src/app/api） → Backend

ルール：

- UI は PageModel（hooks）だけを見る。API 直叩き禁止。
- API 呼び出しは modules/\*/api に閉じる。
- shared/api は 共通 fetch・エラー正規化のみ（機能固有ロジック禁止）。
- Backend 直叩き禁止。必ず BFF（/api/\*）経由。

---

## 2) server/client 混入事故の永久防止（重要）

- `modules/*/server.ts`：server-only 専用（先頭に `import 'server-only'`）
- `shared/api/server.ts` / `shared/api/bffServer.ts`：server-only 専用
- `modules/*/index.ts`：client-safe のみ export（server-only を export しない）
- client component から `next/headers` / server-only を import しない

---

## 3) BFF（src/app/api）境界の方針

- BFF は backend `/api/v1/*` を proxy する
- Route Handler の params は Promise になり得るため、全メソッドで `await ctx.params` を統一
- Cookie は upstream/back 両方向で転送：
  - request：`cookie` を backend へ転送
  - response：`set-cookie` をクライアントへ転送（複数 Cookie 対応）

---

## 4) 認証ガードの原則

- オンボーディング配下は layout でガードする
- ガード判定は BFF 経由の `/api/auth/me` を叩く（backend 直叩き禁止）
- 完成判定：ログイン後に `GET /api/auth/me` が 200 になること

---

## 5) UI 実装の標準（shadcn 前提）

- 素の `<button>/<select>` は極力避け、`Button / Select / Input / Card` を使用
- 共通状態 UI を shared に置く：`PageSkeleton / EmptyState / ErrorState`
- 画面は ViewState の switch で描画（idle/submitting/success/error）
- Error 表示は `toErrorMessage(err: unknown)` 等で統一（any 禁止）

---

## 6) データ契約（Contract）優先

- request/response の型は contract（Zod schema）に集約
- UI/Model/API はその型を import して使う（`as` キャスト禁止）
- 数値入力は `valueAsNumber` 等で number 化し、schema は基本 `z.number()`

---

## 7) TanStack Query の使い方（量産ルール）

- PageModel は `useMutation/useQuery` を持ち、UI に ViewState だけ返す
- `useMutation<TData, TError, TVariables>` で error 型を決め、any を使わない
- invalidate/queryKey は feature 内に閉じる（shared に散らさない）

---

## 8) ルーティングの注意

- `(group)` は URL に出ない。URL が同一になる構成は作らない
- 衝突したら片方削除 or URL を分ける

---

## “AI への禁止事項”まとめ（短縮）

- backend 直叩き禁止（必ず `/api/*`）
- UI から API を呼ばない（PageModel 経由）
- server-only を client へ export/import しない
- `any` を導入しない（unknown → 正規化）
- `(group)` による URL 衝突を作らない
