'use client';

import { useState, useMemo, useCallback } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

import { fetchProfile, upsertProfile } from '../api/profileClient';
import {
  ProfileFormSchema,
  type ProfileFormValues,
} from './useProfilePageModel';
import type { Profile, UpsertProfileInput } from '../contract/profileContract';

export interface ProfileEditPageModelState {
  // UI State
  isEditing: boolean;

  // Methods
  startEditing: () => void;
  cancelEditing: () => void;
  save: (values: ProfileFormValues) => Promise<void>;
}

export function useProfileEditPageModel(): ProfileEditPageModelState & {
  // Queries
  profileQuery: ReturnType<typeof useQuery<Profile | null>>;

  // Mutations
  saveMutation: ReturnType<typeof useMutation<Profile, Error, UpsertProfileInput>>;

  // Computed
  defaults: ProfileFormValues;
} {
  const queryClient = useQueryClient();
  const [isEditing, setIsEditing] = useState(false);

  // Profile Query
  const profileQuery = useQuery({
    queryKey: ['profile', 'me'] as const,
    queryFn: () => fetchProfile(),
    retry: false,
  });

  // Save Mutation
  const saveMutation = useMutation({
    mutationFn: upsertProfile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile', 'me'] });
      setIsEditing(false);
      toast.success('プロフィールを更新しました');
    },
    onError: (error) => {
      toast.error(
        error instanceof Error
          ? error.message
          : 'プロフィールの更新に失敗しました'
      );
    },
  });

  // Default values for form (memoized to prevent infinite re-renders)
  const defaults: ProfileFormValues = useMemo(() => {
    if (profileQuery.data) {
      return {
        sex: profileQuery.data.sex,
        birthdate: profileQuery.data.birthdate,
        height_cm: profileQuery.data.height_cm,
        weight_kg: profileQuery.data.weight_kg,
      };
    }
    return { sex: 'male', birthdate: '', height_cm: 170, weight_kg: 60 };
  }, [profileQuery.data]);

  // Handlers (memoized to prevent unnecessary re-renders)
  const startEditing = useCallback(() => setIsEditing(true), []);
  const cancelEditing = useCallback(() => setIsEditing(false), []);

  const save = useCallback(async (values: ProfileFormValues) => {
    const parsed = ProfileFormSchema.parse(values);
    await saveMutation.mutateAsync(parsed);
  }, [saveMutation]);

  return {
    // UI State
    isEditing,

    // Queries
    profileQuery,

    // Mutations
    saveMutation,

    // Computed
    defaults,

    // Methods
    startEditing,
    cancelEditing,
    save,
  };
}