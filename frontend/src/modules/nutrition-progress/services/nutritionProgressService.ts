/**
 * nutritionProgressService - 栄養進捗専用ドメインサービス
 *
 * 責務:
 * - Target + Nutrition データを統合した栄養進捗計算
 * - ドメイン境界を跨ぐビジネスロジック
 * - React非依存の純粋なTypeScript関数
 */

import type { Target, NutrientCode } from '@/modules/target/contract/targetContract';
import type { DailyNutritionSummary } from '@/modules/nutrition/contract/nutritionContract';
import type { NutrientProgress } from '@/modules/today/contract/todayContract';
import { nutrientLabels } from '@/modules/today/contract/todayContract';

// ========================================
// Domain Types
// ========================================

export interface NutritionProgressData {
  nutrientProgress: NutrientProgress[];
  dailySummaryData: DailySummaryData;
}

export interface DailySummaryData {
  currentCalories: number;
  targetCalories: number;
  protein: {
    current: number;
    target: number;
  };
  fat: {
    current: number;
    target: number;
  };
  carbohydrate: {
    current: number;
    target: number;
  };
}

// ========================================
// Domain Service Interface
// ========================================

export interface INutritionProgressService {
  /**
   * 栄養進捗データを計算
   */
  calculateProgressData(
    target: Target | null,
    nutritionSummary: DailyNutritionSummary | null
  ): NutritionProgressData;

  /**
   * Target有効性チェック
   */
  validateTargetForProgress(target: Target | null): boolean;

  /**
   * 栄養データ有効性チェック
   */
  validateNutritionSummary(summary: DailyNutritionSummary | null): boolean;
}

// ========================================
// Pure Functions (Business Logic)
// ========================================

/**
 * 栄養素進捗計算（純粋関数）
 */
function calculateNutrientProgress(
  target: Target,
  summary: DailyNutritionSummary | null
): NutrientProgress[] {
  if (!target?.nutrients) {
    return [];
  }

  return target.nutrients.map((targetNutrient: any) => {
    const actualNutrient = summary?.nutrients?.find(
      (n: any) => n.code === targetNutrient.code
    );
    const actualAmount = actualNutrient?.value ?? 0;
    const targetAmount = targetNutrient.amount ?? 0;
    const percentage = targetAmount > 0 ? (actualAmount / targetAmount) * 100 : 0;

    return {
      code: targetNutrient.code,
      label: nutrientLabels[targetNutrient.code as NutrientCode] || targetNutrient.code,
      target: targetAmount,
      actual: actualAmount,
      unit: targetNutrient.unit || 'g',
      percentage: Math.round(percentage * 100) / 100, // 小数点2桁
    };
  });
}

/**
 * ターゲットのみから目標値を計算（食事データがない場合）
 */
function calculateTargetOnlyData(target: Target): DailySummaryData {
  const proteinTarget = target.nutrients?.find((n: any) => n.code === 'protein');
  const fatTarget = target.nutrients?.find((n: any) => n.code === 'fat');
  const carbohydrateTarget = target.nutrients?.find((n: any) => n.code === 'carbohydrate');

  const targetCalories =
    ((proteinTarget?.amount ?? 0) * 4) +
    ((fatTarget?.amount ?? 0) * 9) +
    ((carbohydrateTarget?.amount ?? 0) * 4);

  return {
    currentCalories: 0,
    targetCalories: Math.round(targetCalories),
    protein: {
      current: 0,
      target: proteinTarget?.amount ?? 0,
    },
    fat: {
      current: 0,
      target: fatTarget?.amount ?? 0,
    },
    carbohydrate: {
      current: 0,
      target: carbohydrateTarget?.amount ?? 0,
    },
  };
}

/**
 * 日次サマリーデータ計算（純粋関数）
 */
