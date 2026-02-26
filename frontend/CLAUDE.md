# Next.js フロントエンド

## このディレクトリについて

Next.js 16 (App Router) + React 19 ベースのフロントエンド。5層レイヤードアーキテクチャを採用。栄養管理アプリケーションのUIを担当し、レスポンシブデザイン、ダークモード対応、リアルタイム更新を実現。

## 技術スタック

- **フレームワーク**: Next.js 16, React 19, TypeScript 5
- **スタイリング**: TailwindCSS v4, Radix UI, shadcn/ui
- **状態管理**: TanStack React Query 5
- **フォーム**: react-hook-form + Zod
- **HTTP**: openapi-fetch, Axios
- **通知**: Sonner (トースト)
- **アイコン**: Lucide React
- **モック**: MSW (Mock Service Worker)
- **パッケージマネージャ**: pnpm
- **コード品質**: ESLint, Prettier
- **CI/CD**: GitHub Actions, Vercel


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
│   ├── billing/           # 課金・サブスクリプション
│   ├── calendar/          # カレンダー機能
│   ├── meal/              # 食事管理
│   ├── meal-recommendation/ # AI食事推薦
│   ├── nutrition/         # 栄養計算
│   ├── nutrition-progress/# 栄養進捗
│   ├── profile/           # プロフィール
│   ├── target/            # 栄養目標
│   ├── today/             # 今日のサマリー
│   └── tutorial/          # チュートリアル
├── components/ui/         # 共通UIコンポーネント（shadcn/ui）
├── shared/                # 共有ユーティリティ
│   ├── api/              # APIクライアント、プロキシ
│   ├── lib/              # ヘルパー、エラー処理、Query設定
│   ├── config/           # 環境変数
│   └── ui/               # 共通UIコンポーネント（Status等）
└── lib/                   # グローバルユーティリティ（cn関数等）
```

## アーキテクチャ: 5層レイヤードアーキテクチャ

このプロジェクトは5層レイヤードアーキテクチャを採用しています:

```
┌─────────────────────────────────────────┐
│ Layer 1: UI Presentation                │ ← 純粋な表現
├─────────────────────────────────────────┤
│ Layer 2: UI Orchestration               │ ← UI協調
├─────────────────────────────────────────┤
│ Layer 3: Page Aggregation               │ ← ページ集約
├─────────────────────────────────────────┤
│ Layer 4: Feature Logic                  │ ← 機能ロジック
├─────────────────────────────────────────┤
│ Layer 5: Domain Services                │ ← ドメインサービス
└─────────────────────────────────────────┘
```

### モジュール構造

各モジュールは5層アーキテクチャに従った構造:

```
modules/{moduleName}/
├── services/                  # Layer 5: Domain Services
│   └── {module}Service.ts
├── hooks/                     # Layer 4: Feature Logic
│   └── use{Module}Feature.ts
├── model/                     # Layer 3: Page Aggregation
│   └── use{Module}PageModel.ts
├── ui/                        # Layer 2 & 1: UI
│   ├── {Module}Page.tsx       # Layer 2: Orchestration
│   ├── {Module}PageContent.tsx # Layer 2: Orchestration
│   └── sections/              # Layer 1: Presentation
│       └── {Feature}Section.tsx
├── contract/                  # 型定義・スキーマ
│   └── {module}Contract.ts
├── api/                       # APIクライアント
│   └── {module}Client.ts
└── index.ts                   # Public exports
```

### 層別の責務

- **Layer 5**: 外部API呼び出し、ドメイン固有のビジネスロジック、データ変換
- **Layer 4**: React Queryによる状態管理、非同期データフェッチング協調、UI向けデータ統合
- **Layer 3**: ページレベルでの複数機能統合、ページ状態の一元管理、機能間の協調
- **Layer 2**: UIコンポーネント間の協調、イベントハンドリング、モーダル・フォーム状態管理
- **Layer 1**: 純粋な表現コンポーネント、propsによる制御、再利用可能なUI部品

## コマンド

```bash
# 依存関係管理
pnpm install              # 依存関係インストール
pnpm add <package>        # パッケージ追加

