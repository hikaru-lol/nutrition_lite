import { useMemo } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import * as z from 'zod'; // ← v4 はこれが安全

import { fetchProfile, upsertProfile } from '../api/profileClient';
import {
  SexSchema,
  type UpsertProfileInput,
} from '../contract/profileContract';

// フォーム用スキーマ（camelCase, coerce で文字列→数値変換）
export const ProfileFormSchema = z.object({
  sex: SexSchema,
  birthdate: z.string().min(1),
  height_cm: z.coerce.number().int().min(50).max(250),
  weight_kg: z.coerce.number().min(20).max(300),
  meals_per_day: z.coerce.number().int().min(1).max(6).default(3),
});

// ✅ フォームが扱うのは「入力型」
export type ProfileFormValues = z.input<typeof ProfileFormSchema>;

const qk = { me: ['profile', 'me'] as const };

export function useProfilePageModel() {
  const qc = useQueryClient();

  const profileQuery = useQuery({
    queryKey: qk.me,
    queryFn: () => fetchProfile(),
  });

  const upsertMutation = useMutation({
    mutationFn: (values: UpsertProfileInput) => upsertProfile(values),
    onSuccess: () => qc.invalidateQueries({ queryKey: qk.me }),
  });

  const defaults: ProfileFormValues = useMemo(() => {
    if (profileQuery.data) {
      return {
        sex: profileQuery.data.sex,
        birthdate: profileQuery.data.birthdate,
        height_cm: profileQuery.data.height_cm,
        weight_kg: profileQuery.data.weight_kg,
        meals_per_day: profileQuery.data.meals_per_day ?? 3,
      };
    }
    return { sex: 'male', birthdate: '', height_cm: 170, weight_kg: 60, meals_per_day: 3 };
  }, [profileQuery.data]);

  return {
    ProfileFormSchema,
    profileQuery,
    upsertMutation,
    defaults,
    async save(values: ProfileFormValues) {
      // parse して API スキーマ型に変換
      const parsed = ProfileFormSchema.parse(values);
      // meals_per_day が未設定の場合はデフォルト値3を設定
      const payload = {
        ...parsed,
        meals_per_day: parsed.meals_per_day ?? 3,
      };
      return upsertMutation.mutateAsync(payload);
    },
  };
}
