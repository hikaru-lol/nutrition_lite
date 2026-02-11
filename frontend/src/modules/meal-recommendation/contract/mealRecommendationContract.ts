import { z } from 'zod';

// =============================================================================
// スキーマ定義 (Zodを使用してバリデーションとTS型を同時に生成)
// =============================================================================

export const RecommendedMealSchema = z.object({
  title: z.string(),
  description: z.string(),
  ingredients: z.array(z.string()),
  nutrition_focus: z.string(),
});

export const MealRecommendationSchema = z.object({
  id: z.string(),
  user_id: z.string(),
  generated_for_date: z.string(), // YYYY-MM-DD
  body: z.string(),
  tips: z.array(z.string()),
  recommended_meals: z.array(RecommendedMealSchema),
  created_at: z.string(), // ISO datetime
});

export const GenerateMealRecommendationRequestSchema = z.object({
  date: z.string().optional(), // YYYY-MM-DD
});

export const GenerateMealRecommendationResponseSchema = z.object({
  recommendation: MealRecommendationSchema,
});

export const GetMealRecommendationResponseSchema = z.object({
  recommendation: MealRecommendationSchema,
});

export const ListMealRecommendationsResponseSchema = z.object({
  recommendations: z.array(MealRecommendationSchema),
});

// =============================================================================
// TypeScript型定義 (Zodスキーマから自動生成)
// =============================================================================

export type RecommendedMeal = z.infer<typeof RecommendedMealSchema>;
export type MealRecommendation = z.infer<typeof MealRecommendationSchema>;
export type GenerateMealRecommendationRequest = z.infer<typeof GenerateMealRecommendationRequestSchema>;
export type GenerateMealRecommendationResponse = z.infer<typeof GenerateMealRecommendationResponseSchema>;
export type GetMealRecommendationResponse = z.infer<typeof GetMealRecommendationResponseSchema>;
export type ListMealRecommendationsResponse = z.infer<typeof ListMealRecommendationsResponseSchema>;

// =============================================================================
// APIエラー型定義
// =============================================================================

export class MealRecommendationCooldownError extends Error {
  public readonly minutes: number;

  constructor(minutes: number) {
    super(`Please wait ${minutes} minutes before generating again`);
    this.name = 'MealRecommendationCooldownError';
    this.minutes = minutes;
  }
}

export class MealRecommendationDailyLimitError extends Error {
  public readonly currentCount: number;
  public readonly limit: number;

  constructor(currentCount: number, limit: number) {
    super(`Daily limit reached: ${currentCount}/${limit} recommendations per day`);
    this.name = 'MealRecommendationDailyLimitError';
    this.currentCount = currentCount;
    this.limit = limit;
  }
}

// =============================================================================
// ユーティリティ型
// =============================================================================

export type MealRecommendationStatus =
  | 'loading'
  | 'empty'
  | 'available'
  | 'rate-limited'
  | 'error';

export interface MealRecommendationCardState {
  status: MealRecommendationStatus;
  recommendation?: MealRecommendation;
  error?: Error;
  canGenerate: boolean;
  remainingGenerations?: number;
  nextGenerationTime?: Date;
}