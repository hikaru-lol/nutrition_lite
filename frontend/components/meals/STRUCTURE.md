# MealsPage コンポーネント構造分析

## 概要

`MealsPage.tsx` は、1 日の食事記録を管理するメインコンポーネントです。メインの食事（朝食、昼食、夕食など）と間食を分けて表示し、各食事の栄養情報を計算・表示する機能を提供します。

## コンポーネント階層構造

```
app/(app)/meals/page.tsx
└── MealsPage (components/meals/MealsPage.tsx)
    ├── PageHeader (components/layout/PageHeader.tsx)
    ├── MealNutritionChart (components/meals/MealNutritionChart.tsx) [1日の栄養サマリ用]
    ├── MainMealsSection (components/meals/MainMealsSection.tsx)
    │   └── MealSlotCard (components/meals/MealSlotCard.tsx) [複数回繰り返し]
    │       ├── MealNutritionChart (components/meals/MealNutritionChart.tsx) [各食事の栄養用]
    │       └── MealItemList (components/meals/MealItemList.tsx)
    │           └── MealItemRow (components/meals/MealItemRow.tsx) [複数回繰り返し]
    ├── SnackMealsSection (components/meals/SnackMealsSection.tsx)
    │   └── MealItemList (components/meals/MealItemList.tsx)
    │       └── MealItemRow (components/meals/MealItemRow.tsx) [複数回繰り返し]
    └── MealItemDialog (components/meals/MealItemDialog.tsx) [モーダル]
```

## 各コンポーネントの役割

### 1. MealsPage (メインコンポーネント)

**ファイル**: `components/meals/MealsPage.tsx`

**主な責務**:

- URL パラメータから日付を取得
- `useMealsByDate` フックで食事データを取得
- ダイアログの開閉状態管理
- 食事アイテムの作成・編集・削除処理
- 栄養情報の再計算処理
- 1 日の栄養サマリ表示

**主要な状態管理**:

- `dialogOpen`, `dialogMode`, `dialogMealType`, `dialogMealIndex`: ダイアログの状態
- `editingItemId`, `initialFormValues`: 編集時の初期値
- `mealNutritions`: 各食事の栄養情報（キー: `mealType-mealIndex-date`）
- `dailyNutrition`: 1 日の総合栄養サマリ

**主要な関数**:

- `openCreateDialog()`: 新規作成ダイアログを開く
- `openEditDialog()`: 編集ダイアログを開く
- `handleSubmitDialog()`: 食事アイテムの保存処理
- `handleDeleteItem()`: 食事アイテムの削除処理
- `handleRecomputeMealNutrition()`: 栄養情報の再計算

### 2. MainMealsSection

**ファイル**: `components/meals/MainMealsSection.tsx`

**主な責務**:

- メインの食事スロット（1 回目、2 回目...）を表示
- `mealsPerDay` に基づいて必要な数の `MealSlotCard` を生成
- 各スロットへのコールバック関数を渡す

**Props**:

- `mealsPerDay`: 1 日の食事回数
- `slots`: 各食事スロットのデータ
- `onAddItem`, `onEditItem`, `onDeleteItem`: イベントハンドラ
- `onRecomputeNutrition`: 栄養計算のトリガー
- `getNutrition`: 栄養情報の取得関数
- `nutritionLoadingKey`: ローディング状態のキー
- `date`: 対象日付

### 3. SnackMealsSection

**ファイル**: `components/meals/SnackMealsSection.tsx`

**主な責務**:

- 間食の一覧を表示
- 間食の追加・編集・削除機能
- 間食全体の栄養情報表示

**Props**:

- `items`: 間食アイテムの配列
- `onAddItem`, `onEditItem`, `onDeleteItem`: イベントハンドラ
- `onRecomputeNutrition`: 栄養計算のトリガー
- `nutrition`: 間食の栄養情報
- `nutritionLoadingKey`: ローディング状態のキー

### 4. MealSlotCard

**ファイル**: `components/meals/MealSlotCard.tsx`

**主な責務**:

- 1 つの食事スロット（例: 「1 回目の食事」）を表示
- その食事に含まれる食品一覧を表示
- 栄養情報の計算・表示
- 食品追加ボタン

**Props**:

- `mealIndex`: 食事のインデックス（1, 2, 3...）
- `items`: その食事に含まれる食品リスト
- `onAddClick`, `onEditClick`, `onDeleteClick`: イベントハンドラ
- `nutrition`: その食事の栄養情報
- `onRecomputeNutrition`: 栄養計算のトリガー
- `isNutritionLoading`: ローディング状態

### 5. MealItemList

**ファイル**: `components/meals/MealItemList.tsx`

**主な責務**:

- 食事アイテムのリストを表示
- 各アイテムを `MealItemRow` としてレンダリング

**Props**:

- `items`: 表示する食事アイテムの配列
- `onEditClick`, `onDeleteClick`: イベントハンドラ

### 6. MealItemRow

**ファイル**: `components/meals/MealItemRow.tsx`

**主な責務**:

- 1 つの食事アイテムを表示
- 食品名、量、メモを表示
- 編集・削除ボタン

**Props**:

- `item`: 食事アイテムのデータ（`MealItemVM`）
- `onEdit`, `onDelete`: イベントハンドラ

### 7. MealItemDialog

**ファイル**: `components/meals/MealItemDialog.tsx`