# 開発
pnpm dev                  # 開発サーバー起動 (localhost:3000)
pnpm dev:mock             # MSWモック有効で起動

# ビルド
pnpm build                # プロダクションビルド
pnpm start                # プロダクションサーバー起動

# コード品質
pnpm lint                 # ESLint実行
pnpm lint:fix             # ESLint自動修正
pnpm format               # Prettierフォーマット
pnpm type-check           # TypeScript型チェック
```

## ルートグループ & ページ

### 公開ページ `(public)`
- `/auth/login` - ログインページ（デモアカウント機能付き）
- `/auth/register` - 新規アカウント登録

### オンボーディング `(onboarding)`
- `/profile` - プロフィール初期設定
- `/target` - 栄養目標設定
- `/tutorial` - チュートリアル

### メインアプリ `(app)`
- `/today` - 今日のダッシュボード（ホーム）
- `/meal` - 食事記録管理
- `/targets` - 栄養目標一覧・編集
- `/calendar` - カレンダービュー
- `/meal-recommendation` - AI食事推薦
- `/billing/plan` - 課金プラン選択
- `/billing/success` - 決済完了ページ
- `/settings` - 設定ページ

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

## 状態管理パターン（5層アーキテクチャ）

### Layer 5: Domain Services
```typescript
// services/targetService.ts
export class TargetService {
  async getActiveTarget(): Promise<Target> {
    // 純粋なAPI呼び出し + データ変換
    const response = await fetchActiveTarget();
    return this.normalizeTargetData(response);
  }
}

