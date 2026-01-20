// frontend/components/profile/ProfileForm.tsx
'use client';

import * as React from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import type { Sex } from '@/lib/api/profile';

export type ProfileFormValues = {
  sex: Sex;
  birthdate: string; // "" or "YYYY-MM-DD"
  heightCm: string; // 入力は string で保持
  weightKg: string;
  mealsPerDay: string; // "2" | "3" | "4" など
};

export type ProfileFormProps = {
  initialValues?: Partial<ProfileFormValues>;
  onSubmit: (values: ProfileFormValues) => Promise<void> | void;
  isSubmitting?: boolean;
  serverError?: string | null;
  submitLabel?: string;
};

const defaultValues: ProfileFormValues = {
  sex: 'undisclosed',
  birthdate: '',
  heightCm: '',
  weightKg: '',
  mealsPerDay: '3',
};

export function ProfileForm({
  initialValues,
  onSubmit,
  isSubmitting = false,
  serverError,
  submitLabel = '保存する',
}: ProfileFormProps) {
  const [values, setValues] = React.useState<ProfileFormValues>({
    ...defaultValues,
    ...initialValues,
  });

  const [fieldError, setFieldError] = React.useState<string | null>(null);

  const handleChange =
    (field: keyof ProfileFormValues) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
      setValues((prev) => ({ ...prev, [field]: e.target.value }));
    };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // 簡易バリデーション（必要になったら強化）
    if (!values.birthdate) {
      setFieldError('生年月日を入力してください。');
      return;
    }
    if (!values.heightCm || Number(values.heightCm) <= 0) {
      setFieldError('身長は0より大きい値を入力してください。');
      return;
    }
    if (!values.weightKg || Number(values.weightKg) <= 0) {
      setFieldError('体重は0より大きい値を入力してください。');
      return;
    }
    if (!values.mealsPerDay || Number(values.mealsPerDay) < 1) {
      setFieldError('1日のメイン食事回数を正しく入力してください。');
      return;
    }

    setFieldError(null);
    await onSubmit(values);
  };

  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      {(fieldError || serverError) && (
        <p className="text-xs text-rose-400 bg-rose-500/10 border border-rose-500/40 rounded-lg px-3 py-2">
          {fieldError || serverError}
        </p>
      )}

      {/* sex */}
      <div>
        <Label htmlFor="sex">性別（任意）</Label>
        <select
          id="sex"
          className="w-full rounded-xl border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500/70 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950"
          value={values.sex}
          onChange={handleChange('sex')}
        >
          <option value="undisclosed">選択しない</option>
          <option value="male">男性</option>
          <option value="female">女性</option>
          <option value="other">その他</option>
        </select>
      </div>

      {/* birthdate */}
      <div>
        <Label htmlFor="birthdate">生年月日</Label>
        <Input
          id="birthdate"
          type="date"
          value={values.birthdate}
          onChange={handleChange('birthdate')}
        />
      </div>

      {/* height */}
      <div>
        <Label htmlFor="height">身長（cm）</Label>
        <Input
          id="height"
          type="number"
          placeholder="170"
          value={values.heightCm}
          onChange={handleChange('heightCm')}
        />
      </div>

      {/* weight */}
      <div>
        <Label htmlFor="weight">体重（kg）</Label>
        <Input
          id="weight"
          type="number"
          placeholder="60"
          value={values.weightKg}
          onChange={handleChange('weightKg')}
        />
      </div>

      {/* meals_per_day */}
      <div>
        <Label htmlFor="mealsPerDay">1日のメイン食事回数</Label>
        <select
          id="mealsPerDay"
          className="w-full rounded-xl border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500/70 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950"
          value={values.mealsPerDay}
          onChange={handleChange('mealsPerDay')}
        >
          <option value="2">2回</option>
          <option value="3">3回</option>
          <option value="4">4回</option>
        </select>
        <p className="mt-1 text-xs text-slate-500">
          朝・昼・夜など、1日に記録したい「メインの食事回数」です。後から変更できます。
        </p>
      </div>

      <Button type="submit" className="w-full" disabled={isSubmitting}>
        {isSubmitting ? '保存中...' : submitLabel}
      </Button>
    </form>
  );
}
