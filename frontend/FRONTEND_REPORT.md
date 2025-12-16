# フロントエンドプロジェクト詳細レポート

## プロジェクト概要

**プロジェクト名**: Nutrition Lite  
**フレームワーク**: Next.js 16.0.7  
**React バージョン**: 19.2.0  
**言語**: TypeScript 5  
**パッケージマネージャー**: pnpm  
**スタイリング**: Tailwind CSS 4

栄養管理・追跡アプリケーションのフロントエンド実装。食事記録、栄養分析、レポート生成、目標設定などの機能を提供。

---

## 技術スタック

### コア技術

- **Next.js 16.0.7**: App Router を使用した React フレームワーク
- **React 19.2.0**: UI ライブラリ
- **TypeScript 5**: 型安全性を確保
- **Tailwind CSS 4**: ユーティリティファーストの CSS フレームワーク

### 主要ライブラリ

- **recharts 3.5.1**: 栄養情報の可視化（グラフ表示）
- **MSW (Mock Service Worker) 2.12.4**: API モック実装（開発環境用）

### 開発ツール

- **ESLint 9**: コード品質チェック
- **eslint-config-next**: Next.js 用 ESLint 設定

### フォント

- **Inter**: サンセリフフォント（メイン UI）
- **JetBrains Mono**: 等幅フォント（コード表示用）

---

## ディレクトリ構造

