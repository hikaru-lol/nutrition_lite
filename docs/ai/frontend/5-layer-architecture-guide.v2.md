# 5層レイヤードアーキテクチャ設計ガイド

## 概要

React/Next.js プロジェクトにおける5層レイヤードアーキテクチャの設計思想と実装パターンをまとめた包括的ガイドです。

## 設計思想

### 1. 階層化による責務分離

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

### 2. 依存関係の原則

- **単方向依存**: 上位層は下位層に依存するが、下位層は上位層を知らない
- **ドメイン分離**: 異なるドメイン間の直接的な依存を避ける
- **インターフェース境界**: 各層間は明確なインターフェースで分離

### 3. 段階的移行戦略

- **部分移行**: 特定の機能・コンポーネントから段階的に適用
- **並行稼働**: 既存システムを壊さずに新アーキテクチャを検証
- **漸進的改善**: 一度に全体を書き換えるのではなく、継続的に改善

## 層別実装パターン

### Layer 5: Domain Services（ドメインサービス層）

**責務**:
- 外部API呼び出し
- ドメイン固有のビジネスロジック
- データ変換・正規化

**実装パターン**:
```typescript
// services/nutritionService.ts
export class NutritionService {
  async getDailySummary(date: string, meal: MealIdentifier) {
    // 純粋なAPI呼び出し + データ変換
    const response = await recomputeMealAndDaily({ date, ...meal });
    return this.normalizeNutritionData(response);
  }

  private normalizeNutritionData(rawData: any) {
    // ドメイン固有のデータ正規化
  }
}

// 依存性注入パターン
export function useNutritionService(): NutritionService {
  return useMemo(() => new NutritionService(), []);
}
```

**設計原則**:
- 1つのドメインサービス = 1つの責務境界
- 他ドメインサービスへの直接依存は避ける
- React依存を含めない（純粋なロジック）

### Layer 4: Feature Logic（フィーチャーロジック層）

**責務**:
- React Queryによる状態管理
- 非同期データフェッチング協調
- UI向けデータ統合

**実装パターン**:
```typescript
// hooks/useTodayNutritionProgress.ts
export function useTodayNutritionProgress(props: Props): FeatureModel {
  // Layer 5サービス注入
  const nutritionService = useNutritionService();
  const targetService = useTargetService();

  // React Query状態管理
  const activeTargetQuery = useQuery({
    queryKey: ['targets', 'active'],
    queryFn: () => targetService.getActiveTarget(),
  });

  const dailySummaryQuery = useQuery({
    queryKey: ['nutrition', 'daily-summary', date],
    queryFn: () => nutritionService.getDailySummary(date, meal),
    enabled: activeTargetQuery.isSuccess,
  });

  // ビジネスロジック統合
  const progressData = useMemo(() => {
    return calculateProgressData(activeTargetQuery.data, dailySummaryQuery.data);
  }, [activeTargetQuery.data, dailySummaryQuery.data]);

  return {
    // UIに必要なデータとアクションを公開
    nutrientProgress: progressData.progress,
    isLoading: activeTargetQuery.isLoading || dailySummaryQuery.isLoading,
    refetch: () => dailySummaryQuery.refetch(),
  };
}
```

**設計原則**:
- 1つのフィーチャーフック = 1つの機能境界
- 複数ドメインサービスの協調を担う
- UIに最適化されたインターフェースを提供

### Layer 3: Page Aggregation（ページ集約層）

**責務**:
- ページレベルでの複数機能統合
- ページ状態の一元管理
- 機能間の協調

**実装パターン**:
```typescript
// model/useTodayPageModel.ts
export function useTodayPageModel(props: Props) {
  // Layer 4フィーチャーフック統合
  const nutrition = useTodayNutritionProgress({ date });
  const meals = useMealManagement({ date });
  const reports = useDailyReports({ date });

  // ページレベル状態管理
  const [selectedModal, setSelectedModal] = useState<ModalType | null>(null);

  // 機能間協調ロジック
  const handleNutritionAnalysis = useCallback(async (mealType, mealIndex) => {
    await meals.fetchMealNutrition(mealType, mealIndex);
    // 栄養分析完了後に進捗更新をトリガー
    nutrition.refetch();
  }, [meals, nutrition]);

  return {
    // 各機能のデータとアクション
    nutrition,
    meals,
    reports,

    // ページレベルの状態とアクション
    selectedModal,
    setSelectedModal,
    handleNutritionAnalysis,

    // 全体状態
    isLoading: nutrition.isLoading || meals.isLoading,
    isError: nutrition.isError || meals.isError,
  };
}
```

**設計原則**:
- 1つのページモデル = 1つのページスコープ
- フィーチャー間の協調を担う
- 複雑な状態管理はここに集約

### Layer 2: UI Orchestration（UI協調層）

**責務**:
- UI コンポーネント間の協調
- イベントハンドリング
- モーダル・フォーム状態管理