function calculateDailySummaryData(
  target: Target,
  summary: DailyNutritionSummary
): DailySummaryData {
  const proteinTarget = target.nutrients?.find((n: any) => n.code === 'protein');
  const fatTarget = target.nutrients?.find((n: any) => n.code === 'fat');
  const carbohydrateTarget = target.nutrients?.find((n: any) => n.code === 'carbohydrate');

  const proteinActual = summary.nutrients?.find((n: any) => n.code === 'protein');
  const fatActual = summary.nutrients?.find((n: any) => n.code === 'fat');
  const carbohydrateActual = summary.nutrients?.find((n: any) => n.code === 'carbohydrate');

  const currentCalories =
    ((proteinActual?.value ?? 0) * 4) +
    ((fatActual?.value ?? 0) * 9) +
    ((carbohydrateActual?.value ?? 0) * 4);

  const targetCalories =
    ((proteinTarget?.amount ?? 0) * 4) +
    ((fatTarget?.amount ?? 0) * 9) +
    ((carbohydrateTarget?.amount ?? 0) * 4);

  return {
    currentCalories: Math.round(currentCalories),
    targetCalories: Math.round(targetCalories),
    protein: {
      current: proteinActual?.value ?? 0,
      target: proteinTarget?.amount ?? 0,
    },
    fat: {
      current: fatActual?.value ?? 0,
      target: fatTarget?.amount ?? 0,
    },
    carbohydrate: {
      current: carbohydrateActual?.value ?? 0,
      target: carbohydrateTarget?.amount ?? 0,
    },
  };
}

// ========================================
// Domain Service Implementation
// ========================================

export class NutritionProgressService implements INutritionProgressService {
  calculateProgressData(
    target: Target | null,
    nutritionSummary: DailyNutritionSummary | null
  ): NutritionProgressData {
    const defaultData: NutritionProgressData = {
      nutrientProgress: [],
      dailySummaryData: {
        currentCalories: 0,
        targetCalories: 0,
        protein: { current: 0, target: 0 },
        fat: { current: 0, target: 0 },
        carbohydrate: { current: 0, target: 0 },
      },
    };

    const targetValid = this.validateTargetForProgress(target);
    const summaryValid = this.validateNutritionSummary(nutritionSummary);

    if (!targetValid) {
      return defaultData;
    }

    // ターゲットは有効だが食事データがない場合
    // → 目標値は設定されているので、actual=0, percentage=0 で表示
    if (!summaryValid) {
      try {
        const targetOnlyData = calculateTargetOnlyData(target!);
        const nutrientProgress = calculateNutrientProgress(target!, null);
        return {
          nutrientProgress,
          dailySummaryData: targetOnlyData,
        };
      } catch (error) {
        console.error('目標値計算エラー:', error);
        return defaultData;
      }
    }

    try {
      return {
        nutrientProgress: calculateNutrientProgress(target!, nutritionSummary!),
        dailySummaryData: calculateDailySummaryData(target!, nutritionSummary!),
      };
    } catch (error) {
      console.error('栄養進捗計算エラー:', error);
      return defaultData;
    }
  }

  validateTargetForProgress(target: Target | null): boolean {
    if (!target) return false;
    if (!target.nutrients || target.nutrients.length === 0) return false;

    // 必要な栄養素（PFC）があるかチェック
    const requiredNutrients = ['protein', 'fat', 'carbohydrate'];
    const targetNutrientCodes = target.nutrients.map((n: any) => n.code);

    return requiredNutrients.some(required =>
      targetNutrientCodes.includes(required)
    );
  }

  validateNutritionSummary(summary: DailyNutritionSummary | null): boolean {
    if (!summary) return false;
    if (!summary.nutrients || summary.nutrients.length === 0) return false;

    // 基本的な栄養素データがあるかチェック
    return summary.nutrients.some((n: any) =>
      ['protein', 'fat', 'carbohydrate'].includes(n.code)
    );
  }
}

// ========================================
// Hook for Service
// ========================================

/**
 * React Hook形式でNutritionProgressServiceを取得
 */
export function useNutritionProgressService(): NutritionProgressService {
  return new NutritionProgressService();
}

// ========================================
// Exports
// ========================================

export default NutritionProgressService;