/**
 * nutritionTypes - 栄養関連の型定義
 *
 * 責務:
 * - 栄養データの型安全性確保
 * - 栄養詳細モーダル用のデータ構造定義
 * - APIレスポンスとの型整合性
 */

// ========================================
// Basic Nutrition Types
// ========================================

export interface NutrientValue {
  /** 栄養素コード (例: 'protein', 'carbohydrate', 'fat') */
  code: string;
  /** 栄養素の値 */
  value: number;
  /** 単位 (例: 'g', 'mg', 'kcal') */
  unit: string;
  /** 栄養素の名前 (表示用) */
  name?: string;
}

// ========================================
// Meal Nutrition Data
// ========================================

export interface MealNutritionData {
  /** 食事ID */
  id: string;
  /** 食事名 */
  name: string;
  /** 食事タイプ */
  meal_type: 'main' | 'snack';
  /** 食事インデックス */
  meal_index: number;
  /** 食事の総カロリー */
  totalCalories: number;
  /** 栄養素リスト */
  nutrients: NutrientValue[];
  /** 作成日時 */
  created_at?: string;
  /** 更新日時 */
  updated_at?: string;
}

// ========================================
// Daily Nutrition Data
// ========================================

export interface DailyNutritionData {
  /** 対象日 (YYYY-MM-DD) */
  date: string;
  /** 1日の総カロリー */
  totalCalories: number;
  /** 1日の栄養素合計 */
  nutrients: NutrientValue[];
  /** 食事数 */
  mealCount: number;
  /** PFC バランス情報 */
  pfcBalance?: {
    protein: { value: number; percentage: number };
    fat: { value: number; percentage: number };
    carbohydrate: { value: number; percentage: number };
  };
}

// ========================================
// Nutrition Details Modal Data
// ========================================

/**
 * 栄養詳細モーダルに渡されるデータ
 */
export interface NutritionDetailsData {
  /** 個別食事の栄養データ */
  meal: MealNutritionData;
  /** その日の栄養データ全体 */
  daily: DailyNutritionData;
  /** 表示設定 */
  display?: {
    /** タイトル表示名 */
    title?: string;
    /** 詳細表示するかどうか */
    showDetails?: boolean;
    /** グラフ表示するかどうか */
    showChart?: boolean;
  };
}

// ========================================
// Utility Types
// ========================================

/**
 * 栄養素コードの Union 型
 */
export type NutrientCode =
  | 'calories'
  | 'protein'
  | 'fat'
  | 'carbohydrate'
  | 'fiber'
  | 'sugar'
  | 'sodium'
  | 'calcium'
  | 'iron'
  | 'vitaminA'
  | 'vitaminC'
  | 'vitaminD';

/**
 * 栄養素の表示情報
 */
export interface NutrientDisplayInfo {
  code: NutrientCode;
  name: string;
  unit: string;
  category: 'macronutrient' | 'micronutrient' | 'mineral' | 'vitamin';
  dailyValue?: number; // 推奨日摂取量
}

// ========================================
// Type Guards
// ========================================

/**
 * NutritionDetailsData の型ガード
 */
export function isNutritionDetailsData(value: any): value is NutritionDetailsData {
  return (
    value &&
    typeof value === 'object' &&
    value.meal &&
    typeof value.meal === 'object' &&
    typeof value.meal.id === 'string' &&
    value.daily &&
    typeof value.daily === 'object' &&
    typeof value.daily.date === 'string'
  );
}

/**
 * MealNutritionData の型ガード
 */
export function isMealNutritionData(value: any): value is MealNutritionData {
  return (
    value &&
    typeof value === 'object' &&
    typeof value.id === 'string' &&
    typeof value.name === 'string' &&
    Array.isArray(value.nutrients)
  );
}

/**
 * DailyNutritionData の型ガード
 */
export function isDailyNutritionData(value: any): value is DailyNutritionData {
  return (
    value &&
    typeof value === 'object' &&
    typeof value.date === 'string' &&
    typeof value.totalCalories === 'number' &&
    Array.isArray(value.nutrients)
  );
}