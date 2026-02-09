# Today モジュール構造ガイド

## 概要

Today モジュールは、ユーザーの「今日」のデータを統合表示するメインダッシュボード機能を提供します。

**主な責務:**
- 特定日付の食事データ表示
- 栄養進捗の可視化
- 各種モーダル（食事追加・編集・分析等）の管理
- ページ全体のデータ統合とオーケストレーション

**5層アーキテクチャとの対応:**
- Layer 1: `ui/TodayPageContent.tsx`, `ui/components/` - プレゼンテーション
- Layer 2: `ui/TodayPage.tsx`, `ui/hooks/` - UIオーケストレーション
- Layer 3: `model/useTodayPageModel.ts` - ページ集約
- Layer 4: `hooks/` - フィーチャーロジック
- Layer 5: 他モジュールのサービスに依存（meal, nutrition, target等）

---

## ディレクトリ構造

```
src/modules/today/
├── contract/                    # 型定義・スキーマ・ドメイン契約
│   └── todayContract.ts
├── hooks/                       # Layer 4: フィーチャーロジック
│   └── useTodayNutritionProgress.ts
├── model/                       # Layer 3: ページ集約
│   └── useTodayPageModel.ts
├── ui/                          # Layer 2 & 1: UIコンポーネント
│   ├── components/
│   │   └── modals/              # モーダルコンポーネント群
│   │       ├── AddMealModal.tsx
│   │       ├── EditMealModal.tsx
│   │       ├── MealRecommendationModal.tsx
│   │       └── NutritionAnalysisModal.tsx
│   ├── hooks/                   # Layer 2: UIオーケストレーション用フック
│   │   ├── useAddMealModalState.ts
│   │   ├── useEditMealModalState.ts
│   │   ├── useMealRecommendationModalState.ts
│   │   ├── useNutritionAnalysisModalState.ts
│   │   └── useModalStates.ts    # 統合モーダル管理
│   ├── TodayPage.tsx            # Layer 2: ページコンテナ
│   └── TodayPageContent.tsx     # Layer 1: メインコンテンツ
└── index.ts                     # Public exports
```

---

## 各ディレクトリの役割

### `contract/` - 型定義・スキーマ・ドメイン契約

**責務:**
- Zodスキーマによるバリデーション定義
- 型定義のエクスポート
- ドメイン固有の定数・ヘルパー関数
- 他層から参照される契約の一元管理

**ファイル:**
- `todayContract.ts` (68行)

**主な内容:**
```typescript
// Zodスキーマ
export const TodayMealItemFormSchema = z.object({ ... });

// 型定義
export type NutrientProgress = { ... };
export type NutrientCode = 'protein' | 'fat' | 'carbohydrate' | ...;

// 定数
export const nutrientLabels: Record<NutrientCode, string> = { ... };

// ヘルパー関数
export function formatLocalDateYYYYMMDD(date: Date): string { ... }
```

**使用例:**
```typescript
import type { NutrientProgress } from '@/modules/today/contract/todayContract';
import { formatLocalDateYYYYMMDD } from '@/modules/today/contract/todayContract';
```

---

### `hooks/` - Layer 4: フィーチャーロジック

**責務:**
- React Query による状態管理
- 複数サービス・モジュールの協調
- 非同期データフェッチング
- UI向けデータ統合

**ファイル:**
- `useTodayNutritionProgress.ts` (106行)

**主な内容:**
```typescript
export interface TodayNutritionProgressModel {
  activeTarget: any | null;
  nutrientProgress: NutrientProgress[];
  dailySummaryData: DailySummaryData | null;
  isLoading: boolean;
  isError: boolean;
  refetchDailySummary: () => void;
}

export function useTodayNutritionProgress(props: {
  date: string;
}): TodayNutritionProgressModel {
  // 1. サービス取得
  const targetService = useTargetService();
  const nutritionService = useNutritionService();

  // 2. 複数のReact Queryを協調
  const activeTargetQuery = useQuery({ ... });
  const mealItemsQuery = useMealItemsByDate(date);
  const dailySummaryQuery = useQuery({ ... });

  // 3. データ統合
  const nutritionProgressData = nutritionProgressService.calculateProgressData(
    target,
    dailySummary
  );

  return { ... };
}
```

**特徴:**
- React Query による宣言的な状態管理
- 複数モジュールのサービスを利用（target, nutrition, meal, nutrition-progress）
- 依存関係のあるクエリの協調（enabled条件）
- 計算済みデータをModelとして公開

---

### `model/` - Layer 3: ページ集約

**責務:**
- ページレベルでの複数機能統合
- ページ全体の状態管理
- 機能間の協調ロジック
- Layer 4フックの集約

**ファイル:**
- `useTodayPageModel.ts`

