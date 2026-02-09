'use client';

import React, { useState, useEffect } from 'react';
import { useForm, type SubmitHandler } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { FoodSearchInput, type FoodSearchResult } from '@/shared/ui/forms/FoodSearchInput';

const FormSchema = z.object({
  date: z.string(),
  meal_type: z.enum(['main', 'snack']),
  meal_index: z.number().int().min(1).nullable().optional(),
  name: z.string().min(1, '食品名は必須です'),
  amount_value: z.number().nullable().optional(),
  amount_unit: z.string().nullable().optional(),
  serving_count: z.number().min(0.1, '数量は0.1以上で入力してください').nullable().optional(),
  note: z.string().nullable().optional(),
});

export type AddMealFormValues = z.infer<typeof FormSchema>;

interface AddMealModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (values: AddMealFormValues) => Promise<void>;
  mealType: 'main' | 'snack';
  mealIndex?: number;
  date: string;
  isLoading?: boolean;
  error?: string | null;
}

export function AddMealModal({
  isOpen,
  onClose,
  onSubmit,
  mealType,
  mealIndex,
  date,
  isLoading = false,
  error = null,
}: AddMealModalProps) {
  const [foodSearchValue, setFoodSearchValue] = useState('');

  const form = useForm<AddMealFormValues>({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      date,
      meal_type: mealType,
      meal_index: mealType === 'main' ? mealIndex : null,
      name: '',
      amount_value: null,
      amount_unit: null,
      serving_count: 1,
      note: null,
    },
  });

  // モーダルが開かれる度にフォームをリセット
  useEffect(() => {
    if (isOpen) {
      form.reset({
        date,
        meal_type: mealType,
        meal_index: mealType === 'main' ? mealIndex : null,
        name: '',
        amount_value: null,
        amount_unit: null,
        serving_count: 1,
        note: null,
      });
      setFoodSearchValue('');
    }
  }, [isOpen, date, mealType, mealIndex, form]);

  const handleFoodSelect = (food: FoodSearchResult) => {
    form.setValue('name', food.name, { shouldValidate: true });
    setFoodSearchValue(food.name);
  };

  const handleSubmit: SubmitHandler<AddMealFormValues> = async (values) => {
    await onSubmit(values);
    onClose();
  };

  const handleClose = () => {
    form.reset();
    setFoodSearchValue('');
    onClose();
  };

  const mealTypeLabel = mealType === 'main'
    ? `${mealIndex}回目の食事`
    : '間食';

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md mx-auto bg-background border shadow-lg">
        <DialogHeader>
          <DialogTitle>食事を追加</DialogTitle>
          <DialogDescription>
            {mealTypeLabel}の食事内容を記録します
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
          {/* 食品名検索 */}
          <div className="space-y-2">
            <Label htmlFor="food-search">食品名</Label>
            <FoodSearchInput
              value={foodSearchValue}
              onValueChange={(value) => {
                setFoodSearchValue(value);
                form.setValue('name', value, { shouldValidate: true });
              }}
              onSelectFood={handleFoodSelect}
              placeholder="例: 白米、とんかつ"
              disabled={isLoading}
            />
            {form.formState.errors.name && (
              <p className="text-sm text-destructive">
                {form.formState.errors.name.message}
              </p>
            )}
          </div>

          {/* 数量 */}
          <div className="space-y-2">
            <Label htmlFor="serving-count">数量</Label>
            <Input
              id="serving-count"
              type="number"
              inputMode="decimal"
              step="0.1"
              min="0.1"
              placeholder="例: 1"
              value={form.watch('serving_count') ?? ''}
              onChange={(e) => {
                const v = e.target.value;
                form.setValue(
                  'serving_count',
                  v === '' ? null : Number(v),
                  { shouldValidate: true }
                );
              }}
              disabled={isLoading}
            />
            {form.formState.errors.serving_count && (
              <p className="text-sm text-destructive">
                {form.formState.errors.serving_count.message}
              </p>
            )}
          </div>

          {/* メモ */}
          <div className="space-y-2">
            <Label htmlFor="note">メモ（任意）</Label>
            <Input
              id="note"
              placeholder="例: おいしかった、外食"
              value={form.watch('note') ?? ''}
              onChange={(e) => {
                form.setValue('note', e.target.value || null);
              }}
              disabled={isLoading}
            />
          </div>

          {/* エラー表示 */}
          {error && (
            <div className="text-sm text-destructive bg-destructive/10 p-3 rounded-md">
              {error}
            </div>
          )}

          {/* アクションボタン */}
          <div className="flex items-center justify-end gap-3 pt-2">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isLoading}
            >
              キャンセル
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? '追加中...' : '追加'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}