'use client';

import { useMutation } from '@tanstack/react-query';
import { register } from '../api/authClient';

export type RegisterViewState =
  | { type: 'idle' }
  | { type: 'submitting' }
  | { type: 'success' }
  | { type: 'error'; message: string };

export function useRegisterPageModel() {
  const mutation = useMutation({
    mutationFn: async (vars: { email: string; password: string }) => {
      await register(vars);
    },
  });

  const state: RegisterViewState = mutation.isPending
    ? { type: 'submitting' }
    : mutation.isSuccess
    ? { type: 'success' }
    : mutation.isError
    ? {
        type: 'error',
        message: (mutation.error as Error)?.message ?? '登録に失敗しました',
      }
    : { type: 'idle' };

  return {
    state,
    submit: mutation.mutateAsync,
  };
}
