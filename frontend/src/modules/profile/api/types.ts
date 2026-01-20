// src/modules/profile/api/types.ts

export type Sex = 'male' | 'female' | 'other' | 'undisclosed';

export type ProfileRequest = {
  sex: Sex;
  birthdate: string; // YYYY-MM-DD
  height_cm: number;
  weight_kg: number;
  meals_per_day?: number | null; // nullable in spec
};

export type ProfileResponse = {
  user_id: string;
  sex: Sex;
  birthdate: string;
  height_cm: number;
  weight_kg: number;
  image_id: string | null;
  meals_per_day: number | null;
  created_at: string;
  updated_at: string;
};