export function useTargetService(): TargetService {
  return useMemo(() => new TargetService(), []);
}
```

### Layer 4: Feature Logic
```typescript
// hooks/useTargetManagement.ts
export function useTargetManagement(): TargetManagementModel {
  const targetService = useTargetService();

  const activeTargetQuery = useQuery({
    queryKey: ['targets', 'active'],
    queryFn: () => targetService.getActiveTarget(),
  });

  const createMutation = useMutation({
    mutationFn: targetService.createTarget,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['targets'] });
    },
  });

  return {
    activeTarget: activeTargetQuery.data,
    isLoading: activeTargetQuery.isLoading,
    createTarget: createMutation.mutateAsync,
  };
}
```

### Layer 3: Page Aggregation
```typescript
// model/useTargetPageModel.ts
export function useTargetPageModel() {
  const targets = useTargetManagement();
  const nutrition = useNutritionProgress();

  // ページレベルの協調ロジック
  const handleTargetUpdate = useCallback(async (data) => {
    await targets.createTarget(data);
    // 目標更新後に栄養進捗も再計算
    nutrition.refetch();
  }, [targets, nutrition]);

  return {
    targets,
    nutrition,
    handleTargetUpdate,
    isLoading: targets.isLoading || nutrition.isLoading,
  };
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

### フォーム関連
- `Button` - バリアント: default, destructive, outline, secondary, ghost, link
- `Input`, `Textarea` - テキスト入力
- `Label` - フォームラベル
- `Select` - ドロップダウン選択
- `RadioGroup` - ラジオボタングループ
- `Checkbox` - チェックボックス
- `Form` - react-hook-form統合

### レイアウト
- `Card` - CardHeader, CardContent, CardTitle, CardFooter
- `Dialog` - モーダルダイアログ
- `Drawer` - ドロワー
- `Tabs` - タブコンテナ
- `Separator` - 区切り線

### フィードバック
- `Alert` - アラート表示
- `Progress` - プログレスバー
- `Skeleton` - ローディングスケルトン
- `Toast` - トースト通知（Sonner）
- `Badge` - バッジ表示

### ナビゲーション
- `DropdownMenu` - ドロップダウンメニュー
- `NavigationMenu` - ナビゲーションメニュー
- `Breadcrumb` - パンくずリスト

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

## 主要機能

### 食事管理
- **記録**: 朝食・昼食・夕食・間食の登録
- **編集・削除**: リアルタイムでの食事内容更新
- **栄養計算**: 自動的な栄養素計算と表示
- **カレンダー表示**: 月次での記録状況確認

### AI機能連携
- **栄養推定**: 食事名から自動栄養情報取得
- **日次レポート**: AIによる1日の振り返り
- **食事推薦**: 個人目標に基づく最適な食事提案
- **目標生成**: プロフィール情報から最適目標を自動生成

### 進捗トラッキング
- **リアルタイム更新**: 食事追加時の即座な進捗反映
- **視覚的表現**: プログレスバーとパーセンテージ表示
- **色分け表示**: 達成度に応じた色変化（緑/黄/赤）

### サブスクリプション管理
- **プラン選択**: 月額・年額プランの選択UI
- **Stripe決済**: セキュアな決済フロー
- **ポータル管理**: サブスクリプション状況確認

### レスポンシブデザイン
- **モバイル対応**: スマートフォン最適化UI
- **タブレット対応**: 中間サイズデバイス対応
- **デスクトップ**: フル機能表示

### ダークモード
- **自動切り替え**: システム設定に追従
- **手動切り替え**: ユーザー選択保存
- **一貫性**: 全画面でのテーマ適用

## 環境変数

```bash
# .env.local
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1  # オプション（デフォルト: 同一オリジン）
NEXT_PUBLIC_USE_MOCK=true                              # MSWモック有効化
NEXT_PUBLIC_API_MOCKING=enabled                        # APIモッキング
BACKEND_INTERNAL_ORIGIN=http://127.0.0.1:8000          # サーバーサイド用

# デモアカウント情報（ログイン画面で利用可能）
# Email: demo@example.com
# Password: demo1234demo
```

## パスエイリアス

```typescript
// tsconfig.json で設定済み
import { Button } from '@/components/ui/button'; // src/components/ui/button
import { cn } from '@/lib/utils'; // src/lib/utils
```

## 新規モジュール実装の流れ（5層アーキテクチャ）

### 新機能開発時の順序

1. **contract/**: Zod スキーマと型定義
2. **api/**: API クライアント関数
3. **Layer 5**: services/ - ドメインサービス作成
4. **Layer 4**: hooks/ - フィーチャーロジックフック作成
5. **Layer 3**: model/ - ページ集約モデル統合
6. **Layer 1**: ui/sections/ - プレゼンテーションコンポーネント
7. **Layer 2**: ui/ - UIオーケストレーション
8. **index.ts**: Public exports
9. **app/**: ページ統合

### 既存機能リファクタリング時の順序

1. **現状分析**: 既存の責務分散状況を分析
2. **移行計画**: 段階的移行計画を策定
3. **Layer 1から開始**: 表現層から始めて段階的に下位層をリファクタ
4. **並行稼働検証**: 新旧実装を並行稼働させて検証

### 段階的移行戦略

- **部分移行**: 特定の機能・コンポーネントから段階的に適用
- **並行稼働**: 既存システムを壊さずに新アーキテクチャを検証
- **漸進的改善**: 一度に全体を書き換えるのではなく、継続的に改善

## BFF API Routes

### 実装されているAPI Routes

| パス | 対応バックエンドAPI | 説明 |
|------|-------------------|------|
| `/api/auth/*` | `/api/v1/auth/*` | 認証関連（login, register, logout, refresh） |
| `/api/profile/*` | `/api/v1/profile/*` | プロフィール管理 |
| `/api/targets/*` | `/api/v1/targets/*` | 栄養目標管理 |
| `/api/meal-items/*` | `/api/v1/meals/*` | 食事記録管理 |
| `/api/nutrition/*` | `/api/v1/nutrition/*` | 栄養計算 |
| `/api/calendar/*` | `/api/v1/calendar/*` | カレンダー記録 |
| `/api/meal-recommendations/*` | `/api/v1/recommendations/*` | AI食事推薦 |
| `/api/billing/*` | `/api/v1/billing/*` | Stripe課金 |
| `/api/tutorials/*` | `/api/v1/tutorial/*` | チュートリアル |
| `/api/today/*` | `/api/v1/daily-reports/*` | 日次レポート |

### 実装例

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

### Cookie中継

BFF層では認証Cookieを自動的に中継:
- `ACCESS_TOKEN` - アクセストークン
- `REFRESH_TOKEN` - リフレッシュトークン
- HttpOnly, SameSite=Lax設定で XSS対策
