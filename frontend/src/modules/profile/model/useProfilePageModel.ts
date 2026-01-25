import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import * as z from 'zod'; // ← v4 はこれが安全

import { fetchProfile, upsertProfile } from '../api/profileClient';
import { SexSchema } from '../contract/profileContract';

// coerce を使うなら input/output を分けるのが正解
export const ProfileFormSchema = z.object({
  sex: SexSchema,
  birthday: z.string().min(1),
  heightCm: z.coerce.number().int().min(50).max(250),
  weightKg: z.coerce.number().min(20).max(300),
});

// ✅ フォームが扱うのは「入力型」
export type ProfileFormValues = z.input<typeof ProfileFormSchema>;
// ✅ 保存・APIへ渡すのは「出力型」
type ProfileParsedValues = z.output<typeof ProfileFormSchema>;

const qk = { me: ['profile', 'me'] as const };

export function useProfilePageModel() {
  const qc = useQueryClient();

  const profileQuery = useQuery({
    queryKey: qk.me,
    queryFn: () => fetchProfile(),
  });

  const upsertMutation = useMutation({
    mutationFn: (values: ProfileParsedValues) => upsertProfile(values),
    onSuccess: () => qc.invalidateQueries({ queryKey: qk.me }),
  });

  const defaults: ProfileFormValues = profileQuery.data
    ? {
        sex: profileQuery.data.sex,
        birthday: profileQuery.data.birthday,
        heightCm: profileQuery.data.heightCm,
        weightKg: profileQuery.data.weightKg,
      }
    : { sex: 'male', birthday: '', heightCm: 170, weightKg: 60 };

  return {
    ProfileFormSchema,
    profileQuery,
    upsertMutation,
    defaults,
    async save(values: ProfileFormValues) {
      // ✅ ここで parse して「出力型」にしてから APIへ
      const parsed = ProfileFormSchema.parse(values) as ProfileParsedValues;
      return upsertMutation.mutateAsync(parsed);
    },
  };
}
