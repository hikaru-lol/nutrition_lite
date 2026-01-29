---
tags:
created: 2026-01-27 19:10
aliases:
related:
---

# Profile Module - 依存関係分析ドキュメント

## 概要

Profile モジュールは、ユーザープロフィールの取得・更新機能を提供する Feature Module です。
本ドキュメントでは、各ファイル間の依存関係とデータフローを分析します。

---

## アーキテクチャ概要

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              Browser                                    │
├─────────────────────────────────────────────────────────────────────────┤
│  app/(onboarding)/profile/page.tsx                                      │
│       │                                                                 │
│       ↓ imports                                                         │
│  modules/profile/ui/ProfilePage.tsx                                     │
│       │                                                                 │
│       ↓ uses (hook)                                                     │
│  modules/profile/model/useProfilePageModel.ts                           │
│       │                                                                 │
│       ↓ calls                                                           │
│  modules/profile/api/profileClient.ts                                   │
│       │                                                                 │
│       ↓ uses                                                            │
│  shared/api/client.ts (clientApiFetch)                                  │
│       │                                                                 │
│       ↓ fetch("/api/profile/me")                                        │
├─────────────────────────────────────────────────────────────────────────┤
│                         Next.js Server (BFF)                            │
├─────────────────────────────────────────────────────────────────────────┤
│  app/api/profile/route.ts                                               │
│       │                                                                 │
│       ↓ uses                                                            │
│  shared/api/proxy.ts (proxyToBackend)                                   │
│       │                                                                 │
│       ↓ fetch(backendUrl)                                               │
├─────────────────────────────────────────────────────────────────────────┤
│                         Backend (FastAPI)                               │
│  /api/v1/profile                                                        │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## ファイル別依存関係

### 1. `app/(onboarding)/profile/page.tsx`

| レイヤー | Next.js Page                   |
| -------- | ------------------------------ |
| 役割     | ルーティングエントリーポイント |

**インポート:**

- `@/modules/profile/ui/ProfilePage` - UI コンポーネント

**依存されている:**

- Next.js App Router（URL `/profile` でルーティング）

```
page.tsx
  └── ProfilePage (UI)
```

---

### 2. `modules/profile/ui/ProfilePage.tsx`

| レイヤー | UI Layer                             |
| -------- | ------------------------------------ |
| 役割     | プロフィール入力フォームの表示・操作 |

**インポート:**

| カテゴリ      | インポート元                   | 用途                                    |
| ------------- | ------------------------------ | --------------------------------------- |
| React         | `react`                        | `useEffect`                             |
| Next.js       | `next/navigation`              | `useRouter` (ナビゲーション)            |
| Form          | `react-hook-form`              | フォーム状態管理                        |
| Validation    | `@hookform/resolvers/zod`      | Zod バリデーション連携                  |
| UI Components | `@/components/ui/*`            | shadcn/ui (Card, Button, Input, Select) |
| Shared UI     | `@/shared/ui/Status/*`         | LoadingState, ErrorState                |
| PageModel     | `../model/useProfilePageModel` | ビジネスロジック・API 呼び出し          |

**依存されている:**

- `app/(onboarding)/profile/page.tsx`

**レイヤー規約準拠:**

- ✅ UI は PageModel のみをインポート
- ✅ API を直接呼び出していない
- ✅ ViewState パターン (`isLoading`, `isError`) を使用

```
ProfilePage.tsx
  ├── useProfilePageModel (Model)
  ├── shadcn/ui components
  └── shared/ui/Status components
```

---

### 3. `modules/profile/model/useProfilePageModel.ts`

| レイヤー | PageModel Layer                                          |
| -------- | -------------------------------------------------------- |
| 役割     | API 呼び出しのオーケストレーション、フォームスキーマ定義 |

**インポート:**

| カテゴリ       | インポート元                  | 用途                                        |
| -------------- | ----------------------------- | ------------------------------------------- |
| React          | `react`                       | `useMemo`                                   |
| TanStack Query | `@tanstack/react-query`       | `useQuery`, `useMutation`, `useQueryClient` |
| Validation     | `zod`                         | フォームスキーマ定義                        |
| API Client     | `../api/profileClient`        | `fetchProfile`, `upsertProfile`             |
| Contract       | `../contract/profileContract` | `SexSchema`, `UpsertProfileInput` 型        |

**依存されている:**

- `modules/profile/ui/ProfilePage.tsx`

**エクスポート:**

- `ProfileFormSchema` - フォームバリデーションスキーマ
- `ProfileFormValues` - フォーム入力型
- `useProfilePageModel()` - PageModel フック

**レイヤー規約準拠:**

- ✅ TanStack Query の `useQuery`/`useMutation` を所有
- ✅ Query Key はモジュールローカル (`qk.me`)
- ✅ API Client を通じてのみ通信

```
useProfilePageModel.ts
  ├── profileClient (API)
  │     ├── fetchProfile()
  │     └── upsertProfile()
  └── profileContract (Contract)
        ├── SexSchema
        └── UpsertProfileInput
```

---

