import { z } from 'zod';

export const MealTypeSchema = z.enum(['main', 'snack']);

export const MealItemRequestSchema = z.object({
  date: z.string(), // YYYY-MM-DD（厳密化したければ regex でもOK）
  meal_type: MealTypeSchema,
  meal_index: z.number().int().min(1).nullable().optional(),
  name: z.string().min(1),
  amount_value: z.number().nullable().optional(),
  amount_unit: z.string().nullable().optional(),
  serving_count: z.number().nullable().optional(),
  note: z.string().nullable().optional(),
});

export const MealItemResponseSchema = MealItemRequestSchema.extend({
  id: z.string(),
});

export const MealItemListResponseSchema = z.object({
  items: z.array(MealItemResponseSchema),
});

export type MealType = z.infer<typeof MealTypeSchema>;
export type MealItemRequest = z.infer<typeof MealItemRequestSchema>;
export type MealItemResponse = z.infer<typeof MealItemResponseSchema>;
export type MealItemListResponse = z.infer<typeof MealItemListResponseSchema>;
