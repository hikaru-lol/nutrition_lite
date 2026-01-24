import { clientApiFetch } from '@/shared/api/client';
import type { Profile, UpsertProfileInput } from '../contract/profileContract';

export function fetchProfile() {
  return clientApiFetch<Profile>('/profile', { method: 'GET' });
}

export function upsertProfile(body: UpsertProfileInput) {
  return clientApiFetch<Profile>('/profile', {
    method: 'PUT',
    body,
  });
}
