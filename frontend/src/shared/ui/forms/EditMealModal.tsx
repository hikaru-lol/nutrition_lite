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
import { FoodSearchInput, type FoodSearchResult } from './FoodSearchInput';

const EditFormSchema = z.object({
  date: z.string(),
  meal_type: z.enum(['main', 'snack']),
  meal_index: z.number().int().min(1).nullable().optional(),
  name: z.string().min(1, '食品名は必須です'),
  amount_value: z.number().nullable().optional(),
  amount_unit: z.string().nullable().optional(),
  serving_count: z.number().min(0.1, '数量は0.1以上で入力してください').nullable().optional(),
  note: z.string().nullable().optional(),
});

export type EditMealFormValues = z.infer<typeof EditFormSchema>;

export interface MealItemForEdit {
  id: string;
  date: string;
  meal_type: 'main' | 'snack';
  meal_index: number | null;
  name: string;
  amount_value?: number | null;
  amount_unit?: string | null;
  serving_count?: number | null;
  note?: string | null;
}

interface EditMealModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (values: EditMealFormValues) => Promise<void>;
  mealItem: MealItemForEdit | null;
  isLoading?: boolean;
  error?: string | null;
}

export function EditMealModal({
  isOpen,
  onClose,
  onSubmit,
  mealItem,
  isLoading = false,
  error = null,
}: EditMealModalProps) {
  const [foodSearchValue, setFoodSearchValue] = useState('');

  const form = useForm<EditMealFormValues>({
    resolver: zodResolver(EditFormSchema),
    defaultValues: {
      date: '',
      meal_type: 'main',
      meal_index: null,
      name: '',
      amount_value: null,
      amount_unit: null,
      serving_count: 1,
      note: null,
    },
  });

  // mealItem が変更されたらフォームにプリフィル
  useEffect(() => {
    if (isOpen && mealItem) {
      const values: EditMealFormValues = {
        date: mealItem.date,
        meal_type: mealItem.meal_type,
        meal_index: mealItem.meal_index,
        name: mealItem.name,
        amount_value: mealItem.amount_value,
        amount_unit: mealItem.amount_unit,
        serving_count: mealItem.serving_count,
        note: mealItem.note,
      };

      form.reset(values);
      setFoodSearchValue(mealItem.name);
    }
  }, [isOpen, mealItem, form]);

  // モーダルが閉じられた時にフォームをリセット
  useEffect(() => {
    if (!isOpen) {
      form.reset();
      setFoodSearchValue('');
    }
  }, [isOpen, form]);

  const handleFoodSelect = (food: FoodSearchResult) => {
    form.setValue('name', food.name, { shouldValidate: true });
    setFoodSearchValue(food.name);
  };

  const handleSubmit: SubmitHandler<EditMealFormValues> = async (values) => {
    await onSubmit(values);
    onClose();
  };

  const handleClose = () => {
    form.reset();
    setFoodSearchValue('');
    onClose();
  };

  if (!mealItem) {
    return null;
  }

  const mealTypeLabel = mealItem.meal_type === 'main'
    ? `${mealItem.meal_index}回目の食事`
    : '間食';

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md mx-auto bg-background border shadow-lg">
        <DialogHeader>
          <DialogTitle>食事を編集</DialogTitle>
          <DialogDescription>
            {mealTypeLabel}の食事内容を編集します
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
              {isLoading ? '更新中...' : '更新'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}