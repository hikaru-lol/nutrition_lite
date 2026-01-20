// src/modules/auth/api/authServer.ts
import { serverApiFetch } from '@/shared/api/server';
import type { CurrentUserResponse } from '@/shared/api/contracts';

export async function fetchCurrentUserServer() {
  return serverApiFetch<CurrentUserResponse>('/api/v1/auth/me', {
    method: 'GET',
    cache: 'no-store',
  });
}
