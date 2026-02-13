import 'server-only';

const BACKEND_INTERNAL_ORIGIN =
  process.env.BACKEND_INTERNAL_ORIGIN ?? 'http://127.0.0.1:8000';
const BACKEND_API_PREFIX =
  process.env.BACKEND_API_PREFIX ?? '/api/v1';

export const serverEnv = {
  BACKEND_INTERNAL_ORIGIN,
  BACKEND_API_PREFIX,
  BACKEND_AUTH_PREFIX: process.env.BACKEND_AUTH_PREFIX ?? '/api/v1/auth',
} as const;
