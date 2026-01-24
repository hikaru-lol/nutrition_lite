'use client';

import { useMutation } from '@tanstack/react-query';
import { login } from '../api/authClient';

export function useLoginPageModel() {
  const mutation = useMutation({
    mutationFn: async (vars: { email: string; password: string }) => {
      await login(vars); // /api/auth/login → BFF → backend（Set-Cookieが返る想定）
    },
  });

  return {
    isSubmitting: mutation.isPending,
    errorMessage: mutation.isError
      ? (mutation.error as Error)?.message ?? 'ログインに失敗しました'
      : null,
    submit: mutation.mutateAsync,
  };
}