### 4. `modules/profile/api/profileClient.ts`

| レイヤー | API Layer (Feature)                                        |
| -------- | ---------------------------------------------------------- |
| 役割     | BFF エンドポイントへのリクエスト、レスポンスバリデーション |

**インポート:**

| カテゴリ   | インポート元                  | 用途             |
| ---------- | ----------------------------- | ---------------- |
| Shared API | `@/shared/api/client`         | `clientApiFetch` |
| Contract   | `../contract/profileContract` | Zod スキーマ・型 |

**依存されている:**

- `modules/profile/model/useProfilePageModel.ts`

**エクスポート:**

- `fetchProfile()` - プロフィール取得 (404 時は `null`)
- `upsertProfile()` - プロフィール作成・更新

**レイヤー規約準拠:**

- ✅ `clientApiFetch` を使用（BFF 経由）
- ✅ Zod でレスポンスを parse（型安全）
- ✅ 境界でバリデーション実施

```
profileClient.ts
  ├── clientApiFetch (shared/api)
  └── profileContract (Contract)
        ├── ProfileSchema
        └── UpsertProfileSchema
```

---

### 5. `modules/profile/contract/profileContract.ts`

| レイヤー | Contract Layer                       |
| -------- | ------------------------------------ |
| 役割     | 型定義・Zod スキーマ（OpenAPI 対応） |

**インポート:**

- `zod` - スキーマ定義

**依存されている:**

- `modules/profile/model/useProfilePageModel.ts`
- `modules/profile/api/profileClient.ts`

**エクスポート:**

- `SexSchema` - 性別 enum スキーマ
- `ProfileSchema` - プロフィールレスポンススキーマ
- `UpsertProfileSchema` - 更新リクエストスキーマ
- `Sex`, `Profile`, `UpsertProfileInput` - 型定義

```
profileContract.ts (依存なし - リーフノード)
  └── zod
```

---

### 6. `shared/api/client.ts`

| レイヤー | Shared API Layer                                       |
| -------- | ------------------------------------------------------ |
| 役割     | クライアントサイド Fetch ラッパー（BFF `/api/*` 向け） |

**インポート:**

- なし（純粋な fetch ラッパー）

**依存されている:**

- `modules/profile/api/profileClient.ts`
- 他の Feature Module の API Client

**エクスポート:**

- `clientApiFetch<T>()` - 型付き fetch 関数
- `ClientApiOptions` - オプション型

**特徴:**

- `/api` プレフィックスを自動付与（BFF へルーティング）
- `no-store` キャッシュ戦略
- エラー時は `Error` をスロー

---

### 7. `app/api/profile/route.ts`

| レイヤー | BFF Layer            |
| -------- | -------------------- |
| 役割     | Backend へのプロキシ |

**インポート:**

| カテゴリ   | インポート元         | 用途             |
| ---------- | -------------------- | ---------------- |
| Next.js    | `next/server`        | `NextRequest`    |
| Shared API | `@/shared/api/proxy` | `proxyToBackend` |

**依存されている:**

- クライアントからの `/api/profile/me` リクエスト

**エクスポート:**

- `GET()` - プロフィール取得
- `PUT()` - プロフィール更新

**環境変数:**

- `BACKEND_INTERNAL_ORIGIN` (default: `http://127.0.0.1:8000`)
- `BACKEND_API_PREFIX` (default: `/api/v1`)
- `BACKEND_PROFILE_PATH` (default: `/profile`)

```
route.ts
  └── proxyToBackend (shared/api/proxy)
```

---

### 8. `shared/api/proxy.ts`

| レイヤー | Shared API Layer (Server-only)     |
| -------- | ---------------------------------- |
| 役割     | Backend へのプロキシユーティリティ |

**インポート:**

- `server-only` - サーバー専用マーカー
- `next/server` - `NextRequest`

**依存されている:**

- `app/api/profile/route.ts`
- 他の BFF Route Handler

**エクスポート:**

- `proxyToBackend()` - プロキシ関数

**特徴:**

- Cookie / Authorization ヘッダー転送
- Set-Cookie ヘッダー透過
- `server-only` によりクライアントインポート防止

---

## モジュール依存グラフ

```
                    ┌──────────────────────┐
                    │   External Deps      │
                    │ (react, zod, etc.)   │
                    └──────────────────────┘
                              ↑
    ┌─────────────────────────┼─────────────────────────┐
    │                         │                         │
    │  ┌──────────────────────┴──────────────────────┐  │
    │  │           profileContract.ts                │  │
    │  │  (SexSchema, ProfileSchema, types)          │  │
    │  └──────────────────────┬──────────────────────┘  │
    │                         │                         │
    │           ┌─────────────┴─────────────┐           │
    │           ↓                           ↓           │
    │  ┌────────────────┐          ┌────────────────┐   │
    │  │ profileClient  │←─────────│ shared/api/    │   │
    │  │    (API)       │          │   client.ts    │   │
    │  └───────┬────────┘          └────────────────┘   │
    │          │                                        │
    │          ↓                                        │
    │  ┌────────────────┐                               │
    │  │useProfilePage  │                               │
    │  │    Model       │                               │
    │  └───────┬────────┘                               │
    │          │                                        │
    │          ↓                                        │
    │  ┌────────────────┐          ┌────────────────┐   │
    │  │  ProfilePage   │←─────────│  shared/ui/    │   │
    │  │     (UI)       │          │   Status/*     │   │
    │  └───────┬────────┘          └────────────────┘   │
    │          │                                        │
    │          ↓                                        │
    │  ┌────────────────┐                               │
    │  │   page.tsx     │                               │
    │  │  (Next.js)     │                               │
    │  └────────────────┘                               │
    │                                                   │
    │               modules/profile/                    │
    └───────────────────────────────────────────────────┘
```

