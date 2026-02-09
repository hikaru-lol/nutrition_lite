# レイヤーの責務とデータ取得の設計原則

## 概要

このドキュメントは、5層アーキテクチャにおける各レイヤーの責務と、データ取得（useEffect）の配置場所について、実際のリファクタリング事例を通して解説します。

**重要な原則:**
- **データ取得は Layer 4（Feature Logic）の責務**
- **Layer 1（Presentation）と Layer 2（UI Orchestration）は副作用を持たない**
- **Layer 3（Page Aggregation）は集約のみ、データ取得しない**

---

## 目次

1. [問題の発見](#問題の発見)
2. [5層アーキテクチャの原則](#5層アーキテクチャの原則)
3. [各レイヤーの詳細な責務](#各レイヤーの詳細な責務)
4. [実際の問題事例](#実際の問題事例)
5. [修正内容](#修正内容)
6. [Before/After 比較](#beforeafter-比較)
7. [データフロー](#データフロー)
8. [ベストプラクティス](#ベストプラクティス)
9. [よくある間違い](#よくある間違い)
10. [チェックリスト](#チェックリスト)

---

## 問題の発見

### 背景: リロード後に「詳細表示」ボタンが消える問題

**状況:**
1. ユーザーが「栄養分析」を実行
2. 「詳細表示」ボタンが表示される ✅
3. ページをリロード
4. 「詳細表示」ボタンが消える ❌

**原因:**
React Query のキャッシュはメモリ上のみで、リロードで消える。サーバーからデータを取得する仕組みがなかった。

### 最初の修正案（誤り）

```typescript
// ❌ 間違った修正: Layer 1 に useEffect を追加
// MealListSection.tsx (Layer 1: Presentation)

useEffect(() => {
  if (!hasNutritionData && hasItems) {
    nutritionAnalysis.getFromServer(mealType, mealIndex);
  }
}, [mealType, mealIndex, hasItems, hasNutritionData]);
```

**問題点:**
- Layer 1（Presentation）に副作用（useEffect）がある
- 純粋なプレゼンテーションの原則違反
- MealListSection は `shared/ui/sections/` にあり、再利用可能な UI コンポーネントのはず

### 第二の問題提起

**ユーザーからの指摘:**
> "中に useEffect があるということは、これは純粋な UI ということではない？"

**完全に正しい指摘。** Layer 1 は副作用を持つべきではない。

### 第三の問題提起

**ユーザーからの指摘:**
> "TodayPageContent も UI と配線だけだが、ここに useEffect があるのはいいの？"

**これも正しい指摘。** TodayPageContent は Layer 1/2 なので、データ取得の useEffect を持つべきではない。

---

## 5層アーキテクチャの原則

### レイヤー構造

```
┌─────────────────────────────────────────┐
│ Layer 1: UI Presentation                │ ← 純粋な表現
├─────────────────────────────────────────┤
│ Layer 2: UI Orchestration               │ ← UI協調、イベント処理
├─────────────────────────────────────────┤
│ Layer 3: Page Aggregation               │ ← ページ集約
├─────────────────────────────────────────┤
│ Layer 4: Feature Logic                  │ ← データ取得、React Query
├─────────────────────────────────────────┤
│ Layer 5: Domain Services                │ ← API呼び出し、ドメインロジック
└─────────────────────────────────────────┘
```

### データ取得の原則

| Layer | データ取得 | useEffect | React Query |
|-------|-----------|-----------|-------------|
| Layer 1 | ❌ | ❌ | ❌ |
| Layer 2 | ❌ | ❌ | ❌ |
| Layer 3 | ❌ | ❌ | ❌ |
| Layer 4 | ✅ | ✅ | ✅ |
| Layer 5 | ✅ (API呼び出し) | ❌ | ❌ |

**重要:** データ取得の useEffect は **Layer 4 のみ**に配置する。

---

## 各レイヤーの詳細な責務

### Layer 1: UI Presentation

**責務:**
- 純粋な表現
- props による制御のみ
- 副作用なし
- ビジネスロジックなし

**使えるもの:**
```typescript
✅ props
✅ 条件分岐表示（if, ternary）
✅ map, filter などの配列操作（表示用）
✅ React.memo
✅ const 変数（計算結果）
```

**使えないもの:**
```typescript
❌ useEffect（データ取得）
❌ useState（UIステート以外）
❌ useQuery, useMutation
❌ API呼び出し
❌ ビジネスロジック
```

**例外的に使えるもの:**
```typescript
⚠️ useState（ローカルUIステートのみ）
   - 例: ドロップダウンの開閉状態
   - 例: ホバー状態
   - データ取得や外部状態は NG
```

**コード例:**
```typescript
// ✅ 正しい Layer 1
export function MealListSection({
  mealItems,
  isLoading,
  onAddMeal,
  onEditMeal,
  nutritionAnalysis,
}: MealListSectionProps) {
  // ✅ props から計算
  const hasItems = mealItems.length > 0;

  // ✅ props から取得
  const cachedData = nutritionAnalysis.getFromCache(mealType, mealIndex);
  const hasData = Boolean(cachedData);

  // ✅ 条件分岐表示
  if (isLoading) return <LoadingState />;

  return (
    <Card>
      {/* ✅ 表示のみ */}
      {hasItems ? (
        <MealList items={mealItems} onEdit={onEditMeal} />
      ) : (
        <EmptyState />
      )}

      {/* ✅ イベントハンドラは props 経由 */}
      <Button onClick={onAddMeal}>追加</Button>

      {/* ✅ 条件付き表示 */}
      {hasData && (
        <Button onClick={() => nutritionAnalysis.onShowDetails(cachedData)}>
          詳細表示
        </Button>
      )}
    </Card>
  );
}
```

---

### Layer 2: UI Orchestration

**責務:**
- UI コンポーネント間の協調
- イベントハンドリング
- モーダル・フォーム状態管理
- Layer 3 モデルの消費

**使えるもの:**
```typescript
✅ useState（UIステートのみ）
   - モーダルの開閉状態
   - フォームの入力状態
✅ useCallback（イベントハンドラ）
✅ Layer 3 モデルの消費
✅ イベントハンドラの定義
```

**使えないもの:**
```typescript
❌ useEffect（データ取得）
❌ useQuery, useMutation
❌ API呼び出し
❌ ビジネスロジック
```

**コード例:**
```typescript
// ✅ 正しい Layer 2
export function TodayPageContent({ date }: { date: string }) {
  // ✅ Layer 3 モデルを消費
  const model = useTodayPageModel({ date });

  // ✅ イベントハンドラ（UI協調）
  const handleNutritionAnalysis = async (mealType, mealIndex) => {
    // Layer 4 の機能を呼び出すだけ
    await model.mealSectionNutrition.fetchNutrition(mealType, mealIndex);
    model.nutritionAnalysis.selectMealForNutrition(mealType, mealIndex);
  };

  // ✅ Layer 1 に props を配布
  return (
    <div>
      <MealListSection
        mealItems={model.meals.mealItems}
        onAddMeal={model.modals.addMeal.open}
        onAnalyzeNutrition={handleNutritionAnalysis}
        nutritionAnalysis={{
          getFromCache: model.mealSectionNutrition.getFromCache,
          onShowDetails: model.modals.nutritionAnalysis.open,
          // ...
        }}
      />
    </div>
  );
}
```

---

### Layer 3: Page Aggregation

**責務:**
- Layer 4 フックの集約
- ページ全体の状態管理
- 機能間の協調ロジック
- 集約のみ、データ取得しない

**使えるもの:**
```typescript
✅ Layer 4 フックの呼び出し
✅ useCallback（協調ロジック）
✅ 集約されたモデルの返却
```

**使えないもの:**
```typescript
❌ useEffect（データ取得）
❌ useQuery, useMutation（直接）
❌ useState（ページステート以外）
```

**コード例:**
```typescript
// ✅ 正しい Layer 3
export function useTodayPageModel({ date }: { date: string }) {
  // ✅ Layer 4 フックを集約
  const meals = useMealManagement({ date });
  const nutrition = useTodayNutritionProgress({ date });
  const mealSectionNutrition = useMealNutritionAutoLoader({
    date,
    meals: meals.mealItems,
    mealsPerDay: profile.profile?.meals_per_day ?? 3,
  });

  // ✅ 機能間の協調ロジック
  const handleMealUpdate = useCallback(async () => {
    await meals.refetch();
    await nutrition.refetchDailySummary();
  }, [meals, nutrition]);

  // ✅ 集約されたモデルを返す
  return {
    meals,
    nutrition,
    mealSectionNutrition,
    actions: { handleMealUpdate },
  };
}
```

---

### Layer 4: Feature Logic

**責務:**
- React Query による状態管理
- 非同期データフェッチング
- Layer 5 サービスの呼び出し
- UI向けデータ統合
- **useEffect でのデータ取得** ✅

**使えるもの:**
```typescript
✅ useQuery
✅ useMutation
✅ useEffect（データ取得）✨
✅ useState（ローカルステート）
✅ useCallback
✅ Layer 5 サービスの呼び出し
```

**使えないもの:**
```typescript
❌ JSX の返却（UI は Layer 1/2）
❌ イベントハンドラの直接定義（Layer 2 の責務）
```

**コード例:**
```typescript
// ✅ 正しい Layer 4
export function useMealNutritionAutoLoader({
  date,
  meals,
  mealsPerDay,
}: UseMealNutritionAutoLoaderProps) {
  const mealSectionNutrition = useMealSectionNutrition(date);

  // ✅ Layer 4 で useEffect を使用（データ取得）
  useEffect(() => {
    // メイン食事のデータを自動取得
    for (let i = 1; i <= mealsPerDay; i++) {
      const hasMeals = meals.some(
        m => m.meal_type === 'main' && m.meal_index === i
      );
      if (hasMeals) {
        mealSectionNutrition.getFromServer('main', i);
      }
    }

    // 間食のデータを自動取得
    const hasSnacks = meals.some(m => m.meal_type === 'snack');
    if (hasSnacks) {
      mealSectionNutrition.getFromServer('snack');
    }
  }, [date, meals, mealsPerDay, mealSectionNutrition]);

  return mealSectionNutrition;
}
```

---

### Layer 5: Domain Services

**責務:**
- API呼び出し
- ドメイン固有のビジネスロジック
- データ変換
- React 非依存

**使えるもの:**
```typescript
✅ async/await
✅ API クライアント呼び出し
✅ データ変換ロジック
✅ バリデーション
```

**使えないもの:**
```typescript
❌ React フック（use*）
❌ JSX
❌ React Query
```

**コード例:**
```typescript
// ✅ 正しい Layer 5
export class NutritionService implements INutritionService {
  async fetchMealNutrition(
    date: string,
    mealType: MealType,
    mealIndex?: number
  ): Promise<MealAndDailyNutritionResponse> {
    // ✅ API呼び出し
    return computeNutritionData({
      date,
      meal_type: mealType,
      meal_index: mealIndex ?? null,
    });
  }

  // ✅ ドメインロジック
  validateNutritionData(summary: DailyNutritionSummary | null): boolean {
    if (!summary) return false;
    if (!summary.nutrients || summary.nutrients.length === 0) return false;

    const requiredNutrients = ['protein', 'fat', 'carbohydrate'];
    return requiredNutrients.every(nutrient =>
      summary.nutrients.some(n => n.code === nutrient)
    );
  }
}
```

---

## 実際の問題事例

### 事例: MealListSection に useEffect がある

**問題のコード:**
```typescript
// ❌ shared/ui/sections/MealListSection.tsx (Layer 1)

const MealIndexSection = React.memo(function MealIndexSection({
  mealType,
  mealIndex,
  nutritionAnalysis,
  // ...
}) {
  // ❌ Layer 1 に useEffect がある！
  useEffect(() => {
    if (!hasNutritionData && hasItems && nutritionAnalysis.getFromServer) {
      nutritionAnalysis.getFromServer(mealType, mealIndex);
    }
  }, [mealType, mealIndex, hasItems, hasNutritionData]);

  // ...
});
```

**何が問題か:**

1. **Layer 1 の原則違反**
   - MealListSection は `shared/ui/sections/` にある
   - Layer 1（Presentation）として設計されている
   - 純粋な表現のみを持つべき

2. **副作用の配置ミス**
   - useEffect でデータ取得している
   - これは Layer 4 の責務

3. **再利用性の低下**
   - 特定のデータ取得ロジックに依存
   - 他のページで再利用しにくい

4. **テスタビリティの低下**
   - 副作用があるため、単体テストが困難
   - props だけでテストできない

---

## 修正内容

### Step 1: 新しい Layer 4 フックを作成

**ファイル:** `/workspace/frontend/src/modules/today/hooks/useMealNutritionAutoLoader.ts`

```typescript
/**
 * useMealNutritionAutoLoader - Layer 4: Feature Logic
 *
 * 責務:
 * - 初回ロード時に各食事セクションの栄養データを自動取得
 * - サーバーに既存データがあれば復元
 * - React Query のキャッシュを活用
 */
export function useMealNutritionAutoLoader({
  date,
  meals,
  mealsPerDay,
}: UseMealNutritionAutoLoaderProps): MealSectionNutritionManager {
  const mealSectionNutrition = useMealSectionNutrition(date);

  // ✅ Layer 4 で useEffect を使用（正しい配置）
  useEffect(() => {
    // メイン食事（食事1, 食事2, ...）
    for (let i = 1; i <= mealsPerDay; i++) {
      const hasMeals = meals.some(
        m => m.meal_type === 'main' && (m.meal_index ?? 1) === i
      );

      if (hasMeals) {
        // サーバーから既存データを取得（404なら何もしない）
        mealSectionNutrition.getFromServer('main', i);
      }
    }

    // 間食
    const hasSnacks = meals.some(m => m.meal_type === 'snack');
    if (hasSnacks) {
      mealSectionNutrition.getFromServer('snack');
    }
  }, [date, meals, mealsPerDay, mealSectionNutrition]);

  return mealSectionNutrition;
}
```

**ポイント:**
- ✅ Layer 4 に配置
- ✅ useEffect でデータ取得
- ✅ 各食事セクションのデータを自動取得
- ✅ 依存配列に必要な値を含める

---

### Step 2: Layer 3 で新しいフックを使用

**ファイル:** `/workspace/frontend/src/modules/today/model/useTodayPageModel.ts`

```typescript
export function useTodayPageModel({ date }: UseTodayPageModelProps) {
  // Layer 4: Feature Hooks
  const nutrition = useTodayNutritionProgress({ date });
  const meals = useMealManagement({ date });
  const profile = useProfileManagement();

  // ✅ 新しい Layer 4 フックを使用
  const mealSectionNutrition = useMealNutritionAutoLoader({
    date,
    meals: meals.mealItems,
    mealsPerDay: profile.profile?.meals_per_day ?? 3,
  });

  // ✅ Layer 3 は集約のみ
  return {
    nutrition,
    meals,
    profile,
    mealSectionNutrition,
    // ...
  };
}
```

**ポイント:**
- ✅ Layer 3 は Layer 4 フックを呼ぶだけ
- ✅ useEffect は使わない
- ✅ 集約のみ

---

### Step 3: Layer 1 から useEffect を削除

**ファイル:** `/workspace/frontend/src/shared/ui/sections/MealListSection.tsx`

```typescript
const MealIndexSection = React.memo(function MealIndexSection({
  mealType,
  mealIndex,
  items,
  nutritionAnalysis,
  // ...
}: MealIndexSectionProps) {
  const hasItems = items.length > 0;

  // ✅ キャッシュから取得（副作用なし）
  const cachedNutritionData = nutritionAnalysis.getFromCache(
    mealType,
    mealIndex ?? undefined
  );
  const hasNutritionData = Boolean(cachedNutritionData);

  // ❌ 削除: useEffect
  // useEffect(() => {
  //   if (!hasNutritionData && hasItems) {
  //     nutritionAnalysis.getFromServer(mealType, mealIndex);
  //   }
  // }, [mealType, mealIndex, hasItems, hasNutritionData]);

  // ✅ 純粋な表現のみ
  return (
    <div>
      {hasItems && (
        <>
          <Button onClick={onAnalyze}>栄養分析</Button>
          {hasNutritionData && (
            <Button onClick={() => nutritionAnalysis.onShowDetails(cachedData)}>
              詳細表示
            </Button>
          )}
        </>
      )}
    </div>
  );
});
```

**ポイント:**
- ✅ useEffect を削除
- ✅ props から値を取得するのみ
- ✅ 純粋なプレゼンテーション

---

## Before/After 比較

### Before（問題のある設計）

```
┌─────────────────────────────────────────┐
│ Layer 1: MealListSection                │
│   ❌ useEffect でデータ取得             │
│   ❌ 副作用がある                       │
│   ❌ 再利用性が低い                     │
└─────────────────────────────────────────┘
              ↑
┌─────────────────────────────────────────┐
│ Layer 2: TodayPageContent               │
│   ⚠️ もし useEffect を追加したら...    │
│   ❌ Layer 2 も副作用を持つことに       │
└─────────────────────────────────────────┘
              ↑
┌─────────────────────────────────────────┐
│ Layer 3: useTodayPageModel              │
│   ✅ 集約のみ                           │
└─────────────────────────────────────────┘
              ↑
┌─────────────────────────────────────────┐
│ Layer 4: useMealSectionNutrition        │
│   ✅ 手動でデータ取得                   │
│   ⚠️ 自動取得の仕組みなし               │
└─────────────────────────────────────────┘
```

**問題点:**
- ❌ Layer 1 に副作用（useEffect）がある
- ❌ 責務が不明確
- ❌ データ取得ロジックが分散
- ❌ リロード後にデータが消える

---

### After（正しい設計）

```
┌─────────────────────────────────────────┐
│ Layer 1: MealListSection                │
│   ✅ 純粋なプレゼンテーション           │
│   ✅ props のみで制御                   │
│   ✅ 再利用可能                         │
└─────────────────────────────────────────┘
              ↑ props
┌─────────────────────────────────────────┐
│ Layer 2: TodayPageContent               │
│   ✅ UI協調、イベントハンドリング      │
│   ✅ Layer 3 モデルを消費               │
└─────────────────────────────────────────┘
              ↑ model
┌─────────────────────────────────────────┐
│ Layer 3: useTodayPageModel              │
│   ✅ Layer 4 フックを集約               │
└─────────────────────────────────────────┘
              ↑
┌─────────────────────────────────────────┐
│ Layer 4: useMealNutritionAutoLoader ✨  │
│   ✅ useEffect でデータ自動取得         │
│   ✅ サーバーから既存データを復元       │
│   ✅ 正しい場所にロジックを配置         │
└─────────────────────────────────────────┘
              ↑
┌─────────────────────────────────────────┐
│ Layer 5: NutritionService               │
│   ✅ API呼び出し                        │
└─────────────────────────────────────────┘
```

**改善点:**
- ✅ Layer 1 が純粋なプレゼンテーションに
- ✅ 責務が明確
- ✅ データ取得ロジックが Layer 4 に集約
- ✅ リロード後もデータが復元される

---

## データフロー

### 初回ロード時

```
1. ページロード
   └─> TodayPage (app/today/page.tsx)

2. TodayPageContent がレンダリング
   └─> useTodayPageModel({ date })

3. Layer 3: useTodayPageModel
   ├─> useMealManagement({ date })  // 食事データ取得
   │    └─> React Query: ['meals', date]
   │
   └─> useMealNutritionAutoLoader({ date, meals, mealsPerDay }) ✨
        └─> useEffect 実行
             ├─> getFromServer('main', 1)  // 食事1のデータ取得
             │    └─> GET /api/nutrition/meal?date=...&meal_type=main&meal_index=1
             │         └─> React Query キャッシュに保存
             │
             ├─> getFromServer('main', 2)  // 食事2のデータ取得
             │    └─> GET /api/nutrition/meal?date=...&meal_type=main&meal_index=2
             │         └─> React Query キャッシュに保存
             │
             └─> getFromServer('snack')     // 間食のデータ取得
                  └─> GET /api/nutrition/meal?date=...&meal_type=snack
                       └─> React Query キャッシュに保存

4. MealListSection がレンダリング
   └─> getFromCache('main', 1)
        └─> キャッシュにデータあり ✅
        └─> hasNutritionData = true
        └─> 「詳細表示」ボタン表示 ✅
```

### リロード時（修正後）

```
1. ページリロード
   └─> React Query のメモリキャッシュがクリア

2. TodayPageContent がレンダリング
   └─> useTodayPageModel({ date })

3. Layer 3: useTodayPageModel
   └─> useMealNutritionAutoLoader({ date, meals, mealsPerDay }) ✨
        └─> useEffect が再実行
             └─> 各食事セクションのデータを自動取得
                  ├─> getFromServer('main', 1)
                  │    └─> GET /api/nutrition/meal (サーバーから取得)
                  │         └─> キャッシュに保存 ✅
                  │
                  ├─> getFromServer('main', 2)
                  │    └─> GET /api/nutrition/meal (サーバーから取得)
                  │         └─> キャッシュに保存 ✅
                  │
                  └─> getFromServer('snack')
                       └─> GET /api/nutrition/meal (サーバーから取得)
                            └─> キャッシュに保存 ✅

4. MealListSection がレンダリング
   └─> getFromCache('main', 1)
        └─> キャッシュにデータあり ✅
        └─> hasNutritionData = true
        └─> 「詳細表示」ボタン表示 ✅
```

### 栄養分析実行時

```
1. ユーザーが「栄養分析」ボタンをクリック
   └─> TodayPageContent の handleNutritionAnalysis

2. Layer 4: fetchNutrition
   └─> POST /api/nutrition/meal/compute
        └─> OpenAI で栄養計算
        └─> サーバーDB に保存
        └─> React Query キャッシュに保存

3. Layer 2: selectMealForNutrition
   └─> 選択状態を更新
   └─> MealListSection 内に簡易サマリー表示

4. MealListSection が再レンダリング
   └─> hasNutritionData = true
   └─> 「詳細表示」ボタン表示 ✅
```

---

## ベストプラクティス

### 1. useEffect の配置場所を判断する

**質問:** "この useEffect はどの Layer に配置すべきか？"

**判断フロー:**

```
useEffect の目的は？
  ├─> データ取得（API呼び出し）
  │    └─> ✅ Layer 4
  │
  ├─> DOM操作（ref.current.focus()）
  │    └─> ✅ Layer 1 または Layer 2（例外的に許可）
  │
  ├─> サブスクリプション（WebSocket等）
  │    └─> ✅ Layer 4
  │
  ├─> ローカルストレージ同期
  │    └─> ✅ Layer 4
  │
  └─> アナリティクス（ページビュー追跡）
       └─> ✅ Layer 2 または専用フック
```

### 2. 新しいデータ取得機能を追加する場合

**Step 1: Layer 5 にサービスを追加**
```typescript
// services/someService.ts
export class SomeService {
  async fetchData(params) {
    return apiClient.get('/some-endpoint', { params });
  }
}
```

**Step 2: Layer 4 にフックを追加**
```typescript
// hooks/useSomeData.ts
export function useSomeData(params) {
  const service = useSomeService();

  const query = useQuery({
    queryKey: ['some-data', params],
    queryFn: () => service.fetchData(params),
  });

  // 必要に応じて useEffect
  useEffect(() => {
    // 初回取得や自動更新のロジック
  }, [params]);

  return {
    data: query.data,
    isLoading: query.isLoading,
    // ...
  };
}
```

**Step 3: Layer 3 で集約**
```typescript
// model/usePageModel.ts
export function usePageModel() {
  const someData = useSomeData(params);
  const otherData = useOtherData();

  return {
    someData,
    otherData,
  };
}
```

**Step 4: Layer 1/2 で消費**
```typescript
// ui/PageContent.tsx
export function PageContent() {
  const model = usePageModel();

  return (
    <Section data={model.someData.data} />
  );
}
```

### 3. コンポーネントを作成する際のチェックリスト

**Layer 1 コンポーネントを作る場合:**

```typescript
// ✅ チェックリスト
const checklist = {
  // 必須
  propsで制御される: true,
  副作用がない: true,
  useEffectがない: true,
  ReactQueryがない: true,

  // 許可される
  条件分岐表示: true,
  配列のmap: true,
  ReactMemo: true,

  // 例外的に許可
  localUIState: 'ドロップダウンの開閉状態などのみ',

  // NG
  データ取得: false,
  ビジネスロジック: false,
};
```

**Layer 4 フックを作る場合:**

```typescript
// ✅ チェックリスト
const checklist = {
  // 必須
  useQueryかuseMutationを使用: true,
  Layer5サービスを呼び出す: true,

  // 許可される
  useEffect: true,  // データ取得のため
  useState: true,   // ローカルステート
  useCallback: true,

  // NG
  JSXを返す: false,
  UIロジック: false,
};
```

### 4. リファクタリング時の手順

**既存コードに useEffect がある場合:**

1. **現在の配置場所を確認**
   ```typescript
   // ファイルパスで判断
   // shared/ui/sections/ → Layer 1
   // ui/TodayPageContent.tsx → Layer 1/2
   // model/usePageModel.ts → Layer 3
   // hooks/useFeature.ts → Layer 4
   ```

2. **useEffect の目的を確認**
   ```typescript
   // データ取得？ → Layer 4 に移動
   // DOM操作？ → そのまま（例外的に許可）
   // サブスクリプション？ → Layer 4 に移動
   ```

3. **Layer 4 フックを作成**
   ```typescript
   // hooks/useDataAutoLoader.ts
   export function useDataAutoLoader() {
     useEffect(() => {
       // データ取得ロジック
     }, []);
   }
   ```

4. **Layer 3 で使用**
   ```typescript
   export function usePageModel() {
     const data = useDataAutoLoader();
     return { data };
   }
   ```

5. **Layer 1 から useEffect を削除**
   ```typescript
   // useEffect を削除
   // props から値を取得するのみ
   ```

---

## よくある間違い

### 間違い1: Layer 1 に useEffect を追加

```typescript
// ❌ 間違い
export function SomeSection({ data }) {
  useEffect(() => {
    // データ取得
    fetchData().then(setData);
  }, []);

  return <div>{data}</div>;
}
```

**なぜダメか:**
- Layer 1 は純粋なプレゼンテーションのはず
- 副作用を持つべきではない
- 再利用性が低下

**正しい修正:**
```typescript
// ✅ 正しい
// Layer 1
export function SomeSection({ data, isLoading }) {
  if (isLoading) return <Loading />;
  return <div>{data}</div>;
}

// Layer 4
export function useSomeData() {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchData().then((result) => {
      setData(result);
      setIsLoading(false);
    });
  }, []);

  return { data, isLoading };
}
```

---

### 間違い2: Layer 3 に useQuery を追加

```typescript
// ❌ 間違い
export function usePageModel() {
  // Layer 3 で直接 useQuery を使用
  const dataQuery = useQuery({
    queryKey: ['data'],
    queryFn: fetchData,
  });

  return { data: dataQuery.data };
}
```

**なぜダメか:**
- Layer 3 は集約のみの責務
- データ取得は Layer 4 の責務

**正しい修正:**
```typescript
// ✅ 正しい
// Layer 4
export function useSomeData() {
  return useQuery({
    queryKey: ['data'],
    queryFn: fetchData,
  });
}

// Layer 3
export function usePageModel() {
  const someData = useSomeData();  // Layer 4 を集約
  return { someData };
}
```

---

### 間違い3: Layer 2 にビジネスロジックを追加

```typescript
// ❌ 間違い
export function PageContent() {
  const model = usePageModel();

  // Layer 2 にビジネスロジック
  const calculateTotal = (items) => {
    return items.reduce((sum, item) => {
      const tax = item.price * 0.1;
      const discount = item.discount || 0;
      return sum + item.price + tax - discount;
    }, 0);
  };

  const total = calculateTotal(model.items);

  return <div>合計: {total}</div>;
}
```

**なぜダメか:**
- ビジネスロジックは Layer 4 または Layer 5
- Layer 2 は UI協調のみ

**正しい修正:**
```typescript
// ✅ 正しい
// Layer 5
export class OrderService {
  calculateTotal(items: OrderItem[]): number {
    return items.reduce((sum, item) => {
      const tax = item.price * 0.1;
      const discount = item.discount || 0;
      return sum + item.price + tax - discount;
    }, 0);
  }
}

// Layer 4
export function useOrderCalculation(items) {
  const service = useOrderService();

  const total = useMemo(
    () => service.calculateTotal(items),
    [items, service]
  );

  return { total };
}

// Layer 3
export function usePageModel() {
  const items = useOrderItems();
  const calculation = useOrderCalculation(items);

  return { items, calculation };
}

// Layer 2
export function PageContent() {
  const model = usePageModel();
  return <div>合計: {model.calculation.total}</div>;
}
```

---

## チェックリスト

### コードレビュー時のチェック項目

#### Layer 1 のチェック

- [ ] props のみで制御されているか
- [ ] useEffect（データ取得）がないか
- [ ] useQuery/useMutation がないか
- [ ] ビジネスロジックがないか
- [ ] 副作用がないか（DOM操作除く）

#### Layer 2 のチェック

- [ ] useEffect（データ取得）がないか
- [ ] useQuery/useMutation がないか
- [ ] イベントハンドラが適切に定義されているか
- [ ] Layer 3 モデルを消費しているか

#### Layer 3 のチェック

- [ ] Layer 4 フックを集約しているか
- [ ] useQuery/useMutation を直接使用していないか
- [ ] useEffect（データ取得）がないか
- [ ] 集約ロジックのみになっているか

#### Layer 4 のチェック

- [ ] useQuery または useMutation を使用しているか
- [ ] Layer 5 サービスを呼び出しているか
- [ ] useEffect が必要な場合、適切に使用されているか
- [ ] JSX を返していないか

#### Layer 5 のチェック

- [ ] React フックを使用していないか
- [ ] API呼び出しが適切に実装されているか
- [ ] ドメインロジックが適切に実装されているか

---

## まとめ

### 重要な原則

1. **データ取得は Layer 4 のみ**
   - useEffect でのデータ取得は Layer 4
   - Layer 1/2/3 にはデータ取得の useEffect を置かない

2. **Layer 1 は純粋なプレゼンテーション**
   - props のみで制御
   - 副作用なし
   - 再利用可能

3. **Layer 2 は UI協調のみ**
   - イベントハンドリング
   - モーダル状態管理
   - データ取得しない

4. **Layer 3 は集約のみ**
   - Layer 4 フックを集約
   - データ取得しない
   - React Query を直接使わない

5. **Layer 4 はデータ管理**
   - React Query
   - useEffect（データ取得）
   - Layer 5 サービスの呼び出し

### 今回の学び

**問題:**
- リロード後に「詳細表示」ボタンが消える
- Layer 1 に useEffect を追加してしまった

**解決:**
- Layer 4 に専用フック（useMealNutritionAutoLoader）を作成
- useEffect を Layer 4 に配置
- Layer 1 から useEffect を削除
- 正しいレイヤー設計を実現

**効果:**
- リロード後もデータが復元される
- Layer の責務が明確になった
- 再利用性が向上した
- テスタビリティが向上した

---

## 参考資料

### 関連ドキュメント

- `/workspace/docs/ai/frontend/5-layer-architecture-guide.v2.md` - 5層アーキテクチャガイド
- `/workspace/docs/ai/frontend/today-module-structure.md` - Today モジュール構造ガイド
- `/workspace/docs/ai/frontend/modal-5layer-refactoring-guide.md` - モーダルリファクタリングガイド

### 実装例

- `/workspace/frontend/src/modules/today/hooks/useMealNutritionAutoLoader.ts` - Layer 4 フックの実装例
- `/workspace/frontend/src/modules/today/model/useTodayPageModel.ts` - Layer 3 集約の実装例
- `/workspace/frontend/src/shared/ui/sections/MealListSection.tsx` - Layer 1 プレゼンテーションの実装例

---

**最終更新:** 2026-02-06
**対象バージョン:** Next.js 16, React 19
**作成者:** Claude Sonnet 4.5 (AI Assistant)
