'use client';

import { useMutation } from '@tanstack/react-query';
import * as z from 'zod';

import { createTarget } from '../api/targetClient';
import {
  GoalTypeSchema,
  ActivityLevelSchema,
  type CreateTargetRequest,
  type Target,
} from '../contract/targetContract';

// ============================================================
// フォーム用スキーマ（UI が扱う入力型）
// ============================================================
export const TargetFormSchema = z.object({
  title: z.string().min(1, 'タイトルを入力してください'),
  goal_type: GoalTypeSchema,
  goal_description: z.string().optional(),
  activity_level: ActivityLevelSchema,
});

export type TargetFormValues = z.input<typeof TargetFormSchema>;

// ============================================================
// ViewState（UI が見る状態）
// ============================================================
export type TargetGeneratorViewState =
  | { type: 'idle' }
  | { type: 'submitting' }
  | { type: 'success'; result: Target }
  | { type: 'error'; message: string };

// ============================================================
// デフォルト値
// ============================================================
export const defaultFormValues: TargetFormValues = {
  title: '',
  goal_type: 'maintain',
  goal_description: '',
  activity_level: 'normal',
};

// ============================================================
// UI 向けラベル（表示用）
// ============================================================
export const goalTypeLabels: Record<TargetFormValues['goal_type'], string> = {
  weight_loss: '減量',
  maintain: '維持',
  weight_gain: '増量',
  health_improve: '健康改善',
};

export const activityLevelLabels: Record<
  TargetFormValues['activity_level'],
  string
> = {
  low: '低い（ほぼ運動しない）',
  normal: '普通（週3〜4）',
  high: '高い（毎日運動）',
};

// ============================================================
// PageModel Hook
// ============================================================
export function useTargetGeneratorPageModel() {
  const mutation = useMutation({
    mutationFn: async (values: TargetFormValues) => {
      // フォーム値を parse して API 用の型に変換
      const parsed = TargetFormSchema.parse(values);
      const req: CreateTargetRequest = {
        title: parsed.title,
        goal_type: parsed.goal_type,
        goal_description: parsed.goal_description ?? null,
        activity_level: parsed.activity_level,
      };
      return createTarget(req);
    },
  });

  const state: TargetGeneratorViewState = mutation.isPending
    ? { type: 'submitting' }
    : mutation.isSuccess
    ? { type: 'success', result: mutation.data }
    : mutation.isError
    ? {
        type: 'error',
        message:
          mutation.error instanceof Error
            ? mutation.error.message
            : '生成に失敗しました',
      }
    : { type: 'idle' };

  return {
    TargetFormSchema,
    defaultFormValues,
    goalTypeLabels,
    activityLevelLabels,
    state,
    submit: mutation.mutateAsync,
  };
}
