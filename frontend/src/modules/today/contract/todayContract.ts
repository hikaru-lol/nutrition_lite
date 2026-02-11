/**
 * todayContract.ts - Today Module 型定義とスキーマ
 *
 * 責務:
 * - Todayページで使用する型定義
 * - フォームスキーマ
 * - ユーティリティ関数
 */

import { z } from 'zod';
import { MealItemRequestSchema } from '@/modules/meal/contract/mealContract';
import type { NutrientCode } from '@/modules/target/contract/targetContract';

// ========================================
// Form関連
// ========================================

export const TodayMealItemFormSchema = MealItemRequestSchema.extend({
  meal_index: z.number().int().min(1).nullable().optional(),
});

export type TodayMealItemFormValues = z.infer<typeof TodayMealItemFormSchema>;

// ========================================
// 栄養進捗
// ========================================

export type NutrientProgress = {
  code: NutrientCode;
  label: string;
  target: number;
  actual: number;
  unit: string;
  percentage: number;
};

// 栄養素コード → 日本語ラベル
export const nutrientLabels: Record<NutrientCode, string> = {
  carbohydrate: '炭水化物',
  fat: '脂質',
  protein: 'たんぱく質',
  water: '水分',
  sodium: 'ナトリウム',
  potassium: 'カリウム',
  calcium: 'カルシウム',
  iron: '鉄',
  vitamin_d: 'ビタミンD',
  fiber: '食物繊維',
};

// ========================================
// ユーティリティ関数
// ========================================

/**
 * DateオブジェクトをYYYY-MM-DD形式の文字列に変換
 */
export function formatLocalDateYYYYMMDD(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}