```
frontend/
├── app/                          # Next.js App Router ディレクトリ
│   ├── (app)/                    # 認証済みユーザー向けルートグループ
│   │   ├── billing/              # 課金・プラン管理
│   │   │   ├── plan/page.tsx
│   │   │   └── upgrade/page.tsx
│   │   ├── meals/                # 食事記録
│   │   │   └── page.tsx
│   │   ├── profile/               # プロフィール設定
│   │   │   └── page.tsx
│   │   ├── recommendations/      # 栄養推奨
│   │   │   └── today/page.tsx
│   │   ├── reports/              # レポート
│   │   │   └── daily/[date]/page.tsx
│   │   ├── targets/               # 目標設定
│   │   │   └── page.tsx
│   │   ├── layout.tsx            # アプリレイアウト（AppShell）
│   │   └── page.tsx              # ホーム（TodayPage）
│   ├── (onboarding)/             # オンボーディング用ルートグループ
│   │   └── onboarding/
│   │       ├── layout.tsx
│   │       ├── profile/page.tsx
│   │       └── target/page.tsx
│   ├── (public)/                 # 公開ルートグループ
│   │   └── auth/
│   │       ├── layout.tsx
│   │       ├── login/page.tsx
│   │       └── register/page.tsx
│   ├── layout.tsx                # ルートレイアウト
│   ├── globals.css               # グローバルスタイル
│   └── favicon.ico
│
├── components/                    # React コンポーネント
│   ├── auth/                     # 認証関連
│   │   ├── AuthCard.tsx
│   │   ├── LoginForm.tsx
│   │   └── RegisterForm.tsx
│   ├── billing/                  # 課金関連
│   │   ├── BillingPlanPage.tsx
│   │   └── BillingUpgradePage.tsx
│   ├── common/                    # 共通コンポーネント
│   │   └── UpgradeBanner.tsx
│   ├── layout/                    # レイアウトコンポーネント
│   │   ├── AppHeader.tsx
│   │   ├── AppShell.tsx
│   │   ├── AppSidebar.tsx
│   │   ├── NavLink.tsx
│   │   └── PageHeader.tsx
│   ├── meals/                     # 食事記録関連
│   │   ├── MainMealsSection.tsx
│   │   ├── MealItemDialog.tsx
│   │   ├── MealItemList.tsx
│   │   ├── MealItemRow.tsx
│   │   ├── MealNutritionChart.tsx
│   │   ├── MealsHeader.tsx
│   │   ├── MealSlotCard.tsx
│   │   ├── MealsPage.tsx
│   │   ├── SnackMealsSection.tsx
│   │   └── STRUCTURE.md          # コンポーネント構造ドキュメント
│   ├── mocks/                     # モック関連
│   │   └── MockProvider.tsx
│   ├── playground/                # 開発・実験用コンポーネント
│   │   ├── advanced-dashboard/    # 高度なダッシュボード実装
│   │   │   ├── AdvancedDashboard.tsx
│   │   │   ├── charts/
│   │   │   ├── data/
│   │   │   ├── features/
│   │   │   │   ├── command-palette/
│   │   │   │   ├── layout/
│   │   │   │   └── meals/
│   │   │   ├── hooks/
│   │   │   ├── lib/
│   │   │   ├── ui/
│   │   │   └── types.ts
│   │   ├── Layoutlab.tsx
│   │   ├── Playground.tsx
│   │   ├── RichUi.tsx
│   │   └── UiTest.tsx
│   ├── profile/                   # プロフィール関連
│   │   └── ProfileForm.tsx
│   ├── recommendations/           # 推奨関連
│   │   ├── PlanRestrictionNotice.tsx
│   │   ├── RecommendationCard.tsx
│   │   ├── RecommendationEmptyState.tsx
│   │   └── RecommendationsTodayPage.tsx
│   ├── reports/                   # レポート関連
│   │   ├── DailyReportCard.tsx
│   │   ├── DailyReportHeader.tsx
│   │   ├── DailyReportPage.tsx
│   │   ├── ReportActions.tsx
│   │   └── ReportSection.tsx
│   ├── targets/                   # 目標設定関連
│   │   ├── CreateTargetDialog.tsx
│   │   ├── CreateTargetForm.tsx
│   │   ├── TargetCard.tsx
│   │   ├── TargetList.tsx
│   │   └── TargetsPage.tsx
│   ├── today/                     # 今日のサマリー関連
│   │   ├── TodayHeader.tsx
│   │   ├── TodayMealsSummaryCard.tsx
│   │   ├── TodayPage.tsx
│   │   ├── TodayProgressCard.tsx
│   │   ├── TodayRecommendationPreviewCard.tsx
│   │   └── TodayReportPreviewCard.tsx
│   └── ui/                        # 基本 UI コンポーネント（shadcn/ui スタイル）
│       ├── badge.tsx
│       ├── button.tsx
│       ├── card.tsx
│       ├── input.tsx
│       └── label.tsx
│
├── lib/                           # ユーティリティ・ロジック
│   ├── api/                       # API クライアント
│   │   ├── auth.ts               # 認証 API
│   │   ├── billing.ts            # 課金 API
│   │   ├── client.ts             # 共通 API クライアント
│   │   ├── dailyReport.ts        # 日次レポート API
│   │   ├── meals.ts              # 食事 API
│   │   ├── nutrition.ts          # 栄養計算 API
│   │   ├── profile.ts            # プロフィール API
│   │   ├── recommendation.ts    # 推奨 API
│   │   ├── targets.ts            # 目標 API
│   │   └── today.ts              # 今日のサマリー API
│   ├── hooks/                     # カスタムフック
│   │   ├── useCurrentUser.ts     # 現在のユーザー取得
│   │   ├── useDailyReport.ts     # 日次レポート取得
│   │   ├── useMealsByDate.ts     # 日付別食事取得
│   │   ├── useTodayOverview.ts   # 今日のサマリー取得
│   │   └── useTodayRecommendation.ts  # 今日の推奨取得
│   ├── mocks/                     # MSW モック実装
│   │   ├── browser.ts            # ブラウザ環境用
│   │   ├── handlers.ts           # モックハンドラー
│   │   ├── index.ts              # モック有効化判定
│   │   ├── server.ts             # サーバー環境用（テスト）
│   │   └── README.md             # モック実装ガイド
│   └── utils.ts                   # 汎用ユーティリティ関数
│
├── types/                         # TypeScript 型定義
│   ├── auth.ts                   # 認証関連の型
│   ├── meal.ts                   # 食事関連の型
│   ├── nutrition.ts              # 栄養関連の型
│   ├── profile.ts                # プロフィール関連の型
│   ├── report.ts                 # レポート関連の型
│   └── target.ts                 # 目標関連の型
│
├── public/                        # 静的ファイル
│   ├── favicon.ico
│   ├── mockServiceWorker.js      # MSW Service Worker
│   └── *.svg                     # アイコン・画像
│
├── styles/                        # スタイルファイル
│   └── globals.css
│
├── .eslintrc.cjs                  # ESLint 設定
├── .gitignore                     # Git 除外設定
├── eslint.config.mjs              # ESLint 設定（新形式）
├── next.config.ts                 # Next.js 設定
├── next.config.mjs                # Next.js 設定（代替）
├── package.json                   # 依存関係・スクリプト
├── pnpm-lock.yaml                 # 依存関係ロックファイル
├── postcss.config.cjs             # PostCSS 設定
├── postcss.config.mjs             # PostCSS 設定（代替）
├── tailwind.config.cjs            # Tailwind CSS 設定
├── tsconfig.json                  # TypeScript 設定
└── README.md                      # プロジェクト説明
```

