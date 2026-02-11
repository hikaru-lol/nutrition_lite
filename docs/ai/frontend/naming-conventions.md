# フロントエンド命名規則ガイド

**最終更新**: 2026-02-07

このドキュメントは、フロントエンドの5層アーキテクチャにおける命名規則を定義します。

---

## 目次

1. [概要](#概要)
2. [Layer 5: Domain Services](#layer-5-domain-services)
3. [Layer 4: Feature Logic](#layer-4-feature-logic)
4. [Layer 3: Page Aggregation](#layer-3-page-aggregation)
5. [Layer 2: UI Orchestration](#layer-2-ui-orchestration)
6. [Layer 1: UI Presentation](#layer-1-ui-presentation)
7. [変数名の命名規則](#変数名の命名規則)
8. [実装チェックリスト](#実装チェックリスト)
9. [変更履歴](#変更履歴)

---

## 概要

### 基本原則

1. **一貫性**: 同じ責務を持つフックは同じ接尾辞を使用
2. **明確性**: 名前から責務が理解できる
3. **予測可能性**: 命名パターンから動作が予測できる
4. **スケーラビリティ**: 新しいフックを追加しやすい

### レイヤー別の命名規則サマリー

| Layer | フック/型 | 変数名 | 例 |
|-------|----------|--------|-----|
| Layer 5 | `{Module}Service` / `use{Module}Service()` | `{module}Service` | `useMealService()` → `mealService` |
| Layer 4 | `use{Feature}{Category}()` | `{feature}{Category}` | `useMealManager()` → `mealManager` |
| Layer 3 | `use{Feature}PageModel()` | `{feature}PageModel` | `useTodayPageModel()` → `todayPageModel` |
| Layer 2 | `use{Feature}State()` | `{feature}State` | `useNutritionAnalysisState()` → `nutritionAnalysisState` |
| Layer 1 | `{Feature}Section` / `{Feature}Card` | N/A (props) | コンポーネント名のみ |

**変数命名の原則**: フック名から `use` を除き、先頭を小文字にする（camelCase化）

---

## Layer 5: Domain Services

### 命名パターン

**クラス名**: `{Module}Service`
**フック名**: `use{Module}Service()`

### 規則

- モジュール名 + "Service"
- 単数形を使用
- PascalCase (クラス名)
- camelCase (フック名、先頭は `use`)

### 例

```typescript
// ✅ Good
export class MealService { }
export function useMealService(): MealService { }

export class NutritionService { }
export function useNutritionService(): NutritionService { }

export class TargetService { }
export function useTargetService(): TargetService { }

// ❌ Bad
export class MealsService { }  // 複数形は不要
export class MealServiceImpl { }  // Impl 接尾辞は不要
export function getMealService() { }  // use プレフィックス必須
```

### ファイル構造

```
modules/{module}/services/
  └── {module}Service.ts
```

---

## Layer 4: Feature Logic

### 命名パターン

**フック名**: `use{Feature}{Category}()`
**型名**: `{Feature}{Category}Model`
**Props型**: `Use{Feature}{Category}Props`

### カテゴリ別の接尾辞

#### 1. `Manager` - CRUD 操作管理

**用途**: Create, Read, Update, Delete の操作を含むフック

**責務**:
- データのCRUD操作
- React Query の mutation/query を統合
- 楽観的更新
- キャッシュ無効化

**例**:
```typescript
// ✅ Good
export interface MealManagerModel {
  // Data
  mealItems: readonly MealItem[];

  // CRUD Operations
  createMeal: (data: MealItemRequest) => Promise<MealItem>;
  updateMeal: (id: string, data: MealItemRequest) => Promise<MealItem>;
  deleteMeal: (id: string) => Promise<void>;

  // State
  isLoading: boolean;
  isError: boolean;
}

export function useMealManager({ date }: UseMealManagerProps): MealManagerModel {
  // React Query mutations + queries
}

// その他の例
useMealManager()           // 食事のCRUD
useProfileManager()        // プロフィールのCRUD
useTargetManager()         // 目標のCRUD
useDailyReportManager()    // レポートのCRUD
```

**使い分け**:
- ✅ `Manager` を使う: mutation (create/update/delete) がある
- ❌ `Manager` を使わない: 読み取り専用、計算のみ

---

#### 2. `Calculator` - 計算・導出

**用途**: データから新しい値を計算・導出するフック

**責務**:
- 純粋な計算ロジック
- 複数のデータソースからの導出
- 状態の判定
- プログレス計算

**例**:
```typescript
// ✅ Good
export interface TodayNutritionCalculatorModel {
  nutrientProgress: NutrientProgress[];
  dailySummaryData: DailySummaryData | null;
  isLoading: boolean;
}

export function useTodayNutritionCalculator({
  date
}: UseTodayNutritionCalculatorProps): TodayNutritionCalculatorModel {
  // 栄養進捗の計算
  // 複数のデータソースから導出
}

// その他の例
useTodayNutritionCalculator()    // 栄養進捗の計算
useMealCompletionCalculator()    // 食事完了状態の計算
```

**使い分け**:
- ✅ `Calculator` を使う: データから新しい値を計算
- ❌ `Calculator` を使わない: 単純なデータ取得、CRUD操作

---

#### 3. `State` - 状態管理

**用途**: UIの状態やキャッシュを管理するフック

**責務**:
- React Query キャッシュの管理
- ローカル状態の管理
- 状態の取得・更新
- 自動ロード

**例**:
```typescript
// ✅ Good
export interface MealSectionStateManager {
  fetchNutrition: (mealType: MealType, mealIndex?: number) => Promise<any>;
  getFromCache: (mealType: MealType, mealIndex?: number) => any;
  hasCache: (mealType: MealType, mealIndex?: number) => boolean;
}

export function useMealSectionState(
  date: string,
  options?: UseMealSectionStateOptions
): MealSectionStateManager {
  // キャッシュ管理
  // 自動ロード
}

// その他の例
useMealSectionState()           // 食事セクションの状態管理
useNutritionAnalysisState()     // 栄養分析の状態管理
```

**使い分け**:
- ✅ `State` を使う: キャッシュ管理、状態の保持
- ❌ `State` を使わない: CRUD操作、計算のみ

---

#### 4. `Query` - データ取得のみ

**用途**: 読み取り専用のデータ取得フック

**責務**:
- useQuery によるデータ取得
- mutation なし
- 読み取り専用操作

**例**:
```typescript
// ✅ Good
export interface MealRecommendationQueryModel {
  recommendation: MealRecommendation | null;
  isLoading: boolean;
  isError: boolean;
  refetch: () => void;
}

export function useMealRecommendationQuery({
  date
}: UseMealRecommendationQueryProps): MealRecommendationQueryModel {
  const query = useQuery({ ... });
  return { ... };
}
```

**使い分け**:
- ✅ `Query` を使う: 読み取り専用、mutation なし
- ❌ `Query` を使わない: mutation がある場合は `Manager`

---

### Layer 4 命名の決定フローチャート

```
フックの責務は？
  │
  ├─ CRUD操作がある？
  │   └─ Yes → Manager
  │
  ├─ データから新しい値を計算する？
  │   └─ Yes → Calculator
  │
  ├─ キャッシュや状態を管理する？
  │   └─ Yes → State
  │
  └─ 読み取り専用のデータ取得のみ？
      └─ Yes → Query
```

### ファイル構造

```
modules/{module}/hooks/
  ├── use{Feature}Manager.ts        # CRUD操作
  ├── use{Feature}Calculator.ts     # 計算・導出
  ├── use{Feature}State.ts          # 状態管理
  └── use{Feature}Query.ts          # データ取得のみ
```

### 重要なルール

1. **1ファイル = 1フック**: 複数のフックを1ファイルに含めない
2. **接尾辞は必須**: 責務を明確にするため、必ず接尾辞を使用
3. **型名の一貫性**: `{Feature}{Category}Model` パターンを守る

---

## Layer 3: Page Aggregation

### 命名パターン

**ページレベル**: `use{Feature}PageModel()`
**フィーチャーレベル**: `use{Feature}Model()`

### 使い分け

| パターン | 用途 | 例 |
|---------|------|-----|
| `use{Feature}PageModel()` | 特定のページ専用の集約 | `useTodayPageModel()` |
| `use{Feature}Model()` | 複数ページで使える集約 | `useCalendarModel()` |

### 規則

- ページ専用の場合は "Page" を含める
- 汎用的な場合は "Page" を省略
- 複数の Layer 4 フックを統合
- ページレベルの協調ロジックを含む

### 例

```typescript
// ✅ Good - ページ専用
export function useTodayPageModel(props: UseTodayPageModelProps) {
  const nutrition = useTodayNutritionCalculator({ date });
  const meals = useMealManager({ date });
  const profile = useProfileManager();
  // ...
  return { nutrition, meals, profile, ... };
}

// ✅ Good - 汎用フィーチャー
export function useCalendarModel(props: UseCalendarModelProps) {
  // 複数のページで使用可能
}

// ❌ Bad
export function useTodayModel() { }  // ページ専用なのに Page がない
export function useCalendarPageModel() { }  // 汎用なのに Page がある
```

### ファイル構造

```
modules/{module}/model/
  ├── use{Feature}PageModel.ts      # ページ専用
  └── use{Feature}Model.ts          # 汎用
```

---

## Layer 2: UI Orchestration

### 命名パターン

**フック名**: `use{Feature}State()`
**モーダル**: `use{Feature}ModalState()`

### 規則

- UI の状態管理に特化
- "State" 接尾辞を使用
- モーダルの場合は "ModalState"

### 例

```typescript
// ✅ Good
export function useNutritionAnalysisState({ date }) {
  const [selectedMeal, setSelectedMeal] = useState(null);
  // ...
}

export function useAddMealModalState() {
  const [isOpen, setIsOpen] = useState(false);
  // ...
}

// ❌ Bad
export function useNutritionAnalysis() { }  // State 接尾辞がない
export function useModalState() { }  // 何のモーダルか不明
```

### ファイル構造

```
modules/{module}/ui/hooks/
  ├── use{Feature}State.ts
  └── use{Feature}ModalState.ts
```

---

## Layer 1: UI Presentation

### 命名パターン

**セクション**: `{Feature}Section`
**カード**: `{Feature}Card`
**一般コンポーネント**: `{Feature}Component`

### 規則

- 責務に応じた接尾辞を使用
- PascalCase
- 純粋な表現コンポーネント

### 例

```typescript
// ✅ Good
export const MealListSection = React.memo(function MealListSection(props) {
  // 純粋な表現
});

export const DailySummaryCard = React.memo(function DailySummaryCard(props) {
  // 純粋な表現
});

// ❌ Bad
export const MealList = () => { };  // 接尾辞がない
export const Section = () => { };  // 何のセクションか不明
```

### ファイル構造

```
modules/{module}/ui/
  ├── sections/
  │   └── {Feature}Section.tsx
  ├── cards/
  │   └── {Feature}Card.tsx
  └── components/
      └── {Feature}Component.tsx
```

---

## 変数名の命名規則

### 基本原則

**変数名は型名・フック名と一致させる**

```typescript
// ✅ Good - 完全な一貫性
const nutritionCalculator: TodayNutritionCalculatorModel = useTodayNutritionCalculator({ date });
const mealManager: MealManagerModel = useMealManager({ date });
const mealSectionState: MealSectionStateManager = useMealSectionState(date);

// ❌ Bad - 変数名が型名・フック名と不一致
const nutrition: TodayNutritionCalculatorModel = useTodayNutritionCalculator({ date });
const meals: MealManagerModel = useMealManager({ date });
const mealSectionNutrition: MealSectionStateManager = useMealSectionState(date);
```

### なぜ重要か

1. **予測可能性**: 変数名を見るだけで、型とフックが予測できる
2. **一貫性**: プロジェクト全体で統一されたパターン
3. **可読性**: コードレビューや保守が容易
4. **IDE支援**: 自動補完が効果的に機能

### Layer 3/4 における変数命名

#### Layer 4: Feature Logic の変数

フック名から `use` を除き、先頭を小文字にする：

| フック名 | 型名 | 変数名 |
|---------|------|--------|
| `useMealManager()` | `MealManagerModel` | `mealManager` |
| `useTodayNutritionCalculator()` | `TodayNutritionCalculatorModel` | `nutritionCalculator` |
| `useMealCompletionCalculator()` | `MealCompletionCalculatorModel` | `mealCompletionCalculator` |
| `useMealSectionState()` | `MealSectionStateManager` | `mealSectionState` |

#### Layer 3: Page Aggregation の変数

Layer 3 で Layer 4 のフックを使用する場合：

```typescript
export function useTodayPageModel(props: UseTodayPageModelProps) {
  const { date } = props;

  // ✅ Good - 変数名が型名・フック名と一致
  const nutritionCalculator: TodayNutritionCalculatorModel = useTodayNutritionCalculator({ date });
  const mealManager: MealManagerModel = useMealManager({ date });
  const profileManager: ProfileManagerModel = useProfileManager();
  const targetManager: TargetManagerModel = useTargetManager();
  const dailyReportManager: DailyReportManagerModel = useDailyReportManager({ date });
  const mealCompletionCalculator: MealCompletionCalculatorModel = useMealCompletionCalculator({
    meals: mealManager.mealItems,
    profile: profileManager.profile,
  });
  const mealSectionState: MealSectionStateManager = useMealSectionState(date);
  const nutritionAnalysisState: NutritionAnalysisStateModel = useNutritionAnalysisState({ date });

  return {
    nutritionCalculator,
    mealManager,
    profileManager,
    targetManager,
    dailyReportManager,
    mealCompletionCalculator,
    mealSectionState,
    nutritionAnalysisState,
  };
}
```

### 集約状態の命名

複数のデータソースから導出される状態は、**用途を明示**する：

#### パターン1: ページレベルの集約状態

```typescript
// ✅ Good - ページ全体の状態であることが明確
const isPageLoading = nutritionCalculator.isLoading || mealManager.isLoading;
const isPageError = nutritionCalculator.isError || mealManager.isError;

// ❌ Bad - 何の状態か不明確
const isLoading = nutritionCalculator.isLoading || mealManager.isLoading;
const isError = nutritionCalculator.isError || mealManager.isError;
```

**理由**:
- 個別のローディング状態（`mealManager.isLoading`）と区別可能
- ページ全体の初期表示状態であることが明確
- 特定機能のエラー状態と混同しない

#### パターン2: 導出データ

```typescript
// ✅ Good - 何から導出されたか明確
const mealItems = mealManager.mealItems;
const profile = profileManager.profile;
const mealsPerDay = profileManager.profile?.meals_per_day ?? 3;

// ❌ Bad - 元のデータソースが不明
const items = mealManager.mealItems;
const user = profileManager.profile;
const count = profileManager.profile?.meals_per_day ?? 3;
```

### 命名の決定フローチャート

```
変数はどのレイヤーで定義される？
  │
  ├─ Layer 4: Feature Logic
  │   └─ フック名から `use` を除き、camelCase化
  │      例: useMealManager() → mealManager
  │
  ├─ Layer 3: Page Aggregation
  │   ├─ Layer 4 フックを使う場合
  │   │   └─ フック名から `use` を除き、camelCase化
  │   │      例: useMealManager() → mealManager
  │   │
  │   └─ 集約状態を作る場合
  │       └─ 用途を明示する接頭辞を追加
  │          例: isPageLoading, isPageError
  │
  └─ Layer 2/1: UI
      └─ propsで受け取る場合は変更不要
```

### 実例: Before/After

#### Before (不一致)

```typescript
// useTodayPageModel.ts
const nutrition = useTodayNutritionCalculator({ date });
const meals = useMealManager({ date });
const profile = useProfileManager();
const mealSectionNutrition = useMealSectionState(date);
const isLoading = nutrition.isLoading || meals.isLoading;

return { nutrition, meals, profile, mealSectionNutrition, isLoading };

// TodayPageContent.tsx
const { nutrition, meals, profile, mealSectionNutrition, isLoading } = useTodayPageModel({ date });

// ❌ 問題点:
// - 変数名が型名・フック名と不一致
// - mealSectionNutrition は「Nutrition」だが実際は「State」管理
// - isLoading が何のローディングか不明確
```

#### After (一致)

```typescript
// useTodayPageModel.ts
const nutritionCalculator = useTodayNutritionCalculator({ date });
const mealManager = useMealManager({ date });
const profileManager = useProfileManager();
const mealSectionState = useMealSectionState(date);
const isPageLoading = nutritionCalculator.isLoading || mealManager.isLoading;

return { nutritionCalculator, mealManager, profileManager, mealSectionState, isPageLoading };

// TodayPageContent.tsx
const { nutritionCalculator, mealManager, profileManager, mealSectionState, isPageLoading } = useTodayPageModel({ date });

// ✅ 改善点:
// - 変数名が型名・フック名と完全一致
// - mealSectionState は「State」管理であることが明確
// - isPageLoading がページ全体の状態と明確
```

### アンチパターン

#### ❌ 1. ドメイン名のみ（カテゴリなし）

```typescript
// Bad
const nutrition = useTodayNutritionCalculator({ date });
const meals = useMealManager({ date });

// 問題: 責務（Calculator/Manager）が変数名から分からない
```

#### ❌ 2. 省略形

```typescript
// Bad
const nutriCalc = useTodayNutritionCalculator({ date });
const mealMgr = useMealManager({ date });

// 問題: 可読性が低下、型名・フック名と不一致
```

#### ❌ 3. 変数名と責務の不一致

```typescript
// Bad
const mealSectionNutrition: MealSectionStateManager = useMealSectionState(date);

// 問題: 変数名は「Nutrition（栄養）」だが、実際は「State（状態管理）」
```

#### ❌ 4. 集約状態の不明確な命名

```typescript
// Bad
const isLoading = nutritionCalculator.isLoading || mealManager.isLoading;
const loading = someManager.isLoading;
const isLoad = anotherManager.isLoading;

// 問題: 何のローディング状態か不明確、命名パターンが不統一
```

### ベストプラクティス

#### ✅ 1. フック名と変数名を一致させる

```typescript
const mealManager = useMealManager({ date });
const nutritionCalculator = useTodayNutritionCalculator({ date });
const mealSectionState = useMealSectionState(date);
```

#### ✅ 2. 集約状態は用途を明示

```typescript
const isPageLoading = nutritionCalculator.isLoading || mealManager.isLoading;
const isPageError = nutritionCalculator.isError || mealManager.isError;
```

#### ✅ 3. 導出データは元を明示

```typescript
const mealItems = mealManager.mealItems;
const profile = profileManager.profile;
const activeTarget = nutritionCalculator.activeTarget;
```

#### ✅ 4. 型アノテーションで明確化

```typescript
const nutritionCalculator: TodayNutritionCalculatorModel = useTodayNutritionCalculator({ date });
const mealManager: MealManagerModel = useMealManager({ date });
```

---

## 実装チェックリスト

### 新しいフックを作成する際

- [ ] レイヤーを正しく識別した
- [ ] 責務に応じた接尾辞を選択した
- [ ] 型名が `{Feature}{Category}Model` パターンに従っている
- [ ] Props型が `Use{Feature}{Category}Props` パターンに従っている
- [ ] ファイル名がフック名と一致している
- [ ] 1ファイル = 1フック の原則を守っている
- [ ] エクスポートを `index.ts` に追加した
- [ ] 変数名がフック名・型名と一致している（`use` 除去 + camelCase化）

### 既存のフックをリファクタリングする際

- [ ] 現在の責務を分析した
- [ ] 適切なカテゴリに分類した
- [ ] すべての使用箇所を特定した
- [ ] import を更新した
- [ ] export を更新した
- [ ] 変数名を型名・フック名と一致させた
- [ ] 集約状態に用途を明示する命名をした（例: `isPageLoading`）
- [ ] ビルドが成功することを確認した

---

## 変更履歴

### 2026-02-07: 初版作成

**背景**:
TodayPage 関連のフックに命名の不一致が見つかり、アーキテクチャ違反（Layer 4 の横方向依存）が発生していた。

**実施した変更**:

#### ステップ1: TodayPage 専用フック (today module)

| Before | After | 理由 |
|--------|-------|------|
| `useTodayNutritionProgress` | `useTodayNutritionCalculator` | 計算/導出に特化 |
| `useDailyReportManagement` | `useDailyReportManager` | CRUD操作の統一 |
| `useMealSectionNutrition` | `useMealSectionState` | 状態管理に特化 |

#### ステップ2: 共有フック (複数 modules)

| Before | After | Module | 理由 |
|--------|-------|--------|------|
| `useMealManagement` | `useMealManager` | meal | CRUD操作の統一 |
| `useProfileManagement` | `useProfileManager` | profile | CRUD操作の統一 |
| `useTargetManagement` | `useTargetManager` | target | CRUD操作の統一 |
| `useMealCompletionStatus` | `useMealCompletionCalculator` | meal | 計算/導出に特化 |

**影響範囲**:
- 変更ファイル数: 11ファイル
- 変更モジュール: 4モジュール (today, meal, profile, target)
- 使用箇所: `useTodayPageModel.ts` のみ（影響は限定的）

**成果**:
- TodayPage 関連の命名統一率: 100%
- Layer 4 のアーキテクチャ違反: 0件
- 可読性と保守性の大幅な向上

### 2026-02-07: 変数名の命名規則追加

**背景**:
フック名・型名の命名規則は統一されたが、変数名がそれらと一致していないケースがあり、コードの予測可能性が低下していた。

**実施した変更**:

#### 段階1: 明確な不整合の修正

| Before | After | 理由 |
|--------|-------|------|
| `mealSectionNutrition` | `mealSectionState` | 型は`MealSectionStateManager`なのに変数名が「Nutrition」 |
| `nutritionAnalysis` | `nutritionAnalysisState` | 型は`NutritionAnalysisStateModel`なのに変数名が「Analysis」 |

#### 段階2: 全変数の型名・フック名との統一

| Before | After | カテゴリ | 一致する型/フック |
|--------|-------|---------|------------------|
| `nutrition` | `nutritionCalculator` | Calculator | `TodayNutritionCalculatorModel` / `useTodayNutritionCalculator()` |
| `meals` | `mealManager` | Manager | `MealManagerModel` / `useMealManager()` |
| `profile` | `profileManager` | Manager | `ProfileManagerModel` / `useProfileManager()` |
| `targets` | `targetManager` | Manager | `TargetManagerModel` / `useTargetManager()` |
| `dailyReport` | `dailyReportManager` | Manager | `DailyReportManagerModel` / `useDailyReportManager()` |
| `mealCompletion` | `mealCompletionCalculator` | Calculator | `MealCompletionCalculatorModel` / `useMealCompletionCalculator()` |

#### 段階3: 集約状態の用途明示化

| Before | After | 理由 |
|--------|-------|------|
| `isLoading` | `isPageLoading` | ページ全体の初期表示状態であることを明示 |
| `isError` | `isPageError` | ページ全体のエラー状態であることを明示 |

**影響範囲**:
- 変更ファイル数: 2ファイル (`useTodayPageModel.ts`, `TodayPageContent.tsx`)
- 変更箇所: 56箇所
- 破壊的変更: なし（内部実装のみ）

**成果**:
- 変数名・型名・フック名の完全一貫性: 100% (10/10 変数)
- コードの予測可能性向上: 変数名からフック・型が予測可能に
- 集約状態の明確化: 用途が一目で理解可能
- 新規開発者のオンボーディング効率向上

**確立された原則**:
1. **変数名 = フック名（`use`除去 + camelCase化）**: `useMealManager()` → `mealManager`
2. **集約状態は用途を明示**: `isPageLoading`, `isPageError`
3. **型アノテーションで明確化**: `const mealManager: MealManagerModel = ...`

---

## 参考資料

- [5層アーキテクチャガイド](./5-layer-architecture-guide.v2.md)
- [レイヤー責務とデータ取得](./layer-responsibility-and-data-fetch.md)
- [Today モジュール構造](./today-module-structure.md)

---

## まとめ

この命名規則は、以下を目的としています:

1. **一貫性**: チーム全体で同じパターンを共有
2. **明確性**: コードを読むだけで責務が理解できる
3. **保守性**: 新しいコードを追加しやすい
4. **スケーラビリティ**: プロジェクトの成長に対応

命名規則に従うことで、コードの品質が向上し、チーム開発が円滑になります。

疑問点や提案がある場合は、このドキュメントを更新してください。
