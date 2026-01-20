// frontend/components/meals/MealItemDialog.tsx
'use client';

import * as React from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';

export type MealItemFormValues = {
  name: string;
  amountValue: string;
  amountUnit: string;
  servingCount: string;
  note: string;
};

export type MealItemDialogProps = {
  open: boolean;
  mode: 'create' | 'edit';
  mealType: 'main' | 'snack';
  mealIndex: number | null;
  initialValues?: Partial<MealItemFormValues>;
  onOpenChange: (open: boolean) => void;
  onSubmit: (values: MealItemFormValues) => Promise<void> | void;
  isSubmitting?: boolean;
  errorMessage?: string | null;
};

const defaultValues: MealItemFormValues = {
  name: '',
  amountValue: '',
  amountUnit: '',
  servingCount: '',
  note: '',
};

export function MealItemDialog({
  open,
  mode,
  mealType,
  mealIndex,
  initialValues,
  onOpenChange,
  onSubmit,
  isSubmitting = false,
  errorMessage,
}: MealItemDialogProps) {
  const [values, setValues] = React.useState<MealItemFormValues>({
    ...defaultValues,
    ...initialValues,
  });

  const [fieldError, setFieldError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (open) {
      setValues({ ...defaultValues, ...initialValues });
      setFieldError(null);
    }
  }, [open, initialValues]);

  const handleChange =
    (field: keyof MealItemFormValues) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      setValues((prev) => ({ ...prev, [field]: e.target.value }));
    };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!values.name) {
      setFieldError('食品名を入力してください。');
      return;
    }
    setFieldError(null);
    await onSubmit(values);
  };

  if (!open) return null;

  const title = mode === 'create' ? '食事を追加' : '食事を編集';
  const subtitle =
    mealType === 'main'
      ? mealIndex
        ? `${mealIndex} 回目の食事`
        : 'メインの食事'
      : '間食';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70">
      <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900/95 p-4 md:p-5 shadow-xl">
        <div className="mb-3">
          <p className="text-xs text-slate-400">{subtitle}</p>
          <h2 className="mt-1 text-sm font-semibold text-slate-50">{title}</h2>
        </div>

        <form className="space-y-3" onSubmit={handleSubmit}>
          {(fieldError || errorMessage) && (
            <p className="text-xs text-rose-400 bg-rose-500/10 border border-rose-500/40 rounded-lg px-3 py-2">
              {fieldError || errorMessage}
            </p>
          )}

          <div>
            <Label htmlFor="meal-name">食品名</Label>
            <Input
              id="meal-name"
              placeholder="例）鶏むね肉のグリル"
              value={values.name}
              onChange={handleChange('name')}
            />
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div>
              <Label htmlFor="amountValue">量</Label>
              <Input
                id="amountValue"
                type="number"
                placeholder="150"
                value={values.amountValue}
                onChange={handleChange('amountValue')}
              />
            </div>
            <div>
              <Label htmlFor="amountUnit">単位</Label>
              <Input
                id="amountUnit"
                placeholder="g / ml / 個"
                value={values.amountUnit}
                onChange={handleChange('amountUnit')}
              />
            </div>
          </div>

          <div>
            <Label htmlFor="servingCount">何人前 / 何皿分（任意）</Label>
            <Input
              id="servingCount"
              type="number"
              placeholder="1"
              value={values.servingCount}
              onChange={handleChange('servingCount')}
            />
          </div>

          <div>
            <Label htmlFor="note">メモ（任意）</Label>
            <textarea
              id="note"
              className="w-full rounded-xl border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-50 placeholder:text-slate-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500/70 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950"
              rows={3}
              placeholder="味付けや部位など、メモがあれば"
              value={values.note}
              onChange={handleChange('note')}
            />
          </div>

          <div className="mt-3 flex items-center justify-end gap-2">
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => onOpenChange(false)}
              disabled={isSubmitting}
            >
              キャンセル
            </Button>
            <Button type="submit" size="sm" disabled={isSubmitting}>
              {isSubmitting
                ? mode === 'create'
                  ? '追加中...'
                  : '保存中...'
                : mode === 'create'
                ? '追加する'
                : '保存する'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
