import { z } from 'zod';

export const generateTargetRequestSchema = z.object({
  sex: z.enum(['male', 'female']),
  age: z.number().int().min(1).max(120),
  heightCm: z.number().int().min(50).max(250),
  weightKg: z.number().min(10).max(300),
  activityLevel: z.enum([
    'sedentary',
    'light',
    'moderate',
    'active',
    'very_active',
  ]),
  goal: z.enum(['lose', 'maintain', 'gain']),
});

export type GenerateTargetRequest = z.infer<typeof generateTargetRequestSchema>;
