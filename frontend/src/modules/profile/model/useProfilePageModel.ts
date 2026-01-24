import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { z } from 'zod';

import { fetchProfile, upsertProfile } from '../api/profileClient';
import { SexSchema } from '../contract/profileContract';

export const ProfileFormSchema = z.object({
  sex: SexSchema,
  birthday: z.string().min(1),
  heightCm: z.coerce.number().int().min(50).max(250),
  weightKg: z.coerce.number().min(20).max(300),
});

export type ProfileFormValues = z.infer<typeof ProfileFormSchema>;

const qk = {
  me: ['profile', 'me'] as const,
};

export function useProfilePageModel() {
  const qc = useQueryClient();

  const profileQuery = useQuery({
    queryKey: qk.me,
    queryFn: () => fetchProfile(),
  });

  const upsertMutation = useMutation({
    mutationFn: (values: ProfileFormValues) => upsertProfile(values),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.me });
    },
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
      return upsertMutation.mutateAsync(values);
    },
  };
}
