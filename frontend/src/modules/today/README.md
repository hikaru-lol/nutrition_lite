# TodayPage リファクタリング - 新アーキテクチャ

## 概要

TodayPageのリファクタリングにより、630行のmonoliticな実装から、Context + Hooks パターンによる各ドメインの分離が完了しました。

## アーキテクチャ

### Before (Legacy)
```
TodayPage.tsx (630行)
└── useTodayPageModel.ts (monolithic hook)
    ├── 食事管理
    ├── 目標管理
    ├── 栄養分析
    ├── レポート生成
    ├── プロフィール
    └── モーダル管理
```

### After (New Architecture)
```
TodayPage.tsx (55行)
├── TodayPageLayout.tsx (段階的移行)
└── TodayPageProvider (Context)
    ├── useTodayMeals.ts (180行)
    ├── useTodayTargets.ts (160行)
    ├── useTodayNutrition.ts (170行)
    ├── useTodayReports.ts (150行)
    ├── useTodayProfile.ts (80行)
    ├── useTodayModals.ts (140行)
    └── useTodayPageData.ts (統合)
```

## 主な利点

### 1. 責任の分離 (Single Responsibility Principle)
- **食事管理**: CRUD操作、バリデーション、エラーハンドリング
- **目標管理**: 栄養目標、進捗計算、日次サマリー
- **栄養分析**: キャッシュ付き分析、レコメンデーション
- **レポート管理**: AI生成、バリデーション、状態管理
- **プロフィール**: 基本情報、設定値の提供
- **モーダル管理**: 状態管理、イベントハンドリング

### 2. Context + Hooks パターン
```typescript
// Context経由での状態共有
const meals = useTodayMeals();
const targets = useTodayTargets();
const nutrition = useTodayNutrition();

// プロップドリリングの排除
<MealListSection /> // propsなしでContext経由でデータアクセス
```

### 3. 型安全性の向上
```typescript
// 各ドメインの明確な型定義
export interface TodayMealsModel extends TodayMealsState, TodayMealsActions {}
export interface TodayTargetsModel extends TodayTargetsState, TodayTargetsActions {}
// 統合Context型
export interface TodayPageContextValue {
  meals: TodayMealsModel;
  targets: TodayTargetsModel;
  // ...
}
```

### 4. 段階的移行システム
```typescript
// 機能フラグによる段階的移行
interface MigrationFlags {
  useDailySummarySection: boolean;
  useMealListSection: boolean;
  // ...
}
```

## ファイル構成

### 📁 lib/
- **queryKeys.ts** - 階層化されたReact Queryキー管理

### 📁 types/
- **todayTypes.ts** - 全ドメインの型定義とインターフェース

### 📁 context/
- **TodayPageContext.tsx** - Context定義とProvider実装

### 📁 model/ (Domain Hooks)
- **useTodayMeals.ts** - 食事管理ドメイン (180行)
- **useTodayTargets.ts** - 目標管理ドメイン (160行)
- **useTodayNutrition.ts** - 栄養分析ドメイン (170行)
- **useTodayReports.ts** - レポート管理ドメイン (150行)
- **useTodayProfile.ts** - プロフィールドメイン (80行)
- **useTodayModals.ts** - モーダル管理ドメイン (140行)
- **useTodayPageData.ts** - ドメイン統合フック (120行)

### 📁 ui/
#### sections/ (セクションコンポーネント)
- **DailySummarySection.tsx** - 日次サマリー表示
- **MealListSection.tsx** - 食事リスト管理
- **TargetProgressSection.tsx** - 目標進捗表示
- **DailyReportSection.tsx** - レポート管理
- **TodayModalsContainer.tsx** - モーダル統合

#### レイアウト・統合
- **TodayPageLayout.tsx** - 段階的移行レイアウト
- **TodayPageMigrationTest.tsx** - 移行テスト用コンポーネント
- **TodayPageTest.tsx** - Context統合テスト

## 使用方法

