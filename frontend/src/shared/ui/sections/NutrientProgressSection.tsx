/**
 * NutrientProgressSection - 栄養素目標達成度表示コンポーネント
 *
 * 責務:
 * - 栄養素の目標達成度をカテゴリ別に表示
 * - 5つの状態（未設定/食事なし/ローディング/エラー/正常表示）の管理
 * - プログレスバーの色分け表示
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import type { Target } from '@/modules/target/contract/targetContract';
import type { NutrientProgress } from '@/modules/today/types/todayTypes';

// ========================================
// Types
// ========================================

interface NutrientProgressSectionProps {
  /** アクティブな目標設定 */
  activeTarget: Target | null;
  /** 栄養素進捗データ */
  nutrientProgress: NutrientProgress[];
  /** ローディング状態 */
  isLoading: boolean;
  /** エラー状態 */
  isError: boolean;
  /** 再試行コールバック */
  onRetry: () => void;
  /** 食事アイテム数（表示分岐用） */
  mealItemsCount: number;
}

// ========================================
// Constants
// ========================================

const NUTRIENT_CATEGORIES = {
  macronutrients: {
    title: '主要栄養素 (PFC)',
    icon: '🥩',
    nutrients: ['protein', 'fat', 'carbohydrate']
  },
  minerals: {
    title: 'ミネラル',
    icon: '💧',
    nutrients: ['sodium', 'potassium', 'iron', 'calcium']
  },
  vitamins_others: {
    title: 'ビタミン・その他',
    icon: '💊',
    nutrients: ['vitamin_d', 'water', 'fiber']
  }
} as const;

// ========================================
// Utility Functions
// ========================================

/**
 * プログレスバーの色を取得
 */
const getProgressBarColor = (percentage: number): string => {
  if (percentage > 100) return 'bg-red-500';
  if (percentage >= 80) return 'bg-green-500';
  return 'bg-blue-500';
};

// ========================================
// Sub Components
// ========================================

/**
 * 目標未設定状態
 */
function NoTargetState() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>目標達成度</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-sm text-muted-foreground">
          ターゲットを設定すると達成度が表示されます。
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * 食事なし状態
 */
function NoMealsState() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>目標達成度</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-sm text-muted-foreground">
          食事を追加すると達成度が表示されます。
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * ローディング状態
 */
function LoadingState() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>目標達成度</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-sm text-muted-foreground">計算中...</div>
      </CardContent>
    </Card>
  );
}

/**
 * エラー状態
 */
function ErrorState({ onRetry }: { onRetry: () => void }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>目標達成度</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-sm text-destructive">
          栄養データの取得に失敗しました。
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={onRetry}
          className="mt-2"
        >
          再試行
        </Button>
      </CardContent>
    </Card>
  );
}

/**
 * データなし状態
 */
function NoDataState() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>目標達成度</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-sm text-muted-foreground">
          栄養データを処理中です。しばらくお待ちください。
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * 栄養素進捗表示メインビュー
 */
function ProgressView({ nutrientProgress }: { nutrientProgress: NutrientProgress[] }) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>目標達成度</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-8">
            {Object.entries(NUTRIENT_CATEGORIES).map(([categoryKey, category]) => {
              const categoryNutrients = nutrientProgress.filter(np =>
                (category.nutrients as readonly string[]).includes(np.code)
              );

              if (categoryNutrients.length === 0) return null;

              return (
                <div key={categoryKey} className="mb-8 last:mb-0">
                  <div className="flex items-center gap-3 pb-3 mb-4 border-b-2 border-gray-200 dark:border-gray-600">
                    <div className="flex items-center justify-center w-8 h-8 rounded-full bg-gray-100 dark:bg-gray-700">
                      <span className="text-lg">{category.icon}</span>
                    </div>
                    <h3 className="text-base font-bold text-gray-800 dark:text-gray-200 uppercase tracking-wide">
                      {category.title}
                    </h3>
                  </div>

                  <div className="space-y-2">
                    {categoryNutrients.map((np) => (
                      <div key={np.code} className="grid grid-cols-[90px_1fr_110px] gap-4 items-center">
                        <div className="text-sm font-medium text-gray-900 dark:text-gray-300 truncate">
                          {np.label}
                        </div>

                        <div className="h-3 w-full bg-gray-200 dark:bg-gray-700 rounded-full">
                          <div
                            className={`h-3 rounded-full transition-all duration-300 ${getProgressBarColor(np.percentage)}`}
                            style={{ width: `${Math.min(np.percentage, 100)}%` }}
                          />
                        </div>

                        <div className="text-right">
                          <div className="text-sm font-bold text-gray-900 dark:text-white">
                            {np.percentage.toFixed(0)}%
                          </div>
                          <div className="text-xs text-gray-500 dark:text-gray-400 font-mono">
                            {np.actual.toFixed(1)}/{np.target.toFixed(1)}{np.unit}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// ========================================
// Main Component
// ========================================

/**
 * 栄養素目標達成度表示セクション
 *
 * TodayPageContentから抽出された巨大なJSXロジックを
 * 再利用可能なコンポーネントとして分離
 */
export function NutrientProgressSection({
  activeTarget,
  nutrientProgress,
  isLoading,
  isError,
  onRetry,
  mealItemsCount
}: NutrientProgressSectionProps) {
  // 状態別の表示分岐
  if (!activeTarget) {
    return <NoTargetState />;
  }

  if (mealItemsCount === 0) {
    return <NoMealsState />;
  }

  if (isLoading) {
    return <LoadingState />;
  }

  if (isError) {
    return <ErrorState onRetry={onRetry} />;
  }

  if (nutrientProgress.length === 0) {
    return <NoDataState />;
  }

  return <ProgressView nutrientProgress={nutrientProgress} />;
}