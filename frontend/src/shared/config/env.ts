// src/shared/config/env.ts
import { z } from 'zod';

const EnvSchema = z.object({
  NEXT_PUBLIC_API_BASE_URL: z.string().optional().default(''), // 同一オリジンなら空でOK
});

export const env = EnvSchema.parse({
  NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
});

export const API_BASE_URL = env.NEXT_PUBLIC_API_BASE_URL;