### 基本的な使用
```typescript
import { TodayPageProvider, useTodayMeals, useTodayTargets } from '@/modules/today';

// Provider でラップ
<TodayPageProvider date="2024-01-01">
  <MyComponent />
</TodayPageProvider>

// コンポーネント内でhooks使用
function MyComponent() {
  const meals = useTodayMeals();
  const targets = useTodayTargets();

  return (
    <div>
      <p>食事数: {meals.items.length}</p>
      <p>目標: {targets.activeTarget?.title}</p>
    </div>
  );
}
```

### 新アーキテクチャの有効化
```bash
# 環境変数で新アーキテクチャを有効化
NEXT_PUBLIC_USE_NEW_TODAY_ARCHITECTURE=true

# 個別機能フラグ（開発・テスト用）
NEXT_PUBLIC_TODAY_MIGRATION_FLAGS='{"useDailySummarySection":true}'
```

### セクションコンポーネントの使用
```typescript
import {
  DailySummarySection,
  MealListSection,
  TargetProgressSection
} from '@/modules/today';

<TodayPageProvider date={date}>
  <DailySummarySection />
  <MealListSection />
  <TargetProgressSection />
</TodayPageProvider>
```

## パフォーマンス最適化

### 1. React Query キャッシュ戦略
```typescript
// 階層化キー構造
todayQueryKeys = {
  all: (date) => ['today', date],
  meals: (date) => [...todayQueryKeys.all(date), 'meals'],
  targets: (date) => [...todayQueryKeys.all(date), 'targets'],
  // ...
}
```

### 2. メモリベース栄養分析キャッシュ
```typescript
// 重複計算の回避
const nutritionCache = new Map<string, any>();
const cacheKey = `${meal_type}_${meal_index || 'all'}`;
```

### 3. 依存関係の最適化
```typescript
// 必要なドメインのみを依存
const reports = useTodayReports({
  date,
  mealItemsCount: meals.items.length,
  mealsPerDay: profile.mealsPerDay
});
```

## 移行戦略

### Phase 1: インフラ構築 ✅
- クエリキー階層化
- 型定義整備

### Phase 2: ドメイン分離 ✅
- 6つのドメインフックに分割
- 各ドメインの責任明確化

### Phase 3: Context統合 ✅
- Provider実装
- 統合データフック

### Phase 4: セクションコンポーネント ✅
- 5つのセクションコンポーネント作成
- バリエーション実装

### Phase 5: 段階的移行 ✅
- 機能フラグシステム
- ハイブリッドレイアウト
- テストコンポーネント

### Phase 6: 完全移行 🔄
- レガシーコード削除
- 最終最適化
- ドキュメント整備

## トラブルシューティング

### よくある問題

1. **Provider外でのhook使用**
```
Error: useTodayPageContext must be used within TodayPageProvider
```
→ TodayPageProviderでコンポーネントをラップしてください

2. **型エラー**
```typescript
// 正しい型import
import type { TodayMealsModel } from '@/modules/today';
```

3. **キャッシュの問題**
```typescript
// キャッシュクリア
queryClient.invalidateQueries({ queryKey: todayQueryKeys.all(date) });
```

## 今後の拡張

### 1. 追加ドメイン
- レコメンデーション管理
- 分析・統計
- 通知管理

### 2. パフォーマンス向上
- 仮想化対応
- ワーカーでの重い処理
- ストリーミング対応

### 3. テスト整備
- ドメインhookの単体テスト
- Context統合テスト
- E2Eテスト

## 開発者向け情報

### デバッグツール
```typescript
// 開発時のデバッグコンポーネント
<TodayPageMigrationTest />  // 移行テスト
<TodayPageTest />          // Context統合テスト
<ModalStatusIndicator />   // モーダル状態表示
```

### パフォーマンス測定
```typescript
// 開発時のパフォーマンス情報
console.log('TodayPage Context 完全ダンプ:', context);
```

---

**最終更新**: 2026-02-04
**アーキテクト**: Claude (AI Assistant)
**ステータス**: Phase 6 進行中