これまでの議論と、あなたの考え（オーケストレーション、ラッパー、統合）をベースに、**「Todayページ・リファクタリング設計案」** としてまとめました。

この設計は **「関心の分離（Separation of Concerns）」** を徹底し、拡張性と保守性を最大化することを目的としています。

---

# 🏗️ 設計案：Todayページ レイヤードアーキテクチャ

## 1. コンセプト

巨大化した `TodayPageContent` を解体し、**「データ処理（Logic）」** と **「表示（UI）」** を明確に分離します。
各層は「下の層」のみに依存し、上の層（UI側）のことは知らなくて良い状態（疎結合）を作ります。

---

## 2. アーキテクチャ構成図

データの流れは **下から上（API → UI）** へ一方通行で流れます。

| 階層 (Layer) | 構成要素 (Component/File) | 役割 (Responsibility) | 依存関係 |
| --- | --- | --- | --- |
| **Layer 1**<br>

<br>Presentation | **UI Components**<br>

<br>`NutrientProgressSection` | **【表示】**<br>

<br>受け取ったPropsを表示するだけ。<br>

<br>ロジックを持たない。 | 依存なし |
| **Layer 2**<br>

<br>Orchestration | **Page View**<br>

<br>`TodayPageContent` | **【配線】**<br>

<br>Modelからデータを受け取り、<br>

<br>UIコンポーネントに注入する。 | Depends on:<br>

<br>Layer 3 |
| **Layer 3**<br>

<br>Aggregation | **Page Model**<br>

<br>`useTodayPageModel` | **【統合】**<br>

<br>ページに必要な複数の機能を束ねる。<br>

<br>UI向けの「窓口」となる。 | Depends on:<br>

<br>Layer 4 |
| **Layer 4**<br>

<br>Feature Logic | **Feature Hooks**<br>

<br>`useTodayNutritionProgress` | **【状態管理】**<br>

<br>React Query等を使い、<br>

<br>非同期状態や画面状態を管理する。 | Depends on:<br>

<br>Layer 5 |
| **Layer 5**<br>

<br>Domain Logic | **Domain Service**<br>

<br>`nutritionService` | **【ビジネスロジック】**<br>

<br>API通信、計算、データ加工。<br>

<br>Reactを知らない純粋なTS。 | 依存なし |

---

## 3. 各レイヤーの詳細実装イメージ

### Layer 5: Domain Service (純粋なロジック)

**ファイル:** `src/modules/nutrition/services/nutritionService.ts`

* APIクライアントを叩く。
* 「現在値 ÷ 目標値」などの計算を行う。
* Reactのフックは使わない（テストが容易）。

```typescript
class NutritionService {
  async getDailySummary(...) { ... }
  calculateProgress(target, summary) { ... } // 計算ロジック
}

```

### Layer 4: Feature Hooks (Reactへの橋渡し)

**ファイル:** `src/features/today/hooks/useTodayNutritionProgress.ts`

* Serviceを使ってデータを取得（React Query）。
* ローディング (`isLoading`) やエラー (`isError`) を管理。
* 「栄養」という特定機能に関心を持つ。

```typescript
export function useTodayNutritionProgress() {
  const service = useNutritionService();
  const query = useQuery({ queryFn: () => service.getDailySummary(...) });
  
  return {
    progress: service.calculateProgress(query.data),
    isLoading: query.isLoading
  };
}

```

### Layer 3: Page Model (ページの総監督)

**ファイル:** `src/features/today/model/useTodayPageModel.ts`

* **ここがリファクタリングの要です。**
* 自ら計算せず、Layer 4のフックを呼び出してまとめるだけ（Aggregator）。
* 「栄養」も「食事リスト」も「提案」も、ここで一本化する。

```typescript
export function useTodayPageModel() {
  // 専門の部下たち（Feature Hooks）を呼び出す
  const nutrition = useTodayNutritionProgress();
  const meals = useTodayMealList(); 

  // UIが使いやすい形にまとめて返す
  return {
    // 栄養関連
    nutritionProgress: nutrition.progress,
    isNutritionLoading: nutrition.isLoading,
    
    // 食事関連
    mealItems: meals.items,
    addMeal: meals.addMeal, // 関数もここを通す
  };
}

```