**パターン:**
```typescript
export function useTodayPageModel(props: { date: string }) {
  // Layer 4フックを集約
  const meals = useTodayMeals({ date });
  const nutrition = useTodayNutritionProgress({ date });
  const modals = useModalStates();

  // ページレベルの協調ロジック
  const handleMealUpdate = useCallback(async () => {
    await meals.refetch();
    await nutrition.refetchDailySummary();
  }, [meals, nutrition]);

  // 統合されたモデルを返す
  return {
    meals,
    nutrition,
    modals,
    actions: { handleMealUpdate }
  };
}
```

**重要原則:**
- **集約のみ** - React Queryは使わない（Layer 4に委譲）
- **機能の統合** - 複数のLayer 4フックを組み合わせる
- **協調ロジック** - 機能間の相互作用を管理

---

### `ui/` - Layer 2 & 1: UIコンポーネント

#### `ui/TodayPage.tsx` - Layer 2: ページコンテナ

**責務:**
- URLパラメータの解析
- ページ全体のレイアウト
- TodayPageContentへのprops渡し

**パターン:**
```typescript
'use client';

export function TodayPage() {
  const searchParams = useSearchParams();
  const date = useMemo(() => {
    const dateParam = searchParams.get('date');
    return dateParam || formatLocalDateYYYYMMDD(new Date());
  }, [searchParams]);

  return (
    <div>
      <h1>Today</h1>
      <TodayPageContent date={date} />
    </div>
  );
}
```

#### `ui/TodayPageContent.tsx` - Layer 1: メインコンテンツ

**責務:**
- Layer 3モデルの消費
- セクションコンポーネントへのprops配布
- イベントハンドラの接続

**パターン:**
```typescript
'use client';

export function TodayPageContent({ date }: { date: string }) {
  const model = useTodayPageModel({ date });

  return (
    <>
      <MealListSection
        meals={model.meals.data}
        onEdit={model.modals.editMeal.open}
      />
      <NutrientProgressSection
        nutrientProgress={model.nutrition.nutrientProgress}
        isLoading={model.nutrition.isLoading}
      />
      <AddMealModal {...model.modals.addMeal} />
      <EditMealModal {...model.modals.editMeal} />
    </>
  );
}
```

---

### `ui/components/modals/` - モーダルコンポーネント群

**責務:**
- 各種モーダルUIの実装
- フォーム管理（react-hook-form）
- Mutation実行

**ファイル構成:**
| ファイル | 責務 |
|---------|------|
| `AddMealModal.tsx` | 食事追加モーダル |
| `EditMealModal.tsx` | 食事編集モーダル |
| `MealRecommendationModal.tsx` | AI食事推薦モーダル |
| `NutritionAnalysisModal.tsx` | 栄養分析モーダル |

**共通パターン:**
```typescript
interface AddMealModalProps {
  isOpen: boolean;
  close: () => void;
  date: string;
  // その他モーダル固有のprops
}

export function AddMealModal(props: AddMealModalProps) {
  const { isOpen, close, date } = props;

  const form = useForm({ ... });
  const mutation = useMutation({ ... });

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && close()}>
      <form onSubmit={form.handleSubmit(...)}>
        {/* フォーム内容 */}
      </form>
    </Dialog>
  );
}
```

---

### `ui/hooks/` - Layer 2: UIオーケストレーション用フック

**責務:**
- モーダルの開閉状態管理
- 編集対象アイテムの管理
- UI層固有のローカルステート

#### 個別モーダルフック

**ファイル構成:**
| ファイル | 責務 |
|---------|------|
| `useAddMealModalState.ts` | 食事追加モーダル状態 |
| `useEditMealModalState.ts` | 食事編集モーダル状態 |
| `useMealRecommendationModalState.ts` | AI推薦モーダル状態 |
| `useNutritionAnalysisModalState.ts` | 栄養分析モーダル状態 |

**共通パターン:**
```typescript
export interface EditMealModalState {
  isOpen: boolean;
  editingMealItem: MealItemForEdit | null;
}

export interface EditMealModalActions {
  open: (mealItem: MealItem, date: string) => void;
  close: () => void;
}

export interface EditMealModalModel
  extends EditMealModalState, EditMealModalActions {}

export function useEditMealModalState(): EditMealModalModel {
  const [isOpen, setIsOpen] = useState(false);
  const [editingMealItem, setEditingMealItem] = useState(null);

  const open = useCallback((mealItem, date) => {
    setEditingMealItem({ ...mealItem, date });
    setIsOpen(true);
  }, []);

  const close = useCallback(() => {
    setIsOpen(false);
    setEditingMealItem(null);
  }, []);

  return { isOpen, editingMealItem, open, close };
}
```

