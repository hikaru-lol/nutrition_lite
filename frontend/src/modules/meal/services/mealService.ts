/**
 * mealService - Layer 5: Domain Services
 *
 * 責務:
 * - 純粋な食事API操作
 * - 食事ドメインのデータ変換・正規化
 * - 食事ドメイン固有のバリデーション
 */

import { fetchMealItemsByDate, createMealItem, updateMealItem, deleteMealItem } from '../api/mealClient';
import type { MealItem, MealItemRequest, MealItemResponse } from '../contract/mealContract';

// ========================================
// Service Types
// ========================================

/**
 * 食事識別子（栄養分析用）
 */
export interface MealIdentifier {
  meal_type: 'main' | 'snack';
  meal_index: number | null;
}

/**
 * 食事セクション情報
 */
export interface MealSection {
  mealType: 'main' | 'snack';
  mealIndex?: number;
}

/**
 * 食事バリデーション結果
 */
export interface MealValidationResult {
  isValid: boolean;
  errors: string[];
}

// ========================================
// Service Interface
// ========================================

export interface IMealService {
  /**
   * 指定日の食事アイテム一覧を取得
   */
  getMealItemsByDate(date: string): Promise<MealItem[]>;

  /**
   * 食事アイテムを作成
   */
  createMealItem(request: MealItemRequest): Promise<MealItem>;

  /**
   * 食事アイテムを更新
   */
  updateMealItem(entryId: string, data: MealItemRequest): Promise<MealItem>;

  /**
   * 食事アイテムを削除
   */
  deleteMealItem(entryId: string): Promise<void>;

  /**
   * 食事データを正規化
   */
  normalizeMealItems(rawData: any): MealItem[];

  /**
   * 栄養分析用の最初の食事を見つける
   */
  findFirstMealForNutrition(mealItems: MealItem[]): MealIdentifier | null;

  /**
   * 食事セクションを抽出
   */
  getMealSections(mealItems: MealItem[]): MealSection[];

  /**
   * 食事データのバリデーション
   */
  validateMealItems(mealItems: MealItem[]): MealValidationResult;
}

// ========================================
// Service Implementation
// ========================================

export class MealService implements IMealService {
  async getMealItemsByDate(date: string): Promise<MealItem[]> {
    try {
      const response = await fetchMealItemsByDate(date);
      return this.normalizeMealItems(response);
    } catch (error) {
      console.error('Failed to fetch meal items:', error);
      return [];
    }
  }

  async createMealItem(request: MealItemRequest): Promise<MealItem> {
    this.validateMealRequest(request);
    return createMealItem(request);
  }

  async updateMealItem(entryId: string, data: MealItemRequest): Promise<MealItem> {
    if (!entryId || typeof entryId !== 'string') {
      throw new Error('Invalid entry ID provided');
    }

    this.validateMealRequest(data);
    return updateMealItem(entryId, data);
  }

  async deleteMealItem(entryId: string): Promise<void> {
    if (!entryId || typeof entryId !== 'string') {
      throw new Error('Invalid entry ID provided');
    }

    return deleteMealItem(entryId);
  }

  normalizeMealItems(rawData: any): MealItem[] {
    if (!rawData) return [];

    // レスポンス形式に応じて正規化
    const items = rawData.items || rawData;

    if (!Array.isArray(items)) return [];

    return items.filter(this.isValidMealItem).map(this.normalizeMealItem);
  }

  findFirstMealForNutrition(mealItems: MealItem[]): MealIdentifier | null {
    if (!mealItems || mealItems.length === 0) {
      return null;
    }

    // main食事を優先、なければsnackを使用
    const mainMeals = mealItems.filter(item => item.meal_type === 'main');
    if (mainMeals.length > 0) {
      return {
        meal_type: mainMeals[0].meal_type,
        meal_index: mainMeals[0].meal_index ?? 1,
      };
    }

    const snackMeals = mealItems.filter(item => item.meal_type === 'snack');
    if (snackMeals.length > 0) {
      return {
        meal_type: snackMeals[0].meal_type,
        meal_index: null,
      };
    }

    return null;
  }

  getMealSections(mealItems: MealItem[]): MealSection[] {
    const sections = new Set<string>();
    const result: MealSection[] = [];

    mealItems.forEach(item => {
      const key = item.meal_type === 'main'
        ? `${item.meal_type}-${item.meal_index}`
        : item.meal_type;

      if (!sections.has(key)) {
        sections.add(key);
        result.push({
          mealType: item.meal_type,
          mealIndex: item.meal_type === 'main' ? (item.meal_index ?? undefined) : undefined
        });
      }
    });

    return result;
  }

  validateMealItems(mealItems: MealItem[]): MealValidationResult {
    const errors: string[] = [];

    if (!Array.isArray(mealItems)) {
      errors.push('mealItems must be an array');
      return { isValid: false, errors };
    }

    mealItems.forEach((item, index) => {
      if (!this.isValidMealItem(item)) {
        errors.push(`Invalid meal item at index ${index}`);
      }
    });

    return { isValid: errors.length === 0, errors };
  }

  // ========================================
  // Private Helper Methods
  // ========================================

  private isValidMealItem(item: any): item is MealItem {
    return (
      item &&
      typeof item.id === 'string' &&
      typeof item.name === 'string' &&
      ['main', 'snack'].includes(item.meal_type)
    );
  }

  private normalizeMealItem(item: any): MealItem {
    return {
      id: item.id,
      name: item.name,
      meal_type: item.meal_type,
      meal_index: item.meal_index || null,
      serving_count: item.serving_count || null,
      note: item.note || null,
      date: item.date,
      created_at: item.created_at,
      updated_at: item.updated_at,
    };
  }

  private validateMealRequest(request: MealItemRequest): void {
    if (!request.name || typeof request.name !== 'string') {
      throw new Error('Meal name is required and must be a string');
    }

    if (!['main', 'snack'].includes(request.meal_type)) {
      throw new Error('Meal type must be "main" or "snack"');
    }

    if (request.meal_type === 'main' && !request.meal_index) {
      throw new Error('Main meals must have a meal_index');
    }
  }
}

// ========================================
// Service Factory & Hook
// ========================================

/**
 * React Hook形式でMealServiceを取得
 */
export function useMealService(): MealService {
  return new MealService();
}

/**
 * 関数形式でMealServiceを取得（非React環境用）
 */
export function createMealService(): MealService {
  return new MealService();
}

// ========================================
// Exports
// ========================================

export default MealService;