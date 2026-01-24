import { z } from 'zod';

export const SexSchema = z.enum(['male', 'female', 'other']);

export const ProfileSchema = z.object({
  id: z.string(),
  sex: SexSchema,
  birthday: z.string(), // "YYYY-MM-DD"
  heightCm: z.number(),
  weightKg: z.number(),
  createdAt: z.string().optional(),
  updatedAt: z.string().optional(),
});

export const UpsertProfileSchema = z.object({
  sex: SexSchema,
  birthday: z.string(), // "YYYY-MM-DD"
  heightCm: z.number(),
  weightKg: z.number(),
});

export type Sex = z.infer<typeof SexSchema>;
export type Profile = z.infer<typeof ProfileSchema>;
export type UpsertProfileInput = z.infer<typeof UpsertProfileSchema>;