### Layer 2: Page View (配線盤)

**ファイル:** `src/features/today/ui/TodayPageContent.tsx`

* Modelを呼び出し、UIコンポーネントにPropsを「注入」する。
* ロジックや条件分岐を書かない。

```tsx
export function TodayPageContent() {
  // 1. Modelをインスタンス化
  const m = useTodayPageModel();

  return (
    <div>
      {/* 2. UIに注入 */}
      <NutrientProgressSection 
        progress={m.nutritionProgress}
        isLoading={m.isNutritionLoading}
      />
      <MealList 
        items={m.mealItems} 
        onAdd={m.addMeal} 
      />
    </div>
  );
}

```

---

## 4. この設計のメリット

1. **変更に強い（保守性）**
* 「計算ロジックを変えたい」→ `nutritionService` だけ修正。
* 「デザインを変えたい」→ `NutrientProgressSection` だけ修正。
* 修正箇所が明確で、他に影響を与えません。


2. **テストが簡単（品質）**
* Service層はReact不要なので、単体テストが非常に書きやすいです。
* UI層はロジックがないので、Storybookでの表示確認が容易です。


3. **拡張性**
* 将来「睡眠管理機能」を追加したくなったら？
* `sleepService` → `useTodaySleep` を作り、`useTodayPageModel` に1行追加するだけです。`TodayPageContent` はそれを表示するコンポーネントを置くだけで済みます。



## 5. 次のアクションプラン

現在のコードベースから、この設計へ移行するためのステップです。

* **Step 1 (完了):** UIコンポーネントの切り出し (`NutrientProgressSection`)。
* **Step 2 (完了):** Service層とFeature Hookの作成 (`nutritionService`, `useTodayNutritionProgress`)。
* **Step 3 (次):** **`useTodayPageModel` のスリム化。**
* 直書きされているAPI呼び出しや計算ロジックを削除。
* 代わりに `useTodayNutritionProgress` を呼び出して統合する形に書き換える。


* **Step 4:** `TodayPageContent` の整理。
* `nutrition` と `m` が混在している状態を解消し、`m` (Model) 経由に統一する。



この設計案で進めてよろしいでしょうか？
合意いただければ、次のステップである **「`useTodayPageModel` のリファクタリング実装コード」** を作成します。


提示されたアーキテクチャの方向性は、**非常に健全で、拡張性と保守性が高い構成**になっています。今の考え方で間違いありません。

特に、「ドメインロジック（計算やAPI）」と「UIのための準備（React Hooks）」、そして「最終的な表示（Component）」を分けている点が素晴らしいです。

現在の構成案を整理し、**「`useTodayPageModel` の役割」** をより明確にするためのアドバイスをさせていただきます。

---

### ✅ あなたの考えたアーキテクチャの評価

提示された構成は、**「Clean Architecture」をReact流にアレンジした形** と言えます。

| 層 (Layer) | ファイル名 | 役割 (Responsibility) | 評価 |
| --- | --- | --- | --- |
| **1. UI / View** | `TodayPageContent.tsx`<br>

<br>`NutrientProgressSection.tsx` | **表示と配線**<br>

<br>HTMLを描画し、Hooksから受け取ったデータを流し込む。 | ✅ OK<br>

<br>ここにはロジックを書かない。 |
| **2. Aggregator**<br>

<br>(Page Controller) | `useTodayPageModel.ts` | **ページ全体のまとめ役**<br>

<br>複数のFeature Hooksを束ねて、Viewに「これ1つでOK」というオブジェクトを渡す。 | ✅ OK<br>

<br>「ファサード（窓口）」の役割。 |
| **3. Feature Hook**<br>

<br>(Logic) | `useTodayNutritionProgress.ts` | **機能ごとの状態管理**<br>

