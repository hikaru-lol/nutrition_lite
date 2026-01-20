// frontend/components/targets/CreateTargetForm.tsx
'use client';

import * as React from 'react';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import type { GoalType, ActivityLevel } from '@/lib/api/targets';

export type CreateTargetFormValues = {
  title: string;
  goal_type: GoalType;
  activity_level: ActivityLevel;
  goal_description: string;
};

type CreateTargetFormProps = {
  initialValues?: Partial<CreateTargetFormValues>;
  onSubmit: (values: CreateTargetFormValues) => Promise<void> | void;
  onCancel?: () => void;
  isSubmitting?: boolean;
  serverError?: string | null;
};

const defaultValues: CreateTargetFormValues = {
  title: '',
  goal_type: 'maintain',
  activity_level: 'normal',
  goal_description: '',
};

export function CreateTargetForm({
  initialValues,
  onSubmit,
  onCancel,
  isSubmitting = false,
  serverError,
}: CreateTargetFormProps) {
  const [values, setValues] = React.useState<CreateTargetFormValues>({
    ...defaultValues,
    ...initialValues,
  });
  const [fieldError, setFieldError] = React.useState<string | null>(null);

  const handleChange =
    (field: keyof CreateTargetFormValues) =>
    (
      e: React.ChangeEvent<
        HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
      >
    ) => {
      setValues((prev) => ({ ...prev, [field]: e.target.value }));
    };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!values.title.trim()) {
      setFieldError('ターゲット名を入力してください。');
      return;
    }
    setFieldError(null);
    await onSubmit({
      ...values,
      title: values.title.trim(),
    });
  };

  return (
    <form className="space-y-3" onSubmit={handleSubmit}>
      {(fieldError || serverError) && (
        <p className="text-xs text-rose-400 bg-rose-500/10 border border-rose-500/40 rounded-lg px-3 py-2">
          {fieldError || serverError}
        </p>
      )}

      <div>
        <Label htmlFor="target-title">ターゲット名</Label>
        <Input
          id="target-title"
          placeholder="例）減量期（春）"
          value={values.title}
          onChange={handleChange('title')}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div>
          <Label htmlFor="goal-type">目標</Label>
          <select
            id="goal-type"
            className="w-full rounded-xl border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500/70 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950"
            value={values.goal_type}
            onChange={handleChange('goal_type')}
          >
            <option value="weight_loss">減量</option>
            <option value="maintain">現状維持</option>
            <option value="weight_gain">増量</option>
            <option value="health_improve">健康改善</option>
          </select>
        </div>

        <div>
          <Label htmlFor="activity-level">活動レベル</Label>
          <select
            id="activity-level"
            className="w-full rounded-xl border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500/70 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950"
            value={values.activity_level}
            onChange={handleChange('activity_level')}
          >
            <option value="low">低め（座りがち）</option>
            <option value="normal">ふつう（軽い運動あり）</option>
            <option value="high">高め（立ち仕事・運動量多め）</option>
          </select>
        </div>
      </div>

      <div>
        <Label htmlFor="goal-description">目標のイメージ（任意）</Label>
        <textarea
          id="goal-description"
          className="w-full rounded-xl border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-50 placeholder:text-slate-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500/70 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950"
          rows={3}
          placeholder="例）体重を3ヶ月で3kg減らしたい、平日はランチ後に散歩をする…など"
          value={values.goal_description}
          onChange={handleChange('goal_description')}
        />
      </div>

      <div className="flex justify-end gap-2 pt-1">
        {onCancel && (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={onCancel}
            disabled={isSubmitting}
          >
            キャンセル
          </Button>
        )}
        <Button type="submit" size="sm" disabled={isSubmitting}>
          {isSubmitting ? '作成中...' : 'この内容で作成'}
        </Button>
      </div>
    </form>
  );
}
