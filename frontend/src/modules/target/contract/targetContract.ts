import { z } from 'zod';

// ============================================================
// OpenAPI: GoalType, ActivityLevel
// ============================================================
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

// ============================================================
// OpenAPI: CreateTargetRequest
// ============================================================
export const CreateTargetRequestSchema = z.object({
  title: z.string().min(1),
  goal_type: GoalTypeSchema,
  goal_description: z.string().nullable().optional(),
  activity_level: ActivityLevelSchema,
});

// ============================================================
// OpenAPI: TargetNutrient
// ============================================================
export const TargetNutrientSchema = z.object({
  code: NutrientCodeSchema,
  amount: z.number(),
  unit: z.string(),
  source: NutrientSourceSchema,
});

// ============================================================
// OpenAPI: TargetResponse
// ============================================================
export const TargetResponseSchema = z.object({
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

// ============================================================
// OpenAPI: TargetListResponse
// ============================================================
export const TargetListResponseSchema = z.object({
  items: z.array(TargetResponseSchema),
});

// ============================================================
// Types
// ============================================================
export type GoalType = z.infer<typeof GoalTypeSchema>;
export type ActivityLevel = z.infer<typeof ActivityLevelSchema>;
export type NutrientCode = z.infer<typeof NutrientCodeSchema>;
export type TargetNutrient = z.infer<typeof TargetNutrientSchema>;
export type CreateTargetRequest = z.infer<typeof CreateTargetRequestSchema>;
export type TargetResponse = z.infer<typeof TargetResponseSchema>;
export type TargetListResponse = z.infer<typeof TargetListResponseSchema>;