**実装パターン**:
```typescript
// ui/TodayPageContent.tsx
export function TodayPageContent({ date }: Props) {
  // Layer 3ページモデル利用
  const m = useTodayPageModel({ date });

  // UIレベル状態管理
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [selectedMealType, setSelectedMealType] = useState<'main' | 'snack'>('main');

  // イベントハンドラ
  const handleAddClick = (mealType: 'main' | 'snack', mealIndex?: number) => {
    setSelectedMealType(mealType);
    setIsAddModalOpen(true);
  };

  const handleNutritionAnalysis = async (mealType: 'main' | 'snack', mealIndex?: number) => {
    await m.handleNutritionAnalysis(mealType, mealIndex);
    // UI固有のフィードバック
    toast.success('栄養分析完了');
  };

  // 条件付きレンダリング
  if (m.isLoading) return <LoadingState />;
  if (m.isError) return <ErrorState onRetry={() => router.refresh()} />;

  return (
    <div className="space-y-6">
      {/* Layer 1コンポーネント協調 */}
      <NutrientProgressSection
        activeTarget={m.nutrition.activeTarget}
        nutrientProgress={m.nutrition.nutrientProgress}
        isLoading={m.nutrition.isDailySummaryLoading}
        onRetry={m.nutrition.refetchDailySummary}
      />

      <CompactMealList
        mealItems={m.meals.items}
        onAddClick={handleAddClick}
        onAnalyzeNutrition={handleNutritionAnalysis}
      />

      {/* モーダル管理 */}
      <AddMealModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        mealType={selectedMealType}
      />
    </div>
  );
}
```

**設計原則**:
- UIコンポーネントのライフサイクル管理
- ユーザーインタラクションの橋渡し
- UI固有の状態（モーダル、フォーム等）を管理

### Layer 1: UI Presentation（UI表現層）

**責務**:
- 純粋な表現コンポーネント
- props による制御
- 再利用可能な UI 部品

**実装パターン**:
```typescript
// ui/sections/NutrientProgressSection.tsx
interface Props {
  activeTarget: Target | null;
  nutrientProgress: NutrientProgress[];
  isLoading: boolean;
  isError: boolean;
  onRetry: () => void;
  mealItemsCount: number;
}

export function NutrientProgressSection({
  activeTarget,
  nutrientProgress,
  isLoading,
  isError,
  onRetry,
  mealItemsCount,
}: Props) {
  // 純粋な表現ロジックのみ
  const hasData = activeTarget && nutrientProgress.length > 0;

  if (isLoading) return <Skeleton />;
  if (isError) return <ErrorState onRetry={onRetry} />;
  if (!hasData) return <EmptyState />;

  return (
    <Card>
      <CardHeader>
        <CardTitle>栄養目標達成度</CardTitle>
      </CardHeader>
      <CardContent>
        {nutrientProgress.map((progress) => (
          <NutrientProgressBar
            key={progress.code}
            label={progress.label}
            current={progress.current}
            target={progress.target}
            percentage={progress.percentage}
          />
        ))}
      </CardContent>
    </Card>
  );
}
```

**設計原則**:
- 外部依存を持たない
- props によるデータ注入のみ
- 副作用を含まない

## ファイル構成パターン

```
modules/{moduleName}/
├── services/                  # Layer 5
│   └── {module}Service.ts
├── hooks/                     # Layer 4
│   └── use{Module}Feature.ts
├── model/                     # Layer 3
│   └── use{Module}PageModel.ts
├── ui/                        # Layer 2 & 1
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

## 移行戦略

### 1. 段階的移行アプローチ

**フェーズ1: 特定機能の移行**
```typescript
// 既存コンポーネントを残しつつ、新しいアーキテクチャを部分適用
export function TodayPageContent() {
  // 既存のロジック（維持）
  const oldNutritionLogic = useOldNutritionLogic();

  // 新しいアーキテクチャ（特定機能のみ）
  const nutrition = useTodayNutritionProgress({ date });

  return (
    <>
      {/* 新アーキテクチャ適用済み */}
      <NutrientProgressSection
        activeTarget={nutrition.activeTarget}
        nutrientProgress={nutrition.nutrientProgress}
        // ...
      />

      {/* 既存実装（段階的に移行予定） */}
      <OldMealListComponent data={oldNutritionLogic.meals} />
    </>
  );
}
```

**フェーズ2: 全面移行**
```typescript
// 全ての機能を新アーキテクチャに移行
export function TodayPageContent() {
  const m = useTodayPageModel({ date });

  return (
    <>
      <NutrientProgressSection {...m.nutrition} />
      <NewMealListComponent {...m.meals} />
      <DailyReportSection {...m.reports} />
    </>
  );
}
```

### 2. 並行稼働による検証

```typescript
export function FeatureWithValidation() {
  // 既存実装
  const oldResult = useOldImplementation();

  // 新実装
  const newResult = useNewImplementation();

  // 開発環境でのみ比較検証
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      console.log('🔍 比較検証:', {
        old: oldResult.data,
        new: newResult.data,
        matches: deepEqual(oldResult.data, newResult.data)
      });
    }
  }, [oldResult.data, newResult.data]);

  // 本番では新実装を使用
  return process.env.NODE_ENV === 'production'
    ? newResult
    : oldResult;
}
```

### 3. 依存関係の整理手順

**ステップ1: ドメイン境界の特定**
```typescript
// Before: 混在した依存関係
import { Target, calculateNutrientProgress } from '@/modules/target';
import { DailyNutrition } from '@/modules/nutrition';

// After: 明確な境界分離
// nutritionService.ts - Nutritionドメインのみ
import { DailyNutrition } from '@/modules/nutrition/contract';

// nutritionProgressService.ts - 横断的関心事
import type { Target } from '@/modules/target/contract';
import type { DailyNutrition } from '@/modules/nutrition/contract';
```

**ステップ2: 責務の再分散**
```typescript
// Before: 単一サービスが複数ドメインを扱う
class NutritionService {
  calculateProgress(target: Target, nutrition: DailyNutrition) {
    // Target と Nutrition の両方を扱っている
  }
}