---

## ルーティング構造（Next.js App Router）

### ルートグループ

Next.js の Route Groups `()` を使用して、認証状態に応じたレイアウトを分離：

1. **`(app)`**: 認証済みユーザー向け

   - `AppShell` レイアウト（ヘッダー・サイドバー付き）
   - 認証チェック・リダイレクト機能

2. **`(onboarding)`**: 新規ユーザーオンボーディング

   - プロフィール設定・目標設定フロー

3. **`(public)`**: 公開ページ
   - 認証不要（ログイン・登録ページ）

### 主要ルート

| パス                     | 説明                           | コンポーネント             |
| ------------------------ | ------------------------------ | -------------------------- |
| `/`                      | ホーム（今日のサマリー）       | `TodayPage`                |
| `/meals`                 | 食事記録                       | `MealsPage`                |
| `/reports/daily/[date]`  | 日次レポート（動的）           | `DailyReportPage`          |
| `/targets`               | 目標設定                       | `TargetsPage`              |
| `/recommendations/today` | 今日の推奨                     | `RecommendationsTodayPage` |
| `/profile`               | プロフィール設定               | `ProfileForm`              |
| `/billing/plan`          | プラン一覧                     | `BillingPlanPage`          |
| `/billing/upgrade`       | プランアップグレード           | `BillingUpgradePage`       |
| `/auth/login`            | ログイン                       | `LoginForm`                |
| `/auth/register`         | 登録                           | `RegisterForm`             |
| `/onboarding/profile`    | オンボーディング：プロフィール | -                          |
| `/onboarding/target`     | オンボーディング：目標         | -                          |

---

## アーキテクチャパターン

### 1. コンポーネント設計

**階層構造**:

- **ページコンポーネント**: ルートに対応（`app/**/page.tsx`）
- **機能コンポーネント**: ビジネスロジックを含む（`components/**/*.tsx`）
- **UI コンポーネント**: 再利用可能な基本コンポーネント（`components/ui/*.tsx`）

**設計原則**:

- 単一責任の原則
- コンポーネントの分割（表示・ロジック分離）
- カスタムフックによるロジック抽出

### 2. データフェッチング

**カスタムフックパターン**:

```typescript
// lib/hooks/useTodayOverview.ts
const { data, isLoading, error } = useTodayOverview();
```

**特徴**:

- クライアントサイドでのデータ取得
- ローディング・エラー状態の管理
- 再取得機能（`refresh()`）

### 3. API クライアント

**統一された API クライアント** (`lib/api/client.ts`):

