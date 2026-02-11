import { z } from 'zod';

export const GoalTypeSchema = z.enum([
  'weight_loss',
  'maintain',
  'weight_gain',
  'health_improve',
]);

export const ActivityLevelSchema = z.enum(['low', 'normal', 'high']);

export const NutrientCodeSchema = z.enum([
  'carbohydrate',
  'fat',
  'protein',
  'water',
  'fiber',
  'sodium',
  'iron',
  'calcium',
  'vitamin_d',
  'potassium',
]);

export const NutrientSourceSchema = z.enum([
  'llm',
  'manual',
  'user_input',
  'aggregated',
]);

export const TargetNutrientSchema = z.object({
  code: NutrientCodeSchema,
  amount: z.number(),
  unit: z.string(),
  source: NutrientSourceSchema,
});

export const TargetSchema = z.object({
  id: z.string(),
  user_id: z.string(),
  title: z.string(),
  goal_type: GoalTypeSchema,
  goal_description: z.string().nullable().optional(),
  activity_level: ActivityLevelSchema,
  is_active: z.boolean(),
  nutrients: z.array(TargetNutrientSchema),
  llm_rationale: z.string().nullable().optional(),
  disclaimer: z.string().nullable().optional(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const TargetListResponseSchema = z.object({
  items: z.array(TargetSchema),
});

export const CreateTargetRequestSchema = z.object({
  title: z.string(),
  goal_type: GoalTypeSchema,
  goal_description: z.string().nullable().optional(),
  activity_level: ActivityLevelSchema,
});

// ========================================
// Form Schema & Helpers
// ========================================

/**
 * ターゲット作成フォームスキーマ
 * バリデーションルール付き
 */
export const CreateTargetFormSchema = z.object({
  title: z.string().min(1, 'タイトルを入力してください'),
  goal_type: GoalTypeSchema,
  goal_description: z.string().optional(),
  activity_level: ActivityLevelSchema,
});

/**
 * 目標タイプのラベル
 */
export const goalTypeLabels: Record<z.infer<typeof GoalTypeSchema>, string> = {
  weight_loss: '減量',
  maintain: '維持',
  weight_gain: '増量',
  health_improve: '健康改善',
};

/**
 * 活動レベルのラベル
 */
export const activityLevelLabels: Record<z.infer<typeof ActivityLevelSchema>, string> = {
  low: '低い（デスクワーク中心）',
  normal: '普通（適度な運動）',
  high: '高い（激しい運動）',
};

/**
 * フォームのデフォルト値
 */
export const createTargetFormDefaultValues: z.infer<typeof CreateTargetFormSchema> = {
  title: '',
  goal_type: 'maintain',
  goal_description: '',
  activity_level: 'normal',
};

// ========================================
// Types
// ========================================

export type NutrientCode = z.infer<typeof NutrientCodeSchema>;
export type Target = z.infer<typeof TargetSchema>;
export type TargetListResponse = z.infer<typeof TargetListResponseSchema>;
export type CreateTargetRequest = z.infer<typeof CreateTargetRequestSchema>;
export type CreateTargetFormValues = z.infer<typeof CreateTargetFormSchema>;