// After: 専用サービスに分離
class NutritionProgressService {
  calculateProgressData(target: Target | null, nutrition: DailyNutrition | null) {
    // 横断的関心事として独立
  }
}
```

## 適用ガイドライン

### 新機能開発時

1. **ドメイン分析**: 機能が属するドメインを特定
2. **責務分解**: Layer 5 → 4 → 3 → 2 → 1 の順で責務を分解
3. **インターフェース設計**: 各層間のインターフェースを先に設計
4. **ボトムアップ実装**: Layer 5から順に実装

### 既存機能リファクタリング時

1. **現状分析**: 既存の責務分散状況を分析
2. **移行計画**: 段階的移行計画を策定
3. **Layer 1から開始**: 表現層から始めて段階的に下位層をリファクタ
4. **並行稼働検証**: 新旧実装を並行稼働させて検証

### 品質保証

```typescript
// 各層の単体テスト例

// Layer 5: Domain Services
describe('NutritionService', () => {
  it('should normalize nutrition data correctly', async () => {
    const service = new NutritionService();
    const result = await service.getDailySummary('2024-01-01', mockMeal);
    expect(result).toMatchObject(expectedNormalizedData);
  });
});

// Layer 4: Feature Logic
describe('useTodayNutritionProgress', () => {
  it('should combine target and nutrition data', () => {
    const { result } = renderHook(() => useTodayNutritionProgress({ date: '2024-01-01' }));
    expect(result.current.nutrientProgress).toBeDefined();
  });
});

// Layer 1: UI Presentation
describe('NutrientProgressSection', () => {
  it('should render progress bars correctly', () => {
    render(<NutrientProgressSection {...mockProps} />);
    expect(screen.getByText('栄養目標達成度')).toBeInTheDocument();
  });
});
```

## ベストプラクティス

### 1. 命名規則

```typescript
// Layer 5: Services
class {Domain}Service {}
export function use{Domain}Service() {}

// Layer 4: Feature Logic
export function use{Domain}{Feature}() {}

// Layer 3: Page Aggregation
export function use{Page}PageModel() {}

// Layer 2: UI Orchestration
export function {Page}PageContent() {}

// Layer 1: UI Presentation
export function {Feature}Section() {}
```

### 2. TypeScript活用

```typescript
// 厳密な型定義による契約
interface FeatureModel {
  readonly data: ReadonlyArray<DataItem>;
  readonly isLoading: boolean;
  readonly error: Error | null;
  refetch(): Promise<void>;
}

// 層間インターフェースの明確化
interface Props {
  readonly activeTarget: Target | null;
  readonly nutrientProgress: readonly NutrientProgress[];
  readonly onRetry: () => void;
}
```

### 3. パフォーマンス最適化

```typescript
// React.memo for Layer 1 components
export const NutrientProgressSection = React.memo(function NutrientProgressSection(props: Props) {
  // Pure presentation logic
});

// useMemo for expensive computations
const progressData = useMemo(() =>
  calculateProgressData(target, nutrition),
  [target, nutrition]
);

// useCallback for stable references
const handleRetry = useCallback(() => {
  queryClient.invalidateQueries(['nutrition']);
}, [queryClient]);
```

## まとめ

この5層レイヤードアーキテクチャにより：

1. **保守性向上**: 責務が明確に分離され、変更影響範囲が限定
2. **テスタビリティ**: 各層が独立してテスト可能
3. **再利用性**: Layer 1, 4, 5 のコンポーネントは他機能でも再利用可能
4. **段階的移行**: 既存システムを壊さずに段階的に改善可能
5. **チーム開発**: 層別に作業分担が可能

他の機能にも同様のパターンを適用することで、統一性のある高品質なフロントエンドアーキテクチャを構築できます。

---

# 詳細解説：各レイヤーの完全理解

このセクションでは、5層レイヤードアーキテクチャの各レイヤーについて、より詳細かつ実践的な解説を提供します。

## 🔄 最重要原則：単方向データフロー

データと依存関係の流れは**単方向（上位から下位へ）**です。

```
データの流れ: Layer 5 → Layer 4 → Layer 3 → Layer 2 → Layer 1
依存の方向:  Layer 1 → Layer 2 → Layer 3 → Layer 4 → Layer 5
           （上位層は下位層に依存、下位層は上位層を知らない）

イベントの流れ: Layer 1 → Layer 2 → Layer 3 → Layer 4 → Layer 5
              （ユーザー操作が下位層のアクションをトリガー）
```

---

## 📚 各レイヤーの詳細解説

### Layer 1: UI Presentation（UI表現層）

**「純粋な見た目」- 状態を持たず、propsだけで描画**

#### ✅ このレイヤーがやること

```typescript
// 完全に純粋なコンポーネント
interface NutrientProgressSectionProps {
  // すべてpropsで受け取る
  activeTarget: Target | null;
  nutrientProgress: NutrientProgress[];
  isLoading: boolean;
  isError: boolean;
  onRetry: () => void;  // イベントもpropsで受け取る
  mealItemsCount: number;
}