**主な責務**:

- 食事アイテムの作成・編集用モーダルダイアログ
- フォーム入力の管理
- バリデーション

**Props**:

- `open`: ダイアログの表示状態
- `mode`: 'create' | 'edit'
- `mealType`: 'main' | 'snack'
- `mealIndex`: 食事のインデックス（main の場合）
- `initialValues`: 編集時の初期値
- `onOpenChange`: ダイアログの開閉ハンドラ
- `onSubmit`: フォーム送信ハンドラ
- `isSubmitting`: 送信中の状態
- `errorMessage`: エラーメッセージ

**フォーム項目**:

- `name`: 食品名（必須）
- `amountValue`: 量の数値
- `amountUnit`: 単位（g, ml, 個など）
- `servingCount`: 何人前/何皿分
- `note`: メモ

### 8. MealNutritionChart

**ファイル**: `components/meals/MealNutritionChart.tsx`

**主な責務**:

- 栄養情報を棒グラフで可視化
- Recharts ライブラリを使用
- 各栄養素の量を表示

**Props**:

- `nutrients`: 栄養素の配列
- `height`: グラフの高さ（デフォルト: 220）
- `title`: グラフのタイトル（オプション）

## データフロー

### データ取得フロー

```
MealsPage
  └── useMealsByDate(date)
      ├── fetchProfile() → プロフィール取得（meals_per_day）
      └── fetchMealItems(date) → 食事アイテム取得
          └── transformMeals() → MealsView に変換
              ├── mainSlots: MealSlot[]
              └── snacks: MealItemVM[]
```

### 食事アイテム作成フロー

```
ユーザーが「食品を追加」をクリック
  → openCreateDialog()
  → MealItemDialog が開く
  → フォーム入力
  → handleSubmitDialog()
  → createMealItem() API呼び出し
  → refresh() でデータ再取得
```

### 食事アイテム編集フロー

```
ユーザーが「編集」をクリック
  → openEditDialog(entryId)
  → 該当アイテムを検索
  → initialFormValues を設定
  → MealItemDialog が開く
  → フォーム編集
  → handleSubmitDialog()
  → updateMealItem() API呼び出し
  → refresh() でデータ再取得
```

### 栄養情報計算フロー

```
ユーザーが「栄養を計算」をクリック
  → handleRecomputeMealNutrition()
  → recomputeMealAndDailyNutrition() API呼び出し
  → mealNutritions に保存（キー: mealType-mealIndex-date）
  → dailyNutrition を更新
  → MealNutritionChart で表示
```

## API 層

### lib/api/meals.ts

**関数**:

- `fetchMealItems(date)`: 指定日の食事アイテムを取得
- `createMealItem(input)`: 食事アイテムを作成
- `updateMealItem(id, input)`: 食事アイテムを更新
- `deleteMealItem(id)`: 食事アイテムを削除

**型**:

- `MealItemResponse`: API レスポンスの型
- `MealType`: 'main' | 'snack'

### lib/api/nutrition.ts

**関数**:

- `recomputeMealAndDailyNutrition(params)`: 栄養情報を再計算

**型**:

- `MealNutritionSummaryApi`: 1 ミール分の栄養サマリ
- `DailyNutritionSummaryApi`: 1 日分の栄養サマリ
- `NutritionNutrientIntakeApi`: 1 栄養素分の情報

### lib/hooks/useMealsByDate.ts

**カスタムフック**:

- `useMealsByDate(date)`: 指定日の食事データを取得・管理

**戻り値**:

- `data`: `MealsView` 型のデータ
- `isLoading`: ローディング状態
- `error`: エラー状態
- `refresh`: データ再取得関数

**内部処理**:

- プロフィールと食事アイテムを並列取得
- `transformMeals()` で ViewModel に変換
- `mainSlots` と `snacks` に分類

## 型定義

### MealItemVM

```typescript
{
  id: string;
  mealType: 'main' | 'snack';
  mealIndex: number | null;
  name: string;
  amountText?: string;
  note?: string | null;
}
```

### MealSlot

```typescript
{
  mealIndex: number;
  items: MealItemVM[];
}
```

### MealsView

```typescript
{
  date: string;
  mealsPerDay: number;
  mainSlots: MealSlot[];
  snacks: MealItemVM[];
}
```

## UI コンポーネント依存関係

### 共通 UI コンポーネント

- `Card` (`@/components/ui/card`)
- `Button` (`@/components/ui/button`)
- `Input` (`@/components/ui/input`)
- `Label` (`@/components/ui/label`)

### レイアウトコンポーネント

- `PageHeader` (`@/components/layout/PageHeader`)

### 外部ライブラリ

- `recharts`: グラフ表示用（`MealNutritionChart`）

## 状態管理のポイント

1. **ダイアログ状態**: `MealsPage` で一元管理
2. **栄養情報**: キーベースで管理（`mealType-mealIndex-date`）
3. **データ取得**: `useMealsByDate` フックで管理
4. **ローディング状態**: 各操作ごとに個別管理

## 改善の余地

1. **型の一貫性**: `MealSlotCard` の `isLoading` prop が未使用
2. **エラーハンドリング**: より詳細なエラーメッセージ表示
3. **パフォーマンス**: 栄養情報のメモ化検討
4. **アクセシビリティ**: キーボード操作の改善
5. **テスト**: 各コンポーネントの単体テスト追加
