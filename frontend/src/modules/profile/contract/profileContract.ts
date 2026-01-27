import { z } from 'zod';

// OpenAPI: Sex enum
export const SexSchema = z.enum(['male', 'female', 'other', 'undisclosed']);

// OpenAPI: ProfileResponse
export const ProfileSchema = z.object({
  user_id: z.string(),
  sex: SexSchema,
  birthdate: z.string(), // "YYYY-MM-DD"
  height_cm: z.number(),
  weight_kg: z.number(),
  image_id: z.string().nullable().optional(),
  meals_per_day: z.number().nullable().optional(),
  created_at: z.string(),
  updated_at: z.string(),
});

// OpenAPI: ProfileRequest
export const UpsertProfileSchema = z.object({
  sex: SexSchema,
  birthdate: z.string(), // "YYYY-MM-DD"
  height_cm: z.number(),
  weight_kg: z.number(),
  meals_per_day: z.number().nullable().optional(),
});

export type Sex = z.infer<typeof SexSchema>;
export type Profile = z.infer<typeof ProfileSchema>;
export type UpsertProfileInput = z.infer<typeof UpsertProfileSchema>;
