# Next.js フロントエンド

## このディレクトリについて

Next.js 16 (App Router) + React 19 ベースのフロントエンド。モジュラーアーキテクチャを採用。

## 技術スタック

- **フレームワーク**: Next.js 16, React 19, TypeScript 5
- **スタイリング**: TailwindCSS v4, Radix UI, shadcn/ui
- **状態管理**: TanStack React Query 5
- **フォーム**: react-hook-form + Zod
- **HTTP**: openapi-fetch, Axios
- **通知**: Sonner (トースト)
- **アイコン**: Lucide React
- **モック**: MSW (Mock Service Worker)

## 重要: 実装前に必読

- `docs/ai/DEPENDENCY_ANALYSIS`

## ディレクトリ構造

```
src/
├── app/                    # Next.js App Router
│   ├── (app)/             # 認証済みユーザー向けページ
│   ├── (onboarding)/      # オンボーディングフロー
│   ├── (public)/          # 公開ページ（ログイン等）
│   └── api/               # BFF API Routes（バックエンドへのプロキシ）
├── modules/               # 機能モジュール（ドメイン別）
│   ├── auth/              # 認証
│   ├── profile/           # プロフィール
│   ├── target/            # 栄養目標
│   ├── meal/              # 食事管理
│   ├── nutrition/         # 栄養計算
│   ├── today/             # 今日のサマリー
│   └── report/            # 日次レポート
├── components/ui/         # 共通UIコンポーネント（shadcn/ui）
├── shared/                # 共有ユーティリティ
│   ├── api/              # APIクライアント、プロキシ
│   ├── lib/              # ヘルパー、エラー処理、Query設定
│   ├── config/           # 環境変数
│   └── ui/               # 共通UIコンポーネント（Status等）
└── lib/                   # グローバルユーティリティ（cn関数等）
```

## モジュール構造

各モジュールは以下の構造に従う:

```
modules/{moduleName}/
├── api/                   # APIクライアント関数
│   └── {module}Client.ts  # fetch/post関数
├── model/                 # 状態管理・ビジネスロジック
│   └── use{Module}PageModel.ts  # TanStack Query hooks
├── ui/                    # Reactコンポーネント
│   └── {Module}Page.tsx   # ページコンポーネント
├── contract/              # 型定義・Zodスキーマ
│   └── {module}Contract.ts
└── index.ts               # Public exports
```

## コマンド

```bash
pnpm dev      # 開発サーバー起動 (localhost:3000)
pnpm build    # プロダクションビルド
pnpm start    # プロダクションサーバー起動
pnpm lint     # ESLint実行
```

## ルートグループ

| グループ       | パス             | 用途                 |
| -------------- | ---------------- | -------------------- |
| `(public)`     | `/auth/login`    | ログイン             |
|                | `/auth/register` | 新規登録             |
| `(onboarding)` | `/profile`       | プロフィール設定     |
|                | `/target`        | 目標設定             |
| `(app)`        | `/today`         | 今日のダッシュボード |
|                | `/billing/plan`  | 課金プラン           |

## API 通信パターン

### BFF (Backend for Frontend)

フロントエンドは直接バックエンドにアクセスせず、Next.js API Routes を経由する:

```
Client → /api/* (Next.js) → localhost:8000/api/v1/* (FastAPI)
```

### クライアントサイド API

```typescript
// shared/api/client.ts
import { clientApiFetch } from '@/shared/api/client';

// 使用例
const data = await clientApiFetch<SomeType>('/targets', {
  method: 'POST',
  body: { title: 'My Target' },
});
```

### サーバーサイド API (Server Components)

```typescript
// shared/api/bffServer.ts
import { bffServerFetch } from '@/shared/api/bffServer';

// Server Component内で使用
const profile = await bffServerFetch<Profile>('/profile/me');
```

## 状態管理パターン

### TanStack Query

```typescript
// Query Keys (shared/lib/query/keys.ts)
const qk = {
  target: {
    current: () => ['target', 'current'],
    list: () => ['target', 'list'],
  },
};

// Custom Hook (modules/target/model/useTargetPageModel.ts)
export function useTargetPageModel() {
  const query = useQuery({
    queryKey: qk.target.current(),
    queryFn: () => fetchActiveTarget(),
  });

  const mutation = useMutation({
    mutationFn: createTarget,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: qk.target.list() });
    },
  });

  return { query, mutation };
}
```

## フォームパターン