- `apiGet`, `apiPost`, `apiPut`, `apiPatch`, `apiDelete`
- エラーハンドリング（`ApiError` クラス）
- 環境変数によるベース URL 設定

**エンドポイント別モジュール**:

- `lib/api/auth.ts` - 認証
- `lib/api/meals.ts` - 食事
- `lib/api/nutrition.ts` - 栄養計算
- など

### 4. 状態管理

**現在のアプローチ**:

- React の `useState`, `useEffect` を使用
- カスタムフックによる状態カプセル化
- グローバル状態管理ライブラリは未使用

**例**:

- `useCurrentUser`: ユーザー情報の状態管理
- `useMealsByDate`: 食事データの状態管理

### 5. モックシステム（MSW）

**開発環境での API モック**:

- `NEXT_PUBLIC_USE_MOCK=true` で有効化
- Service Worker による HTTP インターセプト
- `lib/mocks/handlers.ts` でモックレスポンス定義

**利点**:

- バックエンド未実装でも開発可能
- テスト環境での再利用
- 実際の API との型整合性

---

## 主要コンポーネント詳細

### レイアウトコンポーネント

#### `AppShell` (`components/layout/AppShell.tsx`)

- **役割**: 認証済みユーザー向けのメインレイアウト
- **機能**:
  - 認証チェック（未認証時は `/auth/login` へリダイレクト）
  - `AppHeader`（ユーザー情報・プラン表示）
  - `AppSidebar`（ナビゲーション）
  - メインコンテンツエリア

#### `AppHeader` (`components/layout/AppHeader.tsx`)

- ユーザー名・プラン情報表示
- トライアル終了日表示
- ログアウト機能（予定）

#### `AppSidebar` (`components/layout/AppSidebar.tsx`)

- ナビゲーションメニュー
- アクティブルートのハイライト

### ページコンポーネント

#### `TodayPage` (`components/today/TodayPage.tsx`)

- **役割**: ホーム画面（今日のサマリー）
- **表示内容**:
  - `TodayProgressCard`: 栄養進捗
  - `TodayMealsSummaryCard`: 食事サマリー
  - `TodayReportPreviewCard`: レポートプレビュー
  - `TodayRecommendationPreviewCard`: 推奨プレビュー
  - `UpgradeBanner`: プランアップグレード案内（トライアル・無料プラン時）

#### `MealsPage` (`components/meals/MealsPage.tsx`)

- **役割**: 食事記録管理
- **主要機能**:
  - メイン食事（朝食・昼食・夕食など）の記録
  - 間食の記録
  - 栄養情報の計算・表示
  - 食事アイテムの追加・編集・削除
- **詳細**: `components/meals/STRUCTURE.md` を参照

#### `DailyReportPage` (`components/reports/DailyReportPage.tsx`)

- 日次レポートの表示
- 栄養分析・グラフ表示

#### `TargetsPage` (`components/targets/TargetsPage.tsx`)

- 栄養目標の設定・管理
- 目標カードの表示

### UI コンポーネント（shadcn/ui スタイル）

基本 UI コンポーネント（`components/ui/`）:

- `button.tsx`: ボタン
- `card.tsx`: カード
- `input.tsx`: 入力フィールド
- `label.tsx`: ラベル
- `badge.tsx`: バッジ

Tailwind CSS を使用したスタイリング。

---

## API クライアント詳細

### 共通クライアント (`lib/api/client.ts`)

**機能**:

- 統一された HTTP リクエスト関数
- エラーハンドリング
- JSON シリアライゼーション
- クレデンシャル（Cookie）の自動送信

**エラー処理**:

```typescript
class ApiError extends Error {
  status: number;
  body: unknown | ErrorPayload;
}
```

### エンドポイント一覧