#### 統合モーダルフック

**ファイル:** `useModalStates.ts`

**責務:**
- 複数のモーダル状態を一元管理
- ページモデルからの利用を簡素化

**実装:**
```typescript
export interface ModalStates {
  addMeal: AddMealModalModel;
  editMeal: EditMealModalModel;
  mealRecommendation: MealRecommendationModalModel;
  nutritionAnalysis: NutritionAnalysisModalModel;
}

export function useModalStates(): ModalStates {
  const addMeal = useAddMealModalState();
  const editMeal = useEditMealModalState();
  const mealRecommendation = useMealRecommendationModalState();
  const nutritionAnalysis = useNutritionAnalysisModalState();

  return {
    addMeal,
    editMeal,
    mealRecommendation,
    nutritionAnalysis
  };
}
```

**使用例（Layer 3）:**
```typescript
export function useTodayPageModel() {
  const modals = useModalStates();

  return {
    modals,  // 全てのモーダル状態を一括で提供
    // ...
  };
}
```

---

### `index.ts` - Public Exports

**責務:**
- モジュールの公開APIを定義
- 外部からアクセス可能なエクスポートの制御
- モジュール境界の明確化

**内容:**
```typescript
// ページコンポーネント
export { TodayPage } from './ui/TodayPage';

// Layer 3モデル
export { useTodayPageModel } from './model/useTodayPageModel';

// 型定義
export type {
  NutrientProgress,
  NutrientCode
} from './contract/todayContract';

// ヘルパー関数（必要に応じて）
export { formatLocalDateYYYYMMDD } from './contract/todayContract';
```

**重要原則:**
- ❌ **他モジュールのサービスを再エクスポートしない** - モジュール境界違反
- ✅ **todayモジュール固有の公開APIのみ**
- ✅ **型定義は積極的にエクスポート** - 他モジュールでの利用を想定

---

## 依存関係図

```
┌─────────────────────────────────────────────────────────────┐
│ app/(app)/today/page.tsx                                    │
│   └─> TodayPage                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: ui/TodayPage.tsx                                   │
│   └─> TodayPageContent                                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: ui/TodayPageContent.tsx                            │
│   ├─> useTodayPageModel() ← Layer 3                        │
│   └─> セクションコンポーネント（shared/ui/sections/）         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: model/useTodayPageModel.ts                         │
│   ├─> useTodayMeals()                 ← Layer 4 (meal)     │
│   ├─> useTodayNutritionProgress()     ← Layer 4 (today)    │
│   └─> useModalStates()                ← Layer 2            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: hooks/useTodayNutritionProgress.ts                 │
│   ├─> useTargetService()              ← Layer 5 (target)   │
│   ├─> useNutritionService()           ← Layer 5 (nutrition)│
│   ├─> useMealService()                ← Layer 5 (meal)     │
│   └─> useNutritionProgressService()   ← Layer 5 (nutrition)│
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 5: 各種ドメインサービス                                │
│   ├─> target/services/targetService.ts                     │
│   ├─> nutrition/services/nutritionService.ts               │
│   ├─> meal/services/mealService.ts                         │
│   └─> nutrition-progress/services/...                      │
└─────────────────────────────────────────────────────────────┘
```

---

## モジュール間の依存関係

### Today モジュールが依存する他モジュール

| モジュール | 使用箇所 | 用途 |
|-----------|---------|------|
| `meal` | Layer 4 hooks | 食事データ取得・操作 |
| `nutrition` | Layer 4 hooks | 栄養計算・サマリー取得 |
| `target` | Layer 4 hooks | 目標設定データ取得 |
| `nutrition-progress` | Layer 4 hooks | 栄養進捗計算サービス |
| `meal-recommendation` | ui/TodayPageContent | AI食事推薦機能 |

### 他モジュールから Today モジュールへの依存

**現状:** ほぼなし（Todayは集約層のため）

**許容される依存例:**
- `calendar` モジュールが `formatLocalDateYYYYMMDD` を使用（ヘルパー関数）
- 他ページが `NutrientProgress` 型を使用（型定義）

---

## 実装パターン・ベストプラクティス

### 1. モーダル状態管理パターン

**個別フック + 統合フック**

```typescript
// ✅ 推奨: 個別フックで実装 + useModalStatesで統合
const modals = useModalStates();
modals.addMeal.open();
modals.editMeal.open(mealItem, date);

// ❌ 非推奨: 個別にインポート
const addMeal = useAddMealModalState();
const editMeal = useEditMealModalState();
```

### 2. Layer 3 モデルの設計原則

**集約のみ、React Queryは使わない**

