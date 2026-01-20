// src/modules/auth/model/hooks.ts
'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { authApi } from '../api/client';
import type { UserSummary } from '../api/types';
import { ApiError } from '@/shared/lib/api/fetcher';
import { authKeys } from './keys';

async function getMeOrNull(): Promise<UserSummary | null> {
  try {
    const res = await authApi.me();
    return res.user;
  } catch (e) {
    if (e instanceof ApiError && e.status === 401) return null; // 未ログインは「正常系null」
    throw e;
  }
}

export function useCurrentUser() {
  return useQuery({
    queryKey: authKeys.me(),
    queryFn: getMeOrNull,
  });
}

export function useRegister() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: authApi.register,
    onSuccess: (res) => {
      qc.setQueryData(authKeys.me(), res.user);
    },
  });
}

export function useLogin() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: authApi.login,
    onSuccess: (res) => {
      qc.setQueryData(authKeys.me(), res.user);
    },
  });
}

export function useLogout() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: authApi.logout,
    onSuccess: () => {
      qc.setQueryData(authKeys.me(), null);
      // 必要なら全invalidate（ログアウト時は安全寄り）
      qc.invalidateQueries();
    },
  });
}

export function useDeleteMe() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: authApi.deleteMe,
    onSuccess: () => {
      qc.setQueryData(authKeys.me(), null);
      qc.invalidateQueries();
    },
  });
}