| モジュール          | 主要関数                                                                       | 説明               |
| ------------------- | ------------------------------------------------------------------------------ | ------------------ |
| `auth.ts`           | `fetchMe()`, `login()`, `register()`                                           | 認証・ユーザー情報 |
| `meals.ts`          | `fetchMealItems()`, `createMealItem()`, `updateMealItem()`, `deleteMealItem()` | 食事記録 CRUD      |
| `nutrition.ts`      | `recomputeMealAndDailyNutrition()`                                             | 栄養計算           |
| `today.ts`          | `fetchTodayOverview()`                                                         | 今日のサマリー     |
| `dailyReport.ts`    | `fetchDailyReport()`                                                           | 日次レポート       |
| `targets.ts`        | `fetchTargets()`, `createTarget()`, `updateTarget()`, `deleteTarget()`         | 目標 CRUD          |
| `recommendation.ts` | `fetchTodayRecommendation()`                                                   | 推奨取得           |
| `profile.ts`        | `fetchProfile()`, `updateProfile()`                                            | プロフィール CRUD  |
| `billing.ts`        | `fetchPlans()`, `upgradePlan()`                                                | 課金・プラン管理   |

---

## カスタムフック

### `useCurrentUser`

- **用途**: 現在のユーザー情報取得
- **戻り値**: `{ user, isLoading }`
- **機能**: 未認証時は `user = null`

### `useTodayOverview`

- **用途**: 今日のサマリーデータ取得
- **戻り値**: `{ data, isLoading, error }`
- **データ内容**: 進捗・食事サマリー・レポートプレビュー・推奨プレビュー

### `useMealsByDate`

- **用途**: 指定日の食事データ取得
- **戻り値**: `{ data, isLoading, error, refresh }`
- **データ構造**: `MealsView`（メイン食事スロット・間食）

### `useDailyReport`

- **用途**: 日次レポート取得
- **戻り値**: `{ data, isLoading, error }`

### `useTodayRecommendation`

- **用途**: 今日の推奨取得
- **戻り値**: `{ data, isLoading, error }`

---

## スタイリング

### Tailwind CSS 4

**設定ファイル**: `tailwind.config.cjs`

**特徴**:

- ユーティリティファースト
- ダークモード対応（`slate-950` 背景）
- カスタムカラーパレット

**使用例**:

```tsx
<div className="min-h-screen bg-slate-950 text-slate-50">
  {/* ダークテーマ */}
</div>
```

### グローバルスタイル (`app/globals.css`)

- CSS 変数によるテーマ管理
- ダークモード対応（`@media (prefers-color-scheme: dark)`）
- フォント変数の定義

---

## 型定義

### 型定義ファイル（`types/`）

現在、型定義ファイルは空の状態。型は各 API モジュール内で定義されている可能性が高い。

**想定される型**:

- `User`, `CurrentUser` - ユーザー情報
- `MealItem`, `MealItemVM` - 食事アイテム
- `Nutrition`, `DailyNutrition` - 栄養情報
- `Target` - 目標
- `Report` - レポート
- `Recommendation` - 推奨

---

## 開発環境設定

### 環境変数

**必要な環境変数**:

- `NEXT_PUBLIC_API_BASE_URL`: API ベース URL（デフォルト: `/api/v1`）
- `NEXT_PUBLIC_USE_MOCK`: MSW モック有効化（`true`/`false`）

### スクリプト（`package.json`）

```json
{
  "dev": "next dev", // 開発サーバー起動
  "build": "next build", // 本番ビルド
  "start": "next start", // 本番サーバー起動
  "lint": "eslint" // リント実行
}
```

### TypeScript 設定

**`tsconfig.json` の特徴**:

- `baseUrl: "."` - 相対パス解決
- `paths: { "@/*": ["./*"] }` - `@/` エイリアス
- `strict: true` - 厳格な型チェック
- `jsx: "react-jsx"` - React 17+ JSX 変換

---

## モックシステム（MSW）

### セットアップ

1. **環境変数設定**: `NEXT_PUBLIC_USE_MOCK=true`
2. **Service Worker**: `public/mockServiceWorker.js`（自動生成）
3. **初期化**: `MockProvider` コンポーネントで自動初期化