export function NutrientProgressSection(props: NutrientProgressSectionProps) {
  // 1. propsの分割代入のみ
  const { activeTarget, nutrientProgress, isLoading, isError, onRetry, mealItemsCount } = props;

  // 2. 表示ロジックのみ（計算はOK、副作用はNG）
  const hasData = activeTarget && nutrientProgress.length > 0;
  const isEmpty = mealItemsCount === 0;

  // 3. 条件付きレンダリング（propsベース）
  if (isLoading) return <Skeleton />;
  if (isError) return <ErrorState onRetry={onRetry} />;
  if (isEmpty) return <EmptyState />;

  // 4. 純粋な表現
  return (
    <Card>
      <CardHeader>
        <CardTitle>栄養目標達成度</CardTitle>
      </CardHeader>
      <CardContent>
        {nutrientProgress.map((progress) => (
          <div key={progress.code}>
            <span>{progress.label}</span>
            <Progress value={progress.percentage} />
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
```

#### ❌ このレイヤーがやってはいけないこと

```typescript
// ❌ 状態管理
const [isOpen, setIsOpen] = useState(false);

// ❌ データ取得
const { data } = useQuery(...);
const nutrition = useTodayNutritionProgress();

// ❌ 副作用
useEffect(() => { ... });

// ❌ イベントハンドラー内でのロジック実装
<Button onClick={() => {
  // 複雑な処理はNG
  // propsで受け取った onXxx を呼ぶだけ
}} />

// ❌ 他モジュール依存
import { calculateNutrition } from '@/modules/nutrition';
```

#### 💡 このレイヤーの特徴

- **Container/Presentational パターンの Presentational**
- **完全に再利用可能**: どのページでも使える
- **Storybook対応**: propsを変えるだけでテスト可能
- **同じprops = 同じ表示**: 予測可能

---

### Layer 2: UI Orchestration（UI協調層）

**「UIの振る舞い」- モーダル管理の主戦場**

#### ✅ このレイヤーがやること

```typescript
// TodayPageContent.tsx (Layer 2コンポーネント)

export function TodayPageContent({ date }: Props) {
  const router = useRouter();

  // 1. Layer 3からデータを取得
  const m = useTodayPageModel({ date });

  // 2. UI固有状態管理（モーダルの主戦場！）
  const addMealModal = useAddMealModalState();      // モーダル開閉
  const editMealModal = useEditMealModalState();    // モーダル開閉
  const nutritionModal = useNutritionAnalysisModalState();

  // 3. UI固有の状態
  const [selectedTab, setSelectedTab] = useState<'overview' | 'detail'>('overview');

  // 4. イベントハンドラー（Layer 1からのイベント受け取り）
  const handleAddClick = (mealType: 'main' | 'snack', mealIndex?: number) => {
    // UI操作
    addMealModal.open(mealType, mealIndex);
  };

  const handleAddModalSubmit = async (values: AddMealFormValues) => {
    // Layer 3のアクション呼び出し
    await m.meals.addMeal(values);

    // UI操作
    addMealModal.close();

    // UIフィードバック
    toast.success('食事を追加しました');
  };

  // 5. 条件付きレンダリング（ページ全体）
  if (m.isLoading) return <LoadingState label="データを読み込み中..." />;
  if (m.isError) return <ErrorState onRetry={() => router.refresh()} />;

  // 6. Layer 1コンポーネントの配置と接続
  return (
    <div className="space-y-6">
      {/* Layer 3のデータをLayer 1に渡す */}
      <NutrientProgressSection
        activeTarget={m.nutrition.activeTarget}
        nutrientProgress={m.nutrition.nutrientProgress}
        isLoading={m.nutrition.isLoading}
        onRetry={m.nutrition.refetch}
        mealItemsCount={m.meals.mealItems.length}
      />

      <MealListSection
        mealItems={m.meals.mealItems}
        onAddClick={handleAddClick}
        onEditClick={handleEditClick}
      />

      {/* モーダル配置（Layer 2の主戦場） */}
      <AddMealModal
        isOpen={addMealModal.isOpen}
        onClose={addMealModal.close}
        onSubmit={handleAddModalSubmit}
        mealType={addMealModal.selectedMealType}
        mealIndex={addMealModal.selectedMealIndex}
      />
    </div>
  );
}
```

#### モーダル状態管理Hook（Layer 2専用）

```typescript
// useAddMealModalState.ts - Layer 2専用Hook

export function useAddMealModalState() {
  // モーダル固有のUI状態
  const [isOpen, setIsOpen] = useState(false);
  const [selectedMealType, setSelectedMealType] = useState<'main' | 'snack'>('main');
  const [selectedMealIndex, setSelectedMealIndex] = useState(1);

  // モーダル操作
  const open = useCallback((mealType: 'main' | 'snack', mealIndex?: number) => {
    setSelectedMealType(mealType);
    if (mealIndex) setSelectedMealIndex(mealIndex);
    setIsOpen(true);
  }, []);

  const close = useCallback(() => {
    setIsOpen(false);
  }, []);

  return { isOpen, selectedMealType, selectedMealIndex, open, close };
}
```

#### 💡 このレイヤーの特徴

- **モーダル管理の主戦場**: `useXxxModalState` はすべてLayer 2
- **Container/Presentational の Container**
- **UI固有の状態**: モーダル、タブ、アコーディオン、ドロワー等
- **Layer 1とLayer 3の繋ぎ役**: データとイベントの橋渡し
- **UIフィードバック**: toast, loading等

---

### Layer 3: Page Aggregation（ページ集約層）

**「ページ全体の司令塔」- 複数機能の統合と協調**

#### ✅ このレイヤーがやること

```typescript
// useTodayPageModel.ts - Layer 3

export function useTodayPageModel({ date }: Props) {
  // 1. 複数のLayer 4機能フックを統合
  const nutrition = useTodayNutritionProgress({ date });
  const meals = useMealManagement({ date });
  const profile = useProfileManagement();
  const dailyReport = useDailyReportManagement({ date });

  // 2. ページレベルの状態管理（最小限）
  // ※モーダル状態はLayer 2で管理
  const [activeView, setActiveView] = useState<'graph' | 'table'>('graph');

  // 3. 機能間の協調ロジック
  const handleMealUpdated = useCallback(async () => {
    // 食事が更新されたら栄養データも更新
    await nutrition.refetchDailySummary();
    // レポートも無効化
    await dailyReport.refetch();
  }, [nutrition, dailyReport]);

  // 4. ページ横断の計算（複数機能のデータを使う）
  const canGenerateReport = useMemo(() => {
    const required = profile.profile?.meals_per_day ?? 3;
    const completed = meals.mealItems.filter(m => m.meal_type === 'main').length;
    return completed >= required;
  }, [profile.profile, meals.mealItems]);

  // 5. ページ全体の集約状態
  const isLoading = nutrition.isLoading || meals.isLoading || profile.isLoading;
  const isError = nutrition.isError || meals.isError;

  // 6. 統合モデルを返す
  return {
    // 各機能モデル（Layer 4）
    nutrition,
    meals,
    profile,
    dailyReport,

    // ページレベル状態
    activeView,
    setActiveView,

    // ページレベル協調
    handleMealUpdated,
    canGenerateReport,

    // 集約状態
    isLoading,
    isError,
  };
}
```

#### ❌ このレイヤーがやってはいけないこと

```typescript
// ❌ モーダル状態管理（Layer 2の仕事）
const [isAddModalOpen, setIsAddModalOpen] = useState(false);

// ❌ 直接React Query使用（Layer 4に抽出）
const mealQuery = useQuery({
  queryKey: ['meals', date],
  queryFn: () => fetch(...),
});

// ❌ API呼び出し（Layer 5の仕事）
const data = await fetch('/api/meals');

// ❌ 複雑なキャッシュ管理（React Queryに任せる）
useEffect(() => {
  // 50行のキャッシュロジック... NG
}, [...]);

// ❌ UI固有のフィードバック（Layer 2の仕事）
toast.success('成功');
```

#### 💡 このレイヤーの特徴

- **できるだけ薄く**: 複雑なロジックはLayer 4へ
- **機能統合の接着剤**: Layer 4フックを組み合わせる
- **ページスコープ**: そのページでしか使わないロジック
- **機能間協調**: 食事更新→栄養再計算のような連携

---

### Layer 4: Feature Logic（機能ロジック層）

**「Reactの世界での機能実装」- React Queryの主戦場**

#### ✅ このレイヤーがやること

```typescript
// useMealManagement.ts - Layer 4

export function useMealManagement({ date }: Props): MealManagementModel {
  const queryClient = useQueryClient();

  // 1. Layer 5サービス注入
  const mealService = useMealService();

  // 2. React Queryでデータ取得
  const mealItemsQuery = useQuery({
    queryKey: ['meals', 'items', date],
    queryFn: () => mealService.getMealItemsByDate(date),
    staleTime: 1000 * 60 * 5,  // 5分間キャッシュ
  });

  // 3. Mutation定義
  const createMutation = useMutation({
    mutationFn: (data: MealItemRequest) =>
      mealService.createMealItem(data),
    onSuccess: () => {
      // 関連キャッシュの無効化
      queryClient.invalidateQueries({ queryKey: ['meals'] });
      queryClient.invalidateQueries({ queryKey: ['nutrition'] });
    },
  });

  // 4. データ整形（UIが使いやすい形に）
  const mealItems = useMemo(() => {
    return mealItemsQuery.data ?? [];
  }, [mealItemsQuery.data]);

  // 5. UIアクション提供
  const addMeal = useCallback(async (data: MealItemRequest) => {
    await createMutation.mutateAsync(data);
  }, [createMutation]);

  // 6. UIに最適化されたインターフェース
  return {
    // データ
    mealItems,

    // 状態
    isLoading: mealItemsQuery.isLoading,
    isError: mealItemsQuery.isError,

    // アクション
    addMeal,
    deleteMeal: deleteMutation.mutateAsync,
    updateMeal: updateMutation.mutateAsync,

    // 高度な操作用（Layer 3で使う）
    refetch: mealItemsQuery.refetch,
    mealItemsQuery,  // 内部Query露出
    createMutation,
  };
}
```

#### 複数ドメインの協調も可能

```typescript
// useTodayNutritionProgress.ts - 複数ドメインサービスを使う例

export function useTodayNutritionProgress({ date }: Props) {
  // 複数のLayer 5サービス利用
  const nutritionService = useNutritionService();
  const targetService = useTargetService();
  const nutritionProgressService = useNutritionProgressService();

  // Targetドメイン
  const targetQuery = useQuery({
    queryKey: ['targets', 'active'],
    queryFn: () => targetService.getActiveTarget(),
  });

  // Nutritionドメイン
  const summaryQuery = useQuery({
    queryKey: ['nutrition', 'daily-summary', date],
    queryFn: () => nutritionService.getDailySummary(date),
    enabled: targetQuery.isSuccess,
  });

  // 複数ドメインを統合した計算
  const progressData = useMemo(() => {
    return nutritionProgressService.calculateProgressData(
      targetQuery.data,
      summaryQuery.data
    );
  }, [targetQuery.data, summaryQuery.data, nutritionProgressService]);

  return {
    activeTarget: targetQuery.data,
    nutrientProgress: progressData.progress,
    dailySummaryData: progressData.summary,
    isLoading: targetQuery.isLoading || summaryQuery.isLoading,
    refetch: () => summaryQuery.refetch(),
  };
}
```

#### 💡 このレイヤーの特徴

- **React Query中心**: 非同期データ取得・キャッシュ管理
- **1機能 = 1フック**: `useMealManagement`, `useTargetManagement`
- **複数ページで再利用可能**: ページ非依存
- **複数ドメイン協調可**: Target + Nutrition等
- **UIに最適化されたデータ提供**: Layer 3/2が使いやすい形に

---

### Layer 5: Domain Services（ドメインサービス層）

**「純粋なビジネスルールとデータアクセス」- React非依存**

#### ✅ このレイヤーがやること

```typescript
// MealService.ts - Layer 5

/**
 * MealService - ドメインサービス
 *
 * React非依存の純粋なTypeScriptクラス
 */
export class MealService {
  // 1. API呼び出し
  async getMealItemsByDate(date: string): Promise<MealItem[]> {
    const response = await fetchMealItemsByDate(date);
    return this.normalizeMealItems(response);
  }

  async createMealItem(request: MealItemRequest): Promise<MealItem> {
    // 2. ドメインバリデーション
    this.validateMealRequest(request);

    // 3. API呼び出し
    return createMealItem(request);
  }

  // 4. データ正規化
  normalizeMealItems(rawData: any): MealItem[] {
    if (!rawData) return [];

    const items = rawData.items || rawData;
    if (!Array.isArray(items)) return [];

    return items
      .filter(this.isValidMealItem)
      .map(this.normalizeMealItem);
  }

  // 5. ドメイン固有ロジック
  findFirstMealForNutrition(mealItems: MealItem[]): MealIdentifier | null {
    // ビジネスルール: main食事を優先
    const mainMeals = mealItems.filter(item => item.meal_type === 'main');
    if (mainMeals.length > 0) {
      return {
        meal_type: mainMeals[0].meal_type,
        meal_index: mainMeals[0].meal_index ?? 1,
      };
    }

    // snackにフォールバック
    const snackMeals = mealItems.filter(item => item.meal_type === 'snack');
    if (snackMeals.length > 0) {
      return {
        meal_type: snackMeals[0].meal_type,
        meal_index: null,
      };
    }

    return null;
  }

  // 6. プライベートヘルパー
  private validateMealRequest(request: MealItemRequest): void {
    if (!request.name || typeof request.name !== 'string') {
      throw new Error('Meal name is required');
    }

    if (request.meal_type === 'main' && !request.meal_index) {
      throw new Error('Main meals must have a meal_index');
    }
  }

  private isValidMealItem(item: any): item is MealItem {
    return (
      item &&
      typeof item.id === 'string' &&
      typeof item.name === 'string' &&
      ['main', 'snack'].includes(item.meal_type)
    );
  }
}

// 7. React Hook形式で提供（DI）
export function useMealService(): MealService {
  return useMemo(() => new MealService(), []);
}

// 8. 非React環境用Factory
export function createMealService(): MealService {
  return new MealService();
}
```

#### ❌ このレイヤーがやってはいけないこと

```typescript
// ❌ React依存
import { useState, useQuery, useMemo } from 'react';

// ❌ React Queryの直接使用
export class MealService {
  useGetMeals() {  // NG! Serviceにuseは使わない
    return useQuery(...);
  }
}

// ❌ 他ドメインサービスへの直接依存
import { TargetService } from '@/modules/target/services';

class MealService {
  constructor(private targetService: TargetService) {}  // NG!
}

// ❌ UI状態の管理
class MealService {
  isModalOpen = false;  // NG!
}
```

#### 💡 このレイヤーの特徴

- **React非依存**: フレームワークが変わっても再利用可能
- **純粋なTypeScript**: クラスまたは関数
- **単一ドメイン責任**: 1サービス = 1ドメイン（Meal, Nutrition等）
- **テストしやすい**: Reactなしで単体テスト可能
- **DI提供**: `useMealService()` でLayer 4に注入

---

## 🎬 実例：ユーザーが「食事追加」した時の完全なフロー

```
【ユーザーアクション】
┌─────────────────────────────────────────┐
│ ユーザーが「+食事追加」ボタンをクリック     │
└─────────────────────────────────────────┘
              ↓

【Layer 1: UI Presentation】
┌─────────────────────────────────────────┐
│ MealListSection                         │
│   <Button onClick={props.onAddClick} /> │ ← propsで受け取ったonAddClickを呼ぶだけ
└─────────────────────────────────────────┘
              ↓ onAddClick('main', 1)

【Layer 2: UI Orchestration】
┌─────────────────────────────────────────┐
│ TodayPageContent                        │
│                                         │
│ const handleAddClick = (mealType, idx)=>│
│   addMealModal.open(mealType, idx);     │ ← モーダルを開く（UI状態変更）
│                                         │
│ <AddMealModal                           │
│   isOpen={addMealModal.isOpen}          │
│   onSubmit={handleAddModalSubmit} />    │
└─────────────────────────────────────────┘
              ↓ ユーザーがフォーム入力して「保存」クリック
              ↓ handleAddModalSubmit(values)

【Layer 2: UI Orchestration（続き）】
┌─────────────────────────────────────────┐
│ const handleAddModalSubmit = async (v)=>│
│   await m.meals.addMeal(v);             │ ← Layer 3のアクション呼び出し
│   addMealModal.close();                 │ ← モーダルを閉じる
│   toast.success('追加しました');         │ ← UIフィードバック
└─────────────────────────────────────────┘
              ↓ m.meals.addMeal(values)

【Layer 3: Page Aggregation】
┌─────────────────────────────────────────┐
│ useTodayPageModel                       │
│                                         │
│ const meals = useMealManagement({date}) │ ← Layer 4フック利用
│                                         │
│ return {                                │
│   meals,  // Layer 4のモデルをそのまま返す│
│   ...                                   │
│ }                                       │
└─────────────────────────────────────────┘
              ↓ meals.addMeal(values)

【Layer 4: Feature Logic】
┌─────────────────────────────────────────┐
│ useMealManagement                       │
│                                         │
│ const mealService = useMealService();   │ ← Layer 5注入
│                                         │
│ const createMutation = useMutation({    │
│   mutationFn: (data) =>                 │
│     mealService.createMealItem(data),   │ ← Layer 5呼び出し
│   onSuccess: () => {                    │
│     queryClient.invalidateQueries(...)  │ ← キャッシュ無効化
│   }                                     │
│ });                                     │
│                                         │
│ const addMeal = (data) =>               │
│   createMutation.mutateAsync(data);     │
└─────────────────────────────────────────┘
              ↓ mealService.createMealItem(data)

【Layer 5: Domain Services】
┌─────────────────────────────────────────┐
│ MealService                             │
│                                         │
│ async createMealItem(request) {         │
│   this.validateMealRequest(request);    │ ← ドメインバリデーション
│   return createMealItem(request);       │ ← API呼び出し
│ }                                       │
└─────────────────────────────────────────┘
              ↓ POST /api/meals

【外部API】
┌─────────────────────────────────────────┐
│ Backend API (FastAPI)                   │
│ POST /api/v1/meals                      │
└─────────────────────────────────────────┘
              ↓ 200 OK

【戻り（成功時）】
Layer 5 → Layer 4（キャッシュ無効化）
       → Layer 3（機能間協調: nutrition.refetch()）
       → Layer 2（モーダルclose、toast表示）
       → Layer 1（新データで再レンダリング）
```

---

## 📊 各レイヤーの比較表

| Layer | 状態管理 | React依存 | データ取得 | 再利用性 | 主な技術 |
|-------|---------|----------|-----------|---------|---------|
| **Layer 1** | ❌なし | ✅あり | ❌なし | ⭐⭐⭐⭐⭐ 最高 | JSX, props |
| **Layer 2** | ✅あり (UI状態) | ✅あり | ❌なし | ⭐⭐ 低い | useState, useCallback |
| **Layer 3** | ✅あり (最小限) | ✅あり | ❌なし | ⭐ ページ固有 | useMemo, useCallback |
| **Layer 4** | ✅あり (サーバー状態) | ✅あり | ✅あり | ⭐⭐⭐⭐ 高い | React Query, useMemo |
| **Layer 5** | ❌なし | ❌なし | ✅あり | ⭐⭐⭐⭐⭐ 最高 | Class, Function |

---

## 🎯 モーダル管理の位置づけ（重要）

```
モーダルの責務分離:

Layer 1 (AddMealModal.tsx)
  ↓ モーダルUIの表現のみ
  └─ isOpen, onClose, onSubmit等をpropsで受け取る

Layer 2 (useAddMealModalState.ts) ← モーダル状態管理の主戦場！
  ↓ モーダルの開閉状態管理
  ├─ isOpen, selectedMealType, selectedMealIndex等
  └─ open(), close() 関数

Layer 2 (TodayPageContent.tsx)
  ↓ モーダルとビジネスロジックの接続
  ├─ addMealModal = useAddMealModalState()
  └─ handleAddModalSubmit = () => { m.meals.addMeal(...); addMealModal.close(); }

Layer 3 (useTodayPageModel.ts)
  ↓ モーダル状態は持たない！
  └─ meals: useMealManagement() のみ提供

Layer 4 (useMealManagement.ts)
  ↓ ビジネスロジック
  └─ addMeal(), deleteMeal() 等のアクション提供
```

**重要ポイント**:
- モーダル状態は **Layer 2** で管理
- Layer 3にはモーダル状態を持ち込まない
- モーダル開閉とビジネスロジックは分離

---

## 🔑 レイヤー分離のチェックリスト

### Layer 1のチェック項目
- [ ] useState を使っていない
- [ ] useEffect を使っていない
- [ ] useQuery / useMutation を使っていない
- [ ] すべてのデータをpropsで受け取っている
- [ ] イベントハンドラーもpropsで受け取っている
- [ ] 他モジュールをimportしていない（共通UIコンポーネントは除く）

### Layer 2のチェック項目
- [ ] モーダル/タブ等のUI状態を管理している
- [ ] Layer 3からデータを受け取っている
- [ ] Layer 1にデータとイベントを渡している
- [ ] UIフィードバック（toast等）を実装している
- [ ] React Queryを直接使っていない

### Layer 3のチェック項目
- [ ] 複数のLayer 4フックを統合している
- [ ] ページ固有の協調ロジックを実装している
- [ ] モーダル状態を持っていない
- [ ] React Queryを直接使っていない（Layer 4に委譲）
- [ ] できるだけ薄く保たれている（100-200行程度）

### Layer 4のチェック項目
- [ ] React Queryでデータ取得・更新を管理している
- [ ] Layer 5サービスを呼び出している
- [ ] UIに最適化されたインターフェースを提供している
- [ ] 複数のページから再利用可能である
- [ ] モーダル状態を持っていない

### Layer 5のチェック項目
- [ ] Reactに依存していない（useXxxを使っていない）
- [ ] 純粋なTypeScriptクラスまたは関数である
- [ ] API呼び出しとデータ変換を実装している
- [ ] ドメインバリデーションを実装している
- [ ] 他ドメインサービスに直接依存していない

---

### アーキテクチャ全体像

データと依存関係の流れは**単方向**（上位から下位へ）です。

```
┌─────────────────────────────────────────┐
│ Layer 1: UI Presentation (UI表現)       │ ← 純粋な「見た目」
├─────────────────────────────────────────┤
│ Layer 2: UI Orchestration (UI協調)      │ ← UIの状態管理・つなぎ込み
├─────────────────────────────────────────┤
│ Layer 3: Page Aggregation (ページ集約)   │ ← ページ全体の司令塔
├─────────────────────────────────────────┤
│ Layer 4: Feature Logic (機能ロジック)    │ ← 特定機能のビジネスロジック・状態
├─────────────────────────────────────────┤
│ Layer 5: Domain Services (ドメイン)      │ ← 純粋な計算・API通信
└─────────────────────────────────────────┘

```

---

### 各レイヤーの詳細解説

#### 1. Layer 1: UI Presentation（UI表現層）

**「どう表示するか」に専念する層**

* **役割**: ユーザーへの画面表示のみを担当する「純粋なコンポーネント」。
* **特徴**:
* 状態（State）を持たず、親から受け取った `props` だけで描画が決まります。
* ビジネスロジックやAPI呼び出しを一切知りません。
* **Container/Presentationalパターン**における "Presentational" に相当します。


* **メリット**: ロジックがないため、Storybook等でのカタログ化や単体テストが極めて容易です。
* **実装例**: `NutrientProgressSection`, `AddMealModal` (UI部分のみ)

#### 2. Layer 2: UI Orchestration（UI協調層）

**「UIの振る舞い」を管理する層**

* **役割**: UIコンポーネント（Layer 1）を操作するための状態管理やイベントハンドリング。
* **特徴**:
* **モーダル管理の主戦場**です。
* 「モーダルが開いているか」「フォームに何が入力されているか」といった**UI固有の状態**を管理します。
* Layer 3からデータを受け取り、Layer 1に渡す「繋ぎ役」も果たします。


* **実装例**:
* `useAddMealModalState` (モーダルの開閉・入力値管理)
* `TodayPageContent` (コンポーネントの配置とイベントの接続)



#### 3. Layer 3: Page Aggregation（ページ集約層）

**「ページ全体の進行」を管理する司令塔**

* **役割**: 複数の機能（Layer 4）を束ね、ページとして成立させる層。
* **特徴**:
* ページ全体で必要なデータを各Featureフックから集めます。
* **機能間の連携**を担当します。（例：「食事を追加（Meal機能）」したら「栄養グラフ（Nutrition機能）を更新する」など）
* ページ固有の複雑な状態遷移を管理します。


* **実装例**: `useTodayPageModel`

#### 4. Layer 4: Feature Logic（機能ロジック層）

**「Reactの世界での機能実装」を担当する層**

* **役割**: 特定の機能（栄養管理、食事管理など）に必要なデータフェッチや加工を行う。
* **特徴**:
* React Query（TanStack Query）などのライブラリを使用し、非同期データのキャッシュや状態管理を行います。
* Layer 5のドメインサービスを呼び出し、UI（Layer 3/2）が使いやすい形にデータを整形して提供します。


* **実装例**: `useTodayNutritionProgress` (APIからデータを取得し、目標値と比較して進捗率を計算して返す)

#### 5. Layer 5: Domain Services（ドメインサービス層）

**「純粋なビジネスルールとデータアクセス」の層**

* **役割**: アプリケーションの核心となるロジックやAPI通信。
* **特徴**:
* **Reactに依存しません**（Hooksを使わない）。純粋なTypeScriptのクラスや関数です。
* APIのエンドポイントを叩く処理や、データの正規化、複雑なドメインルールの計算を行います。
* ここが独立しているため、フレームワークが変わってもロジックを再利用できます。


* **実装例**: `NutritionService`, `mealService`

---

### モーダルリファクタリングにおける適用例

ドキュメントにある「Add Meal Modal」を例にすると、以下のように責務が分散されます。

1. **Layer 5 (`mealService`)**: バックエンドAPIへデータをPOSTする通信処理。
2. **Layer 4 (`useMealManagement`)**: `mealService`を呼び出すReact QueryのMutation定義。成功時のキャッシュ無効化など。
3. **Layer 3 (`TodayPageContent`)**: 「保存ボタン」が押されたら Layer 4 の追加処理を呼び出し、成功したら Layer 2 のモーダルを閉じるよう指示する。
4. **Layer 2 (`useAddMealModalState`)**: `isOpen` (開閉状態) や `selectedMealType` (朝食/昼食などの選択状態) を管理する専用フック。
5. **Layer 1 (`AddMealModal`)**: `isOpen` や `onClose` を props として受け取り、単に表示するだけのコンポーネント。

### まとめ：なぜこの設計にするのか？

この5層構造の最大の利点は、**「変更に強い」**ことです。

* **UIデザインを変えたい時**: Layer 1 だけ修正すればOK。
* **APIの仕様が変わった時**: Layer 5 だけ修正すればOK。
* **モーダルの挙動を変えたい時**: Layer 2 だけ修正すればOK。

それぞれの層が独立しているため、影響範囲を局所化でき、大規模なアプリケーションでも安全に開発・運用を続けることが可能になります。