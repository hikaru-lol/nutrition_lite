// src/modules/profile/api/client.ts
import { apiFetch } from '@/shared/lib/api/fetcher';
import type { ProfileRequest, ProfileResponse } from './types';

export const profileApi = {
  getMe: () => apiFetch<ProfileResponse>('/profile/me'),
  upsertMe: (body: ProfileRequest) =>
    apiFetch<ProfileResponse>('/profile/me', { method: 'PUT', body }),
};