### モックハンドラー

**ファイル**: `lib/mocks/handlers.ts`

**機能**:

- 各 API エンドポイントのモックレスポンス定義
- 開発環境でのバックエンド不要開発

### 使用方法

開発サーバー起動時に自動的に MSW が有効化され、コンソールに `✅ MSWモックが有効化されました` と表示される。

---

## パフォーマンス考慮事項

### 現在の実装

1. **クライアントサイドレンダリング**: ほとんどのページが `'use client'`
2. **データフェッチング**: `useEffect` によるクライアントサイド取得
3. **ローディング状態**: 各フックで個別管理

### 改善の余地

1. **Server Components**: Next.js の Server Components 活用
2. **データキャッシュ**: React Query や SWR の導入検討
3. **コード分割**: 動的インポートによる遅延読み込み
4. **画像最適化**: Next.js Image コンポーネントの活用

---

## セキュリティ考慮事項

### 認証

- Cookie ベースの認証（`credentials: 'include'`）
- `AppShell` での認証チェック
- 未認証時の自動リダイレクト

### API 通信

- HTTPS 推奨（本番環境）
- 環境変数による設定管理
- エラーハンドリング

---

## テスト

### 現在の状態

- テストフレームワークの設定なし
- MSW はテスト環境でも使用可能（`lib/mocks/server.ts`）

### 推奨されるテスト戦略

1. **単体テスト**: Jest + React Testing Library
2. **E2E テスト**: Playwright または Cypress
3. **MSW 活用**: API モックによるテスト

---

## 開発ワークフロー

### 推奨フロー

1. **開発環境起動**: `pnpm dev`
2. **モック有効化**: `.env.local` に `NEXT_PUBLIC_USE_MOCK=true`
3. **コンポーネント開発**: `components/` で実装
4. **API 統合**: `lib/api/` で API クライアント実装
5. **型定義**: `types/` または各モジュール内で定義

---

## 既知の課題・改善点

### コード品質

1. **型定義の整理**: `types/` ディレクトリが空 - 型定義の集約が必要
2. **エラーハンドリング**: より詳細なエラーメッセージ表示
3. **ローディング状態**: 統一されたローディング UI

### アーキテクチャ

1. **状態管理**: グローバル状態管理の検討（必要に応じて）
2. **データフェッチング**: React Query などの導入検討
3. **Server Components**: パフォーマンス向上のため活用検討

### UI/UX

1. **アクセシビリティ**: キーボード操作・スクリーンリーダー対応
2. **レスポンシブデザイン**: モバイル最適化の確認
3. **エラー表示**: ユーザーフレンドリーなエラーメッセージ

---

## ドキュメント

### 既存ドキュメント

1. **`components/meals/STRUCTURE.md`**: MealsPage コンポーネントの詳細構造
2. **`lib/mocks/README.md`**: MSW モック実装ガイド
3. **`README.md`**: 基本的な Next.js プロジェクト説明

### 追加推奨ドキュメント

1. **API 仕様書**: 各エンドポイントの詳細
2. **コンポーネント設計ガイド**: 新規コンポーネント作成時の指針
3. **デプロイメントガイド**: 本番環境へのデプロイ手順

---

## まとめ

このフロントエンドプロジェクトは、Next.js 16 の App Router を使用したモダンな React アプリケーションです。栄養管理アプリケーションとして、食事記録、栄養分析、レポート生成などの機能を提供しています。

**主な特徴**:

- ✅ TypeScript による型安全性
- ✅ Tailwind CSS によるモダンな UI
- ✅ MSW による開発環境での API モック
- ✅ カスタムフックによるロジックの再利用
- ✅ ルートグループによる認証状態の分離

**技術的成熟度**: 中〜高（基本的な機能は実装済み、最適化の余地あり）

---

_レポート作成日: 2024 年_  
_プロジェクトバージョン: 0.1.0_
