/**
 * TargetProgressSection - 目標進捗表示セクション
 *
 * 責務:
 * - Context経由での目標・進捗データ取得
 * - 栄養素進捗の視覚化
 * - プロップスレスな実装
 */

'use client';

import { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { useTodayTargets } from '../../context/TodayPageContext';

// ========================================
// Component Interface
// ========================================

interface TargetProgressSectionProps {
  className?: string;
}

// ========================================
// Main Component
// ========================================

export function TargetProgressSection({ className }: TargetProgressSectionProps = {}) {
  // Context経由で目標関連データを取得
  const targets = useTodayTargets();

  // ========================================
  // Data Processing
  // ========================================

  // 主要栄養素（PFC）の抽出
  const primaryNutrients = useMemo(() => {
    return targets.nutrientProgress.filter(nutrient =>
      ['protein', 'fat', 'carbohydrate'].includes(nutrient.code)
    );
  }, [targets.nutrientProgress]);

  // その他栄養素の抽出
  const otherNutrients = useMemo(() => {
    return targets.nutrientProgress.filter(nutrient =>
      !['protein', 'fat', 'carbohydrate'].includes(nutrient.code)
    );
  }, [targets.nutrientProgress]);

  // ========================================
  // Loading State
  // ========================================

  if (targets.isLoading) {
    return (
      <div className={className}>
        <Card>
          <CardHeader>
            <div className="animate-pulse">
              <div className="h-5 bg-gray-200 rounded w-32 mb-2"></div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="animate-pulse space-y-4">
              {[1, 2, 3].map(i => (
                <div key={i}>
                  <div className="flex justify-between mb-2">
                    <div className="h-4 bg-gray-200 rounded w-20"></div>
                    <div className="h-4 bg-gray-200 rounded w-16"></div>
                  </div>
                  <div className="h-2 bg-gray-200 rounded"></div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // ========================================
  // Error State
  // ========================================

  if (targets.isError || !targets.activeTarget) {
    return (
      <div className={className}>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center text-muted-foreground">
              <p className="mb-2">目標が設定されていません</p>
              <p className="text-sm">栄養目標を設定してください</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // ========================================
  // Render
  // ========================================

  return (
    <div className={className} data-tour="target-progress">
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">目標進捗</CardTitle>
          <p className="text-sm text-muted-foreground">
            {targets.activeTarget.title}
          </p>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* 主要栄養素（PFC）*/}
          {primaryNutrients.length > 0 && (
            <div>
              <h4 className="text-sm font-medium mb-3 text-gray-700">
                主要栄養素
              </h4>
              <div className="space-y-3">
                {primaryNutrients.map((nutrient) => (
                  <NutrientProgressItem
                    key={nutrient.code}
                    nutrient={nutrient}
                    variant="primary"
                  />
                ))}
              </div>
            </div>
          )}

          {/* その他栄養素 */}
          {otherNutrients.length > 0 && (
            <div>
              <h4 className="text-sm font-medium mb-3 text-gray-700">
                その他栄養素
              </h4>
              <div className="space-y-3">
                {otherNutrients.map((nutrient) => (
                  <NutrientProgressItem
                    key={nutrient.code}
                    nutrient={nutrient}
                    variant="secondary"
                  />
                ))}
              </div>
            </div>
          )}

          {/* 進捗なしの場合 */}
          {targets.nutrientProgress.length === 0 && (
            <div className="text-center text-muted-foreground py-4">
              <p className="text-sm">まだ栄養データがありません</p>
              <p className="text-xs">食事を記録すると進捗が表示されます</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// ========================================
// Helper Components
// ========================================

interface NutrientProgressItemProps {
  nutrient: {
    code: string;
    label: string;
    target: number;
    actual: number;
    unit: string;
    percentage: number;
  };
  variant?: 'primary' | 'secondary';
}

function NutrientProgressItem({
  nutrient,
  variant = 'secondary'
}: NutrientProgressItemProps) {
  // 達成状況による色分け
  const getProgressColor = (percentage: number) => {
    if (percentage >= 100) return 'text-green-600';
    if (percentage >= 80) return 'text-blue-600';
    if (percentage >= 50) return 'text-yellow-600';
    return 'text-gray-600';
  };

  // プライマリ栄養素は少し強調
  const progressSize = variant === 'primary' ? 'h-3' : 'h-2';
  const labelSize = variant === 'primary' ? 'text-sm font-medium' : 'text-sm';

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <span className={labelSize}>{nutrient.label}</span>
        <div className={`text-sm tabular-nums ${getProgressColor(nutrient.percentage)}`}>
          <span className="font-medium">
            {nutrient.actual.toFixed(1)}
          </span>
          <span className="text-muted-foreground">
            /{nutrient.target.toFixed(1)} {nutrient.unit}
          </span>
          <span className="ml-1 text-xs">
            ({Math.min(nutrient.percentage, 999).toFixed(0)}%)
          </span>
        </div>
      </div>
      <Progress
        value={Math.min(nutrient.percentage, 100)}
        className={`w-full ${progressSize}`}
      />
    </div>
  );
}

// ========================================
// 軽量版・特殊用途バリエーション
// ========================================

/**
 * PFC進捗のみの軽量版
 */
export function PFCProgressSection({ className }: TargetProgressSectionProps = {}) {
  const targets = useTodayTargets();

  const pfcNutrients = useMemo(() => {
    return targets.nutrientProgress.filter(nutrient =>
      ['protein', 'fat', 'carbohydrate'].includes(nutrient.code)
    );
  }, [targets.nutrientProgress]);

  if (targets.isLoading) {
    return (
      <div className={className}>
        <div className="animate-pulse space-y-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="flex justify-between items-center">
              <div className="h-3 bg-gray-200 rounded w-16"></div>
              <div className="h-3 bg-gray-200 rounded w-20"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (pfcNutrients.length === 0) {
    return (
      <div className={className}>
        <div className="text-sm text-muted-foreground text-center py-2">
          PFC情報なし
        </div>
      </div>
    );
  }

  return (
    <div className={className}>
      <div className="space-y-2">
        <h4 className="text-sm font-medium">PFC進捗</h4>
        <div className="space-y-2">
          {pfcNutrients.map((nutrient) => (
            <div key={nutrient.code} className="flex justify-between text-xs">
              <span>{nutrient.label.charAt(0)}</span>
              <span className="tabular-nums">
                {nutrient.actual.toFixed(1)}/{nutrient.target.toFixed(1)}
                <span className="text-muted-foreground ml-1">
                  ({Math.min(nutrient.percentage, 999).toFixed(0)}%)
                </span>
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/**
 * 目標達成度の概要表示
 */
export function TargetAchievementSection({ className }: TargetProgressSectionProps = {}) {
  const targets = useTodayTargets();

  const achievementStats = useMemo(() => {
    if (targets.nutrientProgress.length === 0) {
      return { achieved: 0, total: 0, averageProgress: 0 };
    }

    const achieved = targets.nutrientProgress.filter(n => n.percentage >= 100).length;
    const total = targets.nutrientProgress.length;
    const averageProgress = targets.nutrientProgress.reduce(
      (sum, n) => sum + n.percentage,
      0
    ) / total;

    return { achieved, total, averageProgress };
  }, [targets.nutrientProgress]);

  if (targets.isLoading) {
    return (
      <div className={className}>
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-32 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-48"></div>
        </div>
      </div>
    );
  }

  return (
    <div className={className}>
      <div className="text-center">
        <div className="text-lg font-semibold">
          {achievementStats.achieved} / {achievementStats.total}
        </div>
        <div className="text-sm text-muted-foreground">
          目標達成 ({achievementStats.averageProgress.toFixed(0)}% 平均進捗)
        </div>
      </div>
    </div>
  );
}

// ========================================
// プレビュー・デバッグ用コンポーネント
// ========================================

/**
 * 目標進捗データのプレビュー表示（開発用）
 */
export function TargetProgressPreview() {
  const targets = useTodayTargets();

  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  return (
    <details className="p-4 border rounded-lg">
      <summary className="cursor-pointer font-medium">
        Target Progress Debug Info
      </summary>
      <div className="mt-2 space-y-2 text-xs">
        <div>
          <strong>Active Target:</strong> {targets.activeTarget?.title ?? 'なし'}
        </div>
        <div>
          <strong>Loading:</strong> {targets.isLoading.toString()}
        </div>
        <div>
          <strong>Error:</strong> {targets.isError.toString()}
        </div>
        <div>
          <strong>Nutrient Progress Count:</strong> {targets.nutrientProgress.length}
        </div>
        <div>
          <strong>Progress Data:</strong>
          {targets.nutrientProgress.length > 0 ? (
            <pre className="mt-1 p-2 bg-gray-100 rounded max-h-40 overflow-auto">
              {JSON.stringify(targets.nutrientProgress, null, 2)}
            </pre>
          ) : (
            ' []'
          )}
        </div>
      </div>
    </details>
  );
}