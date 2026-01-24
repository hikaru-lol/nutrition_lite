---
paths:
  - 'src/**/*.{ts,tsx}'
---

# Server / Client Separation Rules

## 原則

- client component から server-only（または next/headers）を import しない
- server-only 専用ファイルは先頭に `import 'server-only'` を置く

## 推奨ファイル配置（例）

- `src/modules/*/server.ts`：server-only 専用（先頭に import 'server-only'）
- `src/shared/api/server.ts`：server-only fetcher
- `src/shared/api/bffServer.ts`：BFF 呼び出しの server-only ユーティリティ

## Public API

- `src/modules/*/index.ts` は client-safe のみ export
- server-only を index.ts から export しない
