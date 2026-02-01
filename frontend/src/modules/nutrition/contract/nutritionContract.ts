import { z } from 'zod';
import {
  NutrientCodeSchema,
  NutrientSourceSchema,
} from '@/modules/target/contract/targetContract';
import { MealTypeSchema } from '@/modules/meal/contract/mealContract';

// Re-export for convenience
export { NutrientCodeSchema, NutrientSourceSchema };

/**
 * NutritionNutrientIntake: 個別の栄養素摂取量
 */
export const NutritionNutrientIntakeSchema = z.object({
  code: NutrientCodeSchema,
  value: z.number(), // バックエンドに合わせて value に変更
  unit: z.string(),
  source: NutrientSourceSchema,
});

/**
 * MealNutritionSummary: 食事単位の栄養サマリー
 */
export const MealNutritionSummarySchema = z.object({
  id: z.string(),
  date: z.string(),
  meal_type: MealTypeSchema,
  meal_index: z.number().int().nullable().optional(),
  generated_at: z.string(),
  nutrients: z.array(NutritionNutrientIntakeSchema),
});

/**
 * DailyNutritionSummary: 1日単位の栄養サマリー
 */
export const DailyNutritionSummarySchema = z.object({
  id: z.string(),
  date: z.string(),
  generated_at: z.string(),
  nutrients: z.array(NutritionNutrientIntakeSchema),
});

/**
 * MealAndDailyNutritionResponse: /nutrition/meal のレスポンス
 */
export const MealAndDailyNutritionResponseSchema = z.object({
  meal: MealNutritionSummarySchema,
  daily: DailyNutritionSummarySchema,
});

/**
 * DailyNutritionReportResponse: /nutrition/daily/report のレスポンス
 */
export const DailyNutritionReportResponseSchema = z.object({
  date: z.string(),
  summary: z.string(),
  good_points: z.array(z.string()),
  improvement_points: z.array(z.string()),
  tomorrow_focus: z.array(z.string()),
  created_at: z.string(),
});

/**
 * GenerateDailyReportRequest: POST /nutrition/daily/report のリクエスト
 */
export const GenerateDailyReportRequestSchema = z.object({
  date: z.string(),
});

// Type exports
export type NutritionNutrientIntake = z.infer<
  typeof NutritionNutrientIntakeSchema
>;
export type MealNutritionSummary = z.infer<typeof MealNutritionSummarySchema>;
export type DailyNutritionSummary = z.infer<typeof DailyNutritionSummarySchema>;
export type MealAndDailyNutritionResponse = z.infer<
  typeof MealAndDailyNutritionResponseSchema
>;
export type DailyNutritionReport = z.infer<
  typeof DailyNutritionReportResponseSchema
>;
export type GenerateDailyReportRequest = z.infer<
  typeof GenerateDailyReportRequestSchema
>;
