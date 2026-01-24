---
paths:
  - 'src/app/**/*.{ts,tsx}'
---

# Routing Rules (App Router)

- (group) は URL に出ないため、同一 URL になる構成は作らない
  - 例：`src/app/target` と `src/app/(onboarding)/target` は /target で衝突する
- URL が同一になる構成は削除 or URL を分けて回避する