```typescript
// 1. Contract定義 (contract/targetContract.ts)
export const CreateTargetSchema = z.object({
  title: z.string().min(1, '必須'),
  goal_type: GoalTypeSchema,
});
export type CreateTargetRequest = z.infer<typeof CreateTargetSchema>;

// 2. UI Component (ui/TargetForm.tsx)
('use client');

export function TargetForm() {
  const form = useForm<CreateTargetRequest>({
    resolver: zodResolver(CreateTargetSchema),
    defaultValues: { title: '', goal_type: 'maintain' },
  });

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <Input {...form.register('title')} />
      {form.formState.errors.title && (
        <span>{form.formState.errors.title.message}</span>
      )}
      <Button type="submit" disabled={form.formState.isSubmitting}>
        保存
      </Button>
    </form>
  );
}
```

## エラーハンドリング

```typescript
// shared/lib/errors.ts
type ApiErrorKind =
  | 'unauthorized' // 401
  | 'forbidden' // 403
  | 'not_found' // 404
  | 'validation' // 400, 422
  | 'server' // 5xx
  | 'network'
  | 'unknown';

// 使用例
try {
  await clientApiFetch('/some-endpoint');
} catch (e) {
  if (e instanceof ApiError && e.kind === 'unauthorized') {
    router.push('/auth/login');
  }
}
```

## UI コンポーネント (shadcn/ui)

`components/ui/` に以下のコンポーネントが用意されている:

- `Button` - バリアント: default, destructive, outline, secondary, ghost, link
- `Card` - CardHeader, CardContent, CardTitle
- `Input`, `Textarea`, `Label`
- `Select` - Radix UI ベース
- `Progress` - プログレスバー
- `Alert`, `Skeleton`, `Separator`

### ユーティリティ

```typescript
// lib/utils.ts
import { cn } from '@/lib/utils';

// クラス名の結合（clsx + tailwind-merge）
<div className={cn('p-4', isActive && 'bg-primary')} />;
```

## 共通 UI コンポーネント

```typescript
// shared/ui/Status/LoadingState.tsx
<LoadingState />  // ローディングスケルトン

// shared/ui/Status/ErrorState.tsx
<ErrorState
  title="エラーが発生しました"
  message="再試行してください"
  onRetry={() => refetch()}
/>

// shared/ui/EmptyState.tsx
<EmptyState message="データがありません" />
```

## 認証フロー

### サーバーサイド認証チェック

```typescript
// (onboarding)/layout.tsx
export default async function OnboardingLayout({ children }) {
  const ok = await fetchCurrentUserServer()
    .then(() => true)
    .catch(() => false);

  if (!ok) redirect('/auth/login');
  return children;
}
```

### クライアントサイドログイン

```typescript
// modules/auth/model/useLoginPageModel.ts
const mutation = useMutation({
  mutationFn: ({ email, password }) => login({ email, password }),
  onSuccess: () => router.replace('/profile'),
});
```

## 環境変数

```bash
# .env.local
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1  # オプション（デフォルト: 同一オリジン）
NEXT_PUBLIC_USE_MOCK=true                              # MSWモック有効化
NEXT_PUBLIC_API_MOCKING=enabled                        # APIモッキング
BACKEND_INTERNAL_ORIGIN=http://127.0.0.1:8000          # サーバーサイド用
```

## パスエイリアス

```typescript
// tsconfig.json で設定済み
import { Button } from '@/components/ui/button'; // src/components/ui/button
import { cn } from '@/lib/utils'; // src/lib/utils
```

## 新規モジュール実装の流れ

1. **contract/**: Zod スキーマと型定義
2. **api/**: API クライアント関数
3. **model/**: TanStack Query hooks (useXxxPageModel)
4. **ui/**: React コンポーネント
5. **index.ts**: Public exports
6. **app/**: ページ統合 (route.tsx, page.tsx)

## BFF API Route 実装例

```typescript
// app/api/targets/route.ts
import { proxyToBackend } from '@/shared/api/proxy';

const BACKEND = process.env.BACKEND_INTERNAL_ORIGIN ?? 'http://127.0.0.1:8000';
const PREFIX = '/api/v1';

export async function GET(req: NextRequest) {
  return proxyToBackend(
    req,
    `${BACKEND}${PREFIX}/targets${req.nextUrl.search}`
  );
}

export async function POST(req: NextRequest) {
  return proxyToBackend(req, `${BACKEND}${PREFIX}/targets`);
}
```
