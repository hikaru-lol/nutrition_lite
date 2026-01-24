---
paths:
  - 'src/**/*.{ts,tsx}'
---

# Data Contract Rules (Zod-first)

## 原則

- request/response の型は contract（Zod schema）に集約
- UI / Model / API は contract の型を import して使う（as キャスト禁止）

## 数値入力

- フォーム入力は valueAsNumber 等で number 化
- schema は基本 `z.number()`（文字列で保持しない）
