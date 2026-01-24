---
paths:
  - 'src/modules/**/model/**/*.{ts,tsx}'
---

# TanStack Query Rules

## PageModel の責務

- useQuery/useMutation を持ち、UI に ViewState だけ返す
- useMutation<TData, TError, TVariables> で error 型を決め、any を使わない
- queryKey / invalidate は feature 内に閉じる（shared に散らさない）

## 禁止

- UI で useQuery/useMutation を直接持たない（基本は model に寄せる）
- shared/api に機能固有の queryKey を置かない
