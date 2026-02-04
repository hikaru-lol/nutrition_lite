/**
 * DailySummarySection - 日次サマリー表示セクション
 *
 * 責務:
 * - Context経由でのデータ取得
 * - 日次栄養サマリーの表示
 * - プロップスレスな実装
 */

'use client';

import { DailySummaryCard } from '@/shared/ui/cards/DailySummaryCard';
import { useTodayTargets } from '../../context/TodayPageContext';

// ========================================
// Component Interface
// ========================================

interface DailySummarySectionProps {
  className?: string;
}

// ========================================
// Main Component
// ========================================

export function DailySummarySection({ className }: DailySummarySectionProps = {}) {
  // Context経由でターゲット関連データを取得
  const targets = useTodayTargets();

  return (
    <div className={className} data-tour="daily-summary">
      <DailySummaryCard
        data={targets.dailySummaryData}
        isLoading={targets.isDailySummaryLoading}
      />
    </div>
  );
}

// ========================================
// 軽量版・特殊用途バリエーション
// ========================================

/**
 * カロリー情報のみの軽量サマリー
 */
export function CaloriesSummarySection({ className }: DailySummarySectionProps = {}) {
  const targets = useTodayTargets();

  if (targets.isDailySummaryLoading) {
    return (
      <div className={className}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-32 mb-2"></div>
          <div className="h-6 bg-gray-200 rounded w-24"></div>
        </div>
      </div>
    );
  }

  if (!targets.dailySummaryData) {
    return (
      <div className={className}>
        <div className="text-sm text-muted-foreground">
          カロリー情報なし
        </div>
      </div>
    );
  }

  const { currentCalories, targetCalories } = targets.dailySummaryData;

  return (
    <div className={className}>
      <div className="text-sm text-muted-foreground">カロリー</div>
      <div className="text-lg font-semibold">
        {currentCalories} / {targetCalories} kcal
      </div>
    </div>
  );
}

/**
 * PFC情報のみの軽量サマリー
 */
export function PFCSummarySection({ className }: DailySummarySectionProps = {}) {
  const targets = useTodayTargets();

  if (targets.isDailySummaryLoading) {
    return (
      <div className={className}>
        <div className="animate-pulse space-y-2">
          {[1, 2, 3].map(i => (
            <div key={i} className="flex justify-between">
              <div className="h-3 bg-gray-200 rounded w-16"></div>
              <div className="h-3 bg-gray-200 rounded w-12"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!targets.dailySummaryData) {
    return (
      <div className={className}>
        <div className="text-sm text-muted-foreground">
          PFC情報なし
        </div>
      </div>
    );
  }

  const { protein, fat, carbohydrate } = targets.dailySummaryData;

  return (
    <div className={className}>
      <div className="space-y-1 text-xs">
        <div className="flex justify-between">
          <span>P (タンパク質)</span>
          <span>{protein.current.toFixed(1)}g / {protein.target.toFixed(1)}g</span>
        </div>
        <div className="flex justify-between">
          <span>F (脂質)</span>
          <span>{fat.current.toFixed(1)}g / {fat.target.toFixed(1)}g</span>
        </div>
        <div className="flex justify-between">
          <span>C (炭水化物)</span>
          <span>{carbohydrate.current.toFixed(1)}g / {carbohydrate.target.toFixed(1)}g</span>
        </div>
      </div>
    </div>
  );
}

// ========================================
// プレビュー・デバッグ用コンポーネント
// ========================================

/**
 * サマリーデータのプレビュー表示（開発用）
 */
export function DailySummaryPreview() {
  const targets = useTodayTargets();

  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  return (
    <details className="p-4 border rounded-lg">
      <summary className="cursor-pointer font-medium">
        Daily Summary Debug Info
      </summary>
      <div className="mt-2 space-y-2 text-xs">
        <div>
          <strong>Loading:</strong> {targets.isDailySummaryLoading.toString()}
        </div>
        <div>
          <strong>Error:</strong> {targets.isDailySummaryError.toString()}
        </div>
        <div>
          <strong>Data:</strong>
          {targets.dailySummaryData ? (
            <pre className="mt-1 p-2 bg-gray-100 rounded">
              {JSON.stringify(targets.dailySummaryData, null, 2)}
            </pre>
          ) : (
            ' null'
          )}
        </div>
        <div>
          <strong>Progress Items:</strong> {targets.nutrientProgress.length}
        </div>
      </div>
    </details>
  );
}