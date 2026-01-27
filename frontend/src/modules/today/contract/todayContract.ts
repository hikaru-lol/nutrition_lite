import { z } from 'zod';

export const DateISOSchema = z
  .string()
  .regex(/^\d{4}-\d{2}-\d{2}$/, 'YYYY-MM-DD 形式で入力してください');

// OpenAPI: MealType
export const MealTypeSchema = z.enum(['main', 'snack']);

// OpenAPI: NutrientCode
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

// OpenAPI: NutrientSource
export const NutrientSourceSchema = z.enum([
  'llm',
  'manual',
  'user_input',
  'aggregated',
]);

// OpenAPI: TargetNutrient
export const TargetNutrientSchema = z.object({
  code: NutrientCodeSchema,
  amount: z.number(),
  unit: z.string(),
  source: NutrientSourceSchema,
});

// OpenAPI: GoalType
export const GoalTypeSchema = z.enum([
  'weight_loss',
  'maintain',
  'weight_gain',
  'health_improve',
]);

// OpenAPI: ActivityLevel
export const ActivityLevelSchema = z.enum(['low', 'normal', 'high']);

// OpenAPI: MealItemResponse
export const MealItemSchema = z.object({
  id: z.string().uuid(),
  date: DateISOSchema,
  meal_type: MealTypeSchema,
  meal_index: z.number().int().nullable(),
  name: z.string(),
  amount_value: z.number().nullable().optional(),
  amount_unit: z.string().nullable().optional(),
  serving_count: z.number().nullable().optional(),
  note: z.string().nullable().optional(),
});

// OpenAPI: TargetResponse (subset for TodaySummary)
export const ActiveTargetSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),
  title: z.string(),
  goal_type: GoalTypeSchema,
  goal_description: z.string().nullable().optional(),
  activity_level: ActivityLevelSchema,
  is_active: z.boolean(),
  nutrients: z.array(TargetNutrientSchema),
  llm_rationale: z.string().nullable().optional(),
  disclaimer: z.string().nullable().optional(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

// BFF集約型: TodaySummary (※OpenAPIに /today エンドポイント追加時に同期要)
export const TodaySummarySchema = z.object({
  date: DateISOSchema,
  active_target: ActiveTargetSchema.nullable().optional(),
  meals: z.array(MealItemSchema),
});

export type TodaySummary = z.infer<typeof TodaySummarySchema>;
export type MealItem = z.infer<typeof MealItemSchema>;
export type MealType = z.infer<typeof MealTypeSchema>;
export type TargetNutrient = z.infer<typeof TargetNutrientSchema>;
export type ActiveTarget = z.infer<typeof ActiveTargetSchema>;
