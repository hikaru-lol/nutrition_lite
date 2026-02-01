import { clientApiFetch } from '@/shared/api/client';

export type LoginRequest = { email: string; password: string };
export type RegisterRequest = { email: string; password: string };

export async function login(req: LoginRequest) {
  return clientApiFetch<void>('/auth/login', { method: 'POST', body: req });
}

export async function register(req: RegisterRequest) {
  // /api/auth/register → BFF → `${BACKEND_AUTH_PREFIX}/register`
  return clientApiFetch<void>('/auth/register', { method: 'POST', body: req });
}

export async function logout() {
  return clientApiFetch<void>('/auth/logout', { method: 'POST' });
}

export async function fetchCurrentUser() {
  return clientApiFetch<{ user: unknown }>('/auth/me', { method: 'GET' });
}
