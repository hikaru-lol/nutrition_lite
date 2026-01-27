import { clientApiFetch } from '@/shared/api/client';
import {
  ProfileSchema,
  UpsertProfileSchema,
  type Profile,
  type UpsertProfileInput,
} from '../contract/profileContract';

/**
 * 404 の場合は null を返す（プロフィール未作成）
 */
export async function fetchProfile(): Promise<Profile | null> {
  try {
    const raw = await clientApiFetch<unknown>('/profile/me', { method: 'GET' });
    return ProfileSchema.parse(raw);
  } catch (err) {
    // 404 = プロフィール未作成として扱う
    if (err instanceof Error && err.message.includes('PROFILE_NOT_FOUND')) {
      return null;
    }
    throw err;
  }
}

export async function upsertProfile(
  body: UpsertProfileInput
): Promise<Profile> {
  // 任意：フォーム側で保証してても、ここで“境界”としてvalidateしておくと事故りにくい
  const safe = UpsertProfileSchema.parse(body);

  const raw = await clientApiFetch<unknown>('/profile/me', {
    method: 'PUT',
    body: safe,
  });

  return ProfileSchema.parse(raw);
}
