// src/modules/auth/api/authClient.ts
import { apiFetch, registerRefresh } from '@/shared/api/client';
import type {
  CurrentUserResponse,
  RefreshResponse,
} from '@/shared/api/contracts';

export async function fetchCurrentUser() {
  return apiFetch<CurrentUserResponse>('/api/v1/auth/me', { method: 'GET' });
}

export async function refreshSession(): Promise<boolean> {
  try {
    const res = await apiFetch<RefreshResponse>('/api/v1/auth/refresh', {
      method: 'POST',
      retryOnUnauthorized: false,
    });
    return !!res.ok;
  } catch {
    return false;
  }
}

// apiFetch が401時に呼ぶ refresh を登録
registerRefresh(refreshSession);
