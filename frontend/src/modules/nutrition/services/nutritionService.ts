/**
 * nutritionService - 栄養関連のビジネスロジックとAPI処理
 *
 * 責務:
 * - 栄養データ取得のAPI呼び出し
 * - 栄養進捗の計算ロジック
 * - 日次サマリーの処理
 */

import { getNutritionData, computeNutritionData } from '../api/nutritionClient';
import type { DailyNutritionSummary } from '../contract/nutritionContract';

// ========================================
// Service Types
// ========================================

export interface MealInfo {
  meal_type: 'main' | 'snack';
  meal_index: number | null;
}


// ========================================
// Service Interface
// ========================================

export interface INutritionService {
  /**
   * 日次栄養サマリーを取得
   */
  getDailySummary(date: string, firstMeal: MealInfo): Promise<DailyNutritionSummary>;


  /**
   * 食事セクション毎の栄養データを取得
   */
  fetchMealNutrition(date: string, mealType: 'main' | 'snack', mealIndex?: number): Promise<any>;
}

// ========================================
// Service Implementation
// ========================================

export class NutritionService implements INutritionService {
  async getDailySummary(date: string, firstMeal: MealInfo): Promise<DailyNutritionSummary> {
    if (!firstMeal) {
      throw new Error('No meals found for nutrition summary');
    }

    const nutritionData = await getNutritionData({
      date,
      meal_type: firstMeal.meal_type,
      meal_index: firstMeal.meal_index,
    });

    if (!nutritionData?.daily) {
      throw new Error('Daily nutrition data not found');
    }

    return nutritionData.daily;
  }


  async fetchMealNutrition(date: string, mealType: 'main' | 'snack', mealIndex?: number): Promise<any> {
    return computeNutritionData({
      date,
      meal_type: mealType,
      meal_index: mealIndex ?? null,
    });
  }

  /**
   * 栄養データの妥当性をチェック
   */
  validateNutritionData(summary: DailyNutritionSummary | null): boolean {
    if (!summary) return false;
    if (!summary.nutrients || summary.nutrients.length === 0) return false;

    // 最低限のPFC栄養素があるかチェック
    const requiredNutrients = ['protein', 'fat', 'carbohydrate'] as const;
    const summaryNutrientCodes = summary.nutrients.map(n => n.code);

    return requiredNutrients.every(required =>
      summaryNutrientCodes.includes(required as any)
    );
  }
}

// ========================================
// Service Factory
// ========================================

/**
 * NutritionServiceのシングルトンインスタンス作成
 */
let nutritionServiceInstance: NutritionService | null = null;

export function getNutritionService(): NutritionService {
  if (!nutritionServiceInstance) {
    nutritionServiceInstance = new NutritionService();
  }
  return nutritionServiceInstance;
}

// ========================================
// Hook for Service
// ========================================

/**
 * React Hook形式でNutritionServiceを取得
 */
export function useNutritionService(): NutritionService {
  return getNutritionService();
}

// ========================================
// Exports
// ========================================

export default NutritionService;
// export { NutritionService };