---

## BFF 側依存グラフ

```
    ┌─────────────────────────────────────────┐
    │           app/api/profile/              │
    │              route.ts                   │
    │  ┌───────────────────────────────────┐  │
    │  │  GET()  ─────┐                    │  │
    │  │              │                    │  │
    │  │  PUT()  ─────┼───→ proxyToBackend │  │
    │  │              │      (shared/api/  │  │
    │  │              ↓       proxy.ts)    │  │
    │  │    buildProfileBackendUrl()       │  │
    │  └───────────────────────────────────┘  │
    │                         │               │
    └─────────────────────────│───────────────┘
                              ↓
                    ┌─────────────────────┐
                    │  Backend (FastAPI)  │
                    │  /api/v1/profile    │
                    └─────────────────────┘
```

---

## データフロー詳細

### GET /profile/me（プロフィール取得）

```
1. ProfilePage → useProfilePageModel()
   │
2. useQuery({ queryFn: fetchProfile })
   │
3. fetchProfile() → clientApiFetch('/profile/me', { method: 'GET' })
   │
4. fetch('/api/profile/me') → Next.js Route Handler
   │
5. route.ts GET() → proxyToBackend(req, backendUrl)
   │
6. fetch('http://127.0.0.1:8000/api/v1/profile?...')
   │
7. Backend Response → Response 透過
   │
8. profileClient: ProfileSchema.parse(raw)
   │
9. useQuery: data = Profile | null
   │
10. ProfilePage: form.reset(m.defaults)
```

### PUT /profile/me（プロフィール更新）

```
1. ProfilePage: form.handleSubmit → m.save(values)
   │
2. useProfilePageModel.save()
   │  ├── ProfileFormSchema.parse(values) // 型変換
   │  └── upsertMutation.mutateAsync(parsed)
   │
3. upsertProfile(body) → UpsertProfileSchema.parse(body) // 境界バリデーション
   │
4. clientApiFetch('/profile/me', { method: 'PUT', body: safe })
   │
5. fetch('/api/profile/me') → Next.js Route Handler
   │
6. route.ts PUT() → proxyToBackend(req, backendUrl)
   │
7. Backend Response → Response 透過
   │
8. profileClient: ProfileSchema.parse(raw)
   │
9. useMutation.onSuccess → queryClient.invalidateQueries({ queryKey: qk.me })
   │
10. ProfilePage: router.push('/target')
```

---

## レイヤー準拠チェックリスト

| ルール                            | 状態 | 備考                                        |
| --------------------------------- | ---- | ------------------------------------------- |
| UI → PageModel のみ               | ✅   | ProfilePage は useProfilePageModel のみ使用 |
| UI から API 直接呼び出し禁止      | ✅   | profileClient をインポートしていない        |
| PageModel が Query/Mutation 所有  | ✅   | useQuery, useMutation を使用                |
| API Client は clientApiFetch 使用 | ✅   | shared/api/client.ts 経由                   |
| Contract で Zod スキーマ定義      | ✅   | ProfileSchema, UpsertProfileSchema          |
| BFF は server-only                | ✅   | proxy.ts に `import 'server-only'`          |
| Cookie/Set-Cookie 転送            | ✅   | proxy.ts で実装済み                         |

---

## ファイルサイズ・複雑度

| ファイル                 | 行数 | 責務                   |
| ------------------------ | ---- | ---------------------- |
| `page.tsx`               | 10   | ルーティングのみ       |
| `ProfilePage.tsx`        | 138  | UI + フォーム          |
| `useProfilePageModel.ts` | 61   | Model + Query          |
| `profileClient.ts`       | 38   | API 呼び出し           |
| `profileContract.ts`     | 31   | 型定義                 |
| `route.ts`               | 33   | BFF プロキシ           |
| `proxy.ts`               | 33   | プロキシユーティリティ |
| `client.ts`              | 31   | Fetch ラッパー         |

---

## まとめ

Profile モジュールは、プロジェクトのアーキテクチャ規約に準拠した実装となっています：

1. **レイヤー分離**: UI → Model → API → shared/api → BFF の依存方向が守られている
2. **型安全**: Zod スキーマによる境界バリデーションが各レイヤーで実施されている
3. **サーバー/クライアント分離**: `server-only` によりクライアントへの混入を防止
4. **Cookie 透過**: BFF でログインセッションの Cookie が正しく転送される
