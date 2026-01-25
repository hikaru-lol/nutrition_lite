import { clientApiFetch } from '@/shared/api/client';
import {
  ProfileSchema,
  UpsertProfileSchema,
  type Profile,
  type UpsertProfileInput,
} from '../contract/profileContract';

export async function fetchProfile(): Promise<Profile> {
  const raw = await clientApiFetch<unknown>('/profile', { method: 'GET' });
  return ProfileSchema.parse(raw);
}

export async function upsertProfile(
  body: UpsertProfileInput
): Promise<Profile> {
  // 任意：フォーム側で保証してても、ここで“境界”としてvalidateしておくと事故りにくい
  const safe = UpsertProfileSchema.parse(body);

  const raw = await clientApiFetch<unknown>('/profile', {
    method: 'PUT',
    body: safe,
  });

  return ProfileSchema.parse(raw);
}
