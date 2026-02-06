import 'server-only';
import { bffServerFetch } from '@/shared/api/bffServer';

export type CurrentUser = {
  id: string;
  email: string;
  name: string | null;
};

export async function fetchCurrentUserServer() {
  // ✅ backend直叩きではなく BFF経由
  return bffServerFetch<CurrentUser>('/api/auth/me', { method: 'GET' });
}
