---
paths:
  - 'src/app/api/**/*.{ts,tsx}'
---

# BFF (src/app/api) Rules

## 絶対

- Backend 直叩きは禁止。BFF は backend の /api/v1 を proxy する境界。
- Route Handler の `params` は async になり得る前提で、全メソッドで `await ctx.params` を統一する。

## Cookie 転送（重要）

- request：クライアント → BFF → backend へ `cookie` を転送
- response：backend → BFF → クライアントへ `set-cookie` を転送（複数 set-cookie 対応）

## 実装の作法

- fetch のエラーは shared/api の正規化関数に寄せる（unknown をそのまま投げない）
- BFF で機能ロジックを膨らませない（変換・proxy・認証境界が主）
