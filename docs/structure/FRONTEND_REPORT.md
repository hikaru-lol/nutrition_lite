# フロントエンド構成・構造レポート

## プロジェクト概要

**プロジェクト名**: Nutrition Lite  
**フレームワーク**: Next.js 16.0.7（App Router）  
**React バージョン**: 19.2.0  
**言語**: TypeScript 5  
**パッケージマネージャー**: pnpm  
**スタイリング**: Tailwind CSS 4

栄養管理・追跡アプリケーションのフロントエンド実装。食事記録、栄養分析、レポート生成、目標設定、課金関連 UI を提供。

---

## 技術スタック

### コア技術

- **Next.js 16.0.7**: App Router を使用した React フレームワーク
- **React 19.2.0**: UI ライブラリ
- **TypeScript 5**: 型安全性を確保
- **Tailwind CSS 4**: ユーティリティファーストの CSS フレームワーク

### 主要ライブラリ / ツール

- **recharts 3.5.1**: 栄養情報の可視化（グラフ表示）
- **MSW 2.12.4**: API モック（開発用）
- **ESLint 9 + eslint-config-next**: コード品質チェック

### フォント

- **Inter**（本文）
- **JetBrains Mono**（コード表示系）

---

## ディレクトリ構成（抜粋）

```
frontend/
├── app/                           # Next.js App Router
│   ├── (app)/                     # 認証済みルートグループ
│   │   ├── billing/plan/page.tsx
│   │   ├── billing/upgrade/page.tsx
│   │   ├── meals/page.tsx
│   │   ├── profile/page.tsx
│   │   ├── recommendations/today/page.tsx
│   │   ├── reports/daily/[date]/page.tsx
│   │   ├── targets/page.tsx
│   │   ├── layout.tsx             # AppShell と Playground 切替の起点
│   │   └── page.tsx               # ホーム（Today）
│   ├── (onboarding)/onboarding/
│   │   ├── layout.tsx
│   │   ├── profile/page.tsx
│   │   └── target/page.tsx
│   ├── (public)/auth/
│   │   ├── layout.tsx
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── layout.tsx                 # ルートレイアウト（フォント / MSW）
│   ├── globals.css
│   └── favicon.ico
│
├── components/                     # 画面・機能・UI コンポーネント
│   ├── auth/                       # 認証フォーム
│   ├── billing/                    # 課金関連
│   ├── layout/                     # AppShell / Header / Sidebar 等
│   ├── meals/                      # 食事記録 UI
│   ├── recommendations/            # 推奨 UI
│   ├── reports/                    # レポート UI
│   ├── targets/                    # 目標設定 UI
│   ├── today/                      # ホームサマリー UI
│   ├── mocks/                      # MSW 初期化
│   ├── playground/                 # UI 実験領域（advanced-dashboard 等）
│   └── ui/                         # ベース UI（badge/button/card 等）
│
├── lib/
│   ├── api/                        # API クライアント群
│   ├── hooks/                      # データ取得・状態管理フック
│   ├── mocks/                      # MSW 設定
│   └── utils.ts
│
├── types/                          # ドメイン型定義
├── public/                         # 静的ファイル / mockServiceWorker.js
├── styles/                         # 追加の CSS（globals.css）
└── 各種設定ファイル（Next.js, Tailwind, TS, ESLint, PostCSS）
```

---

## ルーティング構造（Next.js App Router）

### ルートグループ

- **`(app)`**: 認証済みユーザー向け。`AppShell` を通して共通レイアウトを提供。
- **`(onboarding)`**: 新規ユーザー向けのプロフィール・目標設定フロー。
- **`(public)`**: ログイン / 登録など公開ルート。

### 主要ルート

| パス                     | 役割                             |
| ------------------------ | -------------------------------- |
| `/`                      | ホーム（今日のサマリー）         |
| `/meals`                 | 食事記録                         |
| `/reports/daily/[date]`  | 日次レポート（動的）             |
| `/targets`               | 目標設定                         |
| `/recommendations/today` | 今日の推奨                       |
| `/profile`               | プロフィール                     |
| `/billing/plan`          | プラン一覧                       |
| `/billing/upgrade`       | プランアップグレード             |
| `/auth/login`            | ログイン                         |
| `/auth/register`         | 登録                             |
| `/onboarding/profile`    | オンボーディング：プロフィール   |
| `/onboarding/target`     | オンボーディング：目標           |

---

## アーキテクチャ / 実装の特徴

### コンポーネント構成

- **ページ**: `app/**/page.tsx`
- **画面・機能 UI**: `components/**`
- **共通 UI**: `components/ui/*`
- **Playground**: `components/playground/*`（実験的 UI・ダッシュボード）

### データ取得

- `lib/hooks/*` にカスタムフックを集約（例: `useTodayOverview`, `useMealsByDate`）
- ローディング / エラーハンドリングをフック側で吸収

### API クライアント

- `lib/api/client.ts` に HTTP 基盤ロジックを集約
- 目的別に `lib/api/*` で分割（auth / meals / nutrition / targets など）

### モック（MSW）

- `NEXT_PUBLIC_USE_MOCK=true` で有効化
- `lib/mocks/*` と `components/mocks/MockProvider.tsx` で初期化
- `public/mockServiceWorker.js` を使用

---

## スクリプト / 設定

### npm scripts

- `pnpm dev` / `pnpm build` / `pnpm start` / `pnpm lint`

### 設定ファイル

- Next.js: `next.config.ts`, `next.config.mjs`
- Tailwind / PostCSS: `tailwind.config.cjs`, `postcss.config.cjs`, `postcss.config.mjs`
- TypeScript: `tsconfig.json`
- ESLint: `.eslintrc.cjs`, `eslint.config.mjs`

---

## 参照ドキュメント

- `components/meals/STRUCTURE.md`: Meals UI の詳細構造
- `lib/mocks/README.md`: MSW モック実装ガイド
- `README.md`: Next.js 標準の導入説明
