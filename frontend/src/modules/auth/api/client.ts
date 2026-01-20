// src/modules/auth/api/client.ts
import { apiFetch } from '@/shared/lib/api/fetcher';
import type {
  AuthUserResponse,
  LoginRequest,
  RegisterRequest,
  RefreshResponse,
} from './types';

export const authApi = {
  register: (body: RegisterRequest) =>
    apiFetch<AuthUserResponse>('/auth/register', {
      method: 'POST',
      body,
      skipAuthRefresh: true,
    }),

  login: (body: LoginRequest) =>
    apiFetch<AuthUserResponse>('/auth/login', {
      method: 'POST',
      body,
      skipAuthRefresh: true,
    }),

  logout: () => apiFetch<void>('/auth/logout', { method: 'POST' }),

  me: () => apiFetch<AuthUserResponse>('/auth/me'),

  deleteMe: () => apiFetch<void>('/auth/me', { method: 'DELETE' }),

  refresh: () =>
    apiFetch<RefreshResponse>('/auth/refresh', {
      method: 'POST',
      skipAuthRefresh: true,
    }),
};
