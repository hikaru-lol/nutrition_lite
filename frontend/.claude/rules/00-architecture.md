---
paths:
  - 'src/**/*.{ts,tsx,js,jsx}'
---

# Architecture Rules (Frontend)

## 絶対に崩さない依存方向

UI（modules/_/ui） → PageModel（modules/_/model） → API（modules/\*/api） → shared/api（fetcher） → BFF（src/app/api） → Backend

## ルール

- UI は PageModel（hooks）だけを見る。modules/\*/api を UI から直接 import しない
- API 呼び出しは modules/\*/api に閉じる（UI/Model 直 fetch 禁止）
- shared/api は「共通 fetch / エラー正規化」のみ（機能ロジック禁止）
- Backend 直叩き禁止（必ず BFF /api/\* 経由）
