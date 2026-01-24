'use client';

import { useMutation } from '@tanstack/react-query';
import { generateTarget, type TargetResult } from '../api/targetClient';
import type { GenerateTargetRequest } from '../contract/targetContract';

export type TargetGeneratorViewState =
  | { type: 'idle' }
  | { type: 'submitting' }
  | { type: 'success'; result: TargetResult }
  | { type: 'error'; message: string };

export function useTargetGeneratorPageModel() {
  const mutation = useMutation({
    mutationFn: async (req: GenerateTargetRequest) => generateTarget(req),
  });

  const state: TargetGeneratorViewState = mutation.isPendingw
    ? { type: 'submitting' }
    : mutation.isSuccess
    ? { type: 'success', result: mutation.data }
    : mutation.isError
    ? {
        type: 'error',
        message: (mutation.error as any)?.message ?? '生成に失敗しました',
      }
    : { type: 'idle' };

  return {
    state,
    submit: mutation.mutateAsync,
  };
}