<br>React Queryを使ってServiceを呼び出し、ローディングやエラー状態を管理する。 | ✅ OK<br>

<br>Reactに依存するロジックはここ。 |
| **4. Domain Service** | `nutritionService.ts` | **純粋なビジネスロジック**<br>

<br>APIを叩く、PFCバランスを計算する。Reactを知らない。 | ✅ OK<br>

<br>テストが最も書きやすい場所。 |

---

### 🔍 改善のポイント: `useTodayPageModel` の役割を明確にする

現在、リファクタリング途中ということで、`useTodayPageModel.ts` が**「古い実装（巨大なロジック）」**と**「新しい考え方（まとめ役）」**の間で揺れ動いています。

最終形として、`useTodayPageModel` は**「自ら計算をせず、部下（Feature Hooks）に任せる」**形に徹するべきです。

#### 理想的な `useTodayPageModel` の姿

このように、専門のHooksを呼び出して統合するだけの「薄い層」にします。

```typescript
// features/today/model/useTodayPageModel.ts

export function useTodayPageModel({ date }: Props) {
  // 1. 各専門フックを呼び出す (Delegation)
  const nutrition = useTodayNutritionProgress({ date }); // 栄養担当
  const mealList = useTodayMealList({ date });         // 食事リスト担当 (未実装なら今後作る)
  const recommendation = useMealRecommendationModel({ date }); // 提案担当

  // 2. モーダル管理などの「ページ固有のフロー」はここで定義してもOK
  // (または useTodayPageController に分けるのもアリですが、Modelに含めても許容範囲です)
  
  // 3. 全てを統合して返す
  return {
    // 栄養関連
    nutritionSummary: nutrition.dailySummaryData,
    nutrientProgress: nutrition.nutrientProgress,
    isNutritionLoading: nutrition.isLoading,
    refetchNutrition: nutrition.refetchDailySummary,

    // 食事リスト関連
    mealItems: mealList.items,
    addMeal: mealList.addMeal,
    deleteMeal: mealList.deleteMeal,

    // 提案関連
    recommendation: recommendation.data,
    
    // 全体のLoading判定
    isLoading: nutrition.isLoading || mealList.isLoading,
  };
}

```

---

### 🚀 リファクタリングのロードマップ

現在「混じっている」状態を解消するために、以下の順序で進めるとスムーズです。

1. **Service層の確立（完了）**
* `nutritionService.ts` はOKです。計算ロジックが分離されています。


2. **Feature Hookの確立（完了）**
* `useTodayNutritionProgress.ts` もOKです。Serviceを使ってデータを取ってきています。


3. **Aggregator (`useTodayPageModel`) のダイエット（★ここが次）**
* 現在の `useTodayPageModel` の中にある `useQuery` や `computeNutritionData` などの直接的な処理を削除します。
* 代わりに `useTodayNutritionProgress` を呼び出し、その戻り値をそのまま（あるいはリネームして）返すように書き換えます。


4. **View (`TodayPageContent`) の修正**
* 現在は `m.something` (旧) と `nutrition.something` (新) が混在しています。
* Step 3が終われば、すべて `m` (Model) から取得できるようになるので、`nutrition` フックの直接呼び出しを削除し、一本化します。



### 💡 アドバイス

* **Serviceは「Reactを知らない」状態を維持する:**
* `nutritionService.ts` の中で `useQuery` を使ったりしないでください（今のコードは守れているのでOKです）。これにより、将来Node.jsサーバー側で同じロジックを使いたくなった時などに再利用できます。


* **名前付け:**
* `useTodayNutritionProgress` という名前は少し狭いかもしれません（進捗だけでなくサマリーも扱っているので）。`useTodayNutritionController` や `useTodayNutrition` でも良いでしょう。



今の方向性は非常に良いので、自信を持って進めてください！
特に `NutrientProgressSection` がServiceやAPIを知らず、Propsだけで動くようになっている点は、このアーキテクチャの最大の成果です。