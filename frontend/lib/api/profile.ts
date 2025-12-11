// frontend/lib/api/profile.ts
import { apiGet, apiPut } from './client';

export type Sex = 'male' | 'female' | 'other' | 'undisclosed';

export type ProfileResponseApi = {
  user_id: string;
  sex: Sex;
  birthdate: string; // "YYYY-MM-DD"
  height_cm: number;
  weight_kg: number;
  meals_per_day: number | null;
  image_id: string | null;
  created_at: string;
  updated_at: string;
};

export type ProfileRequestApi = {
  sex: Sex;
  birthdate: string; // "YYYY-MM-DD"
  height_cm: number;
  weight_kg: number;
  meals_per_day?: number | null; // schema上 nullable, requiredではない
};

export async function fetchProfile(): Promise<ProfileResponseApi> {
  return apiGet<ProfileResponseApi>('/profile/me');
}

export async function upsertProfile(
  body: ProfileRequestApi
): Promise<ProfileResponseApi> {
  return apiPut<ProfileResponseApi>('/profile/me', body);
}