```typescript
// ✅ 推奨: Layer 4フックの集約のみ
export function useTodayPageModel() {
  const meals = useTodayMeals();      // Layer 4
  const nutrition = useTodayNutrition(); // Layer 4
  return { meals, nutrition };
}

// ❌ 非推奨: Layer 3でReact Queryを直接使用
export function useTodayPageModel() {
  const mealsQuery = useQuery({ ... }); // NG: Layer 4の責務
  return { meals: mealsQuery.data };
}
```

### 3. 型定義の配置

**contract/ に一元化**

```typescript
// ✅ 推奨: contract/todayContract.ts
export type NutrientProgress = { ... };
export const nutrientLabels = { ... };

// ❌ 非推奨: 各ファイルに散在
// hooks/useTodayNutritionProgress.ts
type NutrientProgress = { ... };  // NG: 重複定義
```

### 4. import パスの統一

**contract からインポート**

```typescript
// ✅ 推奨
import type { NutrientProgress } from '@/modules/today/contract/todayContract';

// ❌ 非推奨（古い構造）
import type { NutrientProgress } from '@/modules/today/types/todayTypes';
```

---

## リファクタリング履歴

### Before（リファクタ前）

**問題点:**
- `types/todayTypes.ts` が249行で肥大化
- 使われていない型定義が多数存在
- モジュール境界違反（index.ts で他モジュールのサービスを再エクスポート）
- モーダルコンポーネントが ui/components/ 直下に分散

### After（リファクタ後）

**改善内容:**
- ✅ `contract/todayContract.ts` (68行) に整理 - **68%削減**
- ✅ 使用中の型定義のみを保持
- ✅ index.ts から他モジュールの再エクスポートを削除
- ✅ モーダルコンポーネントを `ui/components/modals/` に集約
- ✅ `useModalStates.ts` で統合モーダル管理を実現

**ファイル削減:**
- `types/todayTypes.ts` (249行) → 削除

**新規作成:**
- `contract/todayContract.ts` (68行)
- `ui/hooks/useModalStates.ts` (48行)

---

## 今後の拡張ガイド

### 新しいモーダルを追加する場合

1. **Layer 2フックを作成**
   ```typescript
   // ui/hooks/useNewModalState.ts
   export function useNewModalState() { ... }
   ```

2. **useModalStatesに統合**
   ```typescript
   // ui/hooks/useModalStates.ts
   export function useModalStates() {
     const newModal = useNewModalState();
     return { ..., newModal };
   }
   ```

3. **モーダルコンポーネント作成**
   ```typescript
   // ui/components/modals/NewModal.tsx
   export function NewModal(props) { ... }
   ```

4. **TodayPageContentで使用**
   ```typescript
   const model = useTodayPageModel();
   <NewModal {...model.modals.newModal} />
   ```

### 新しいフィーチャーフックを追加する場合

1. **Layer 4フックを作成**
   ```typescript
   // hooks/useNewFeature.ts
   export function useNewFeature() {
     const service = useService();
     const query = useQuery({ ... });
     return { data, isLoading };
   }
   ```

2. **Layer 3モデルに統合**
   ```typescript
   // model/useTodayPageModel.ts
   export function useTodayPageModel() {
     const newFeature = useNewFeature();
     return { ..., newFeature };
   }
   ```

3. **UIで消費**
   ```typescript
   const model = useTodayPageModel();
   <Section data={model.newFeature.data} />
   ```

---

## トラブルシューティング

### Q: モーダルが開かない

**確認ポイント:**
1. `useModalStates()` が正しく呼ばれているか
2. `modals.xxx.open()` が実行されているか
3. `isOpen` プロパティが正しく渡されているか

### Q: 型エラー: Cannot find module 'todayTypes'

**対処法:**
```typescript
// 古いimportを変更
- import type { NutrientProgress } from '@/modules/today/types/todayTypes';
+ import type { NutrientProgress } from '@/modules/today/contract/todayContract';
```

### Q: Layer 3とLayer 4の境界が不明確

**判断基準:**
- **Layer 4**: React Queryを使う、非同期処理、サービス呼び出し
- **Layer 3**: Layer 4フックの集約のみ、React Queryは使わない

---

## まとめ

Today モジュールは以下の構造で整理されています:

1. **contract/** - 型定義・スキーマの一元管理
2. **hooks/** - Layer 4フィーチャーロジック（React Query）
3. **model/** - Layer 3ページ集約（集約のみ）
4. **ui/hooks/** - Layer 2モーダル状態管理
5. **ui/components/modals/** - モーダルコンポーネント群
6. **ui/** - Layer 2/1 UIコンポーネント

この構造により、**責務の分離**、**再利用性の向上**、**保守性の向上**を実現しています。

新機能追加時は、このガイドに従って適切な層に実装することで、一貫性のあるコードベースを維持できます。
