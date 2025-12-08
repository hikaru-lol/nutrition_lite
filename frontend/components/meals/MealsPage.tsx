// frontend/components/meals/MealsPage.tsx
'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { useState } from 'react';
import { MealsHeader } from './MealsHeader';
import { MainMealsSection } from './MainMealsSection';
import { SnackMealsSection } from './SnackMealsSection';
import { MealItemDialog, type MealItemFormValues } from './MealItemDialog';
import { useMealsByDate } from '@/lib/hooks/useMealsByDate';
import {
  createMealItem,
  updateMealItem,
  deleteMealItem,
} from '@/lib/api/meals';

export function MealsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const paramDate = searchParams.get('date');
  const today = new Date().toISOString().slice(0, 10);
  const date = paramDate ?? today;

  const { data, isLoading, error, refresh } = useMealsByDate(date);

  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogMode, setDialogMode] = useState<'create' | 'edit'>('create');
  const [dialogMealType, setDialogMealType] = useState<'main' | 'snack'>(
    'main'
  );
  const [dialogMealIndex, setDialogMealIndex] = useState<number | null>(1);
  const [editingItemId, setEditingItemId] = useState<string | null>(null);
  const [initialFormValues, setInitialFormValues] = useState<
    Partial<MealItemFormValues> | undefined
  >(undefined);
  const [dialogError, setDialogError] = useState<string | null>(null);
  const [dialogSubmitting, setDialogSubmitting] = useState(false);

  const changeDate = (newDate: string) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set('date', newDate);
    router.push(`/meals?${params.toString()}`);
  };

  const backToToday = () => {
    changeDate(today);
  };

  const openCreateDialog = (
    mealType: 'main' | 'snack',
    mealIndex: number | null
  ) => {
    setDialogMode('create');
    setDialogMealType(mealType);
    setDialogMealIndex(mealIndex);
    setEditingItemId(null);
    setInitialFormValues(undefined);
    setDialogError(null);
    setDialogOpen(true);
  };

  const openEditDialog = (entryId: string) => {
    if (!data) return;
    const allItems = [
      ...data.mainSlots.flatMap((s) => s.items),
      ...data.snacks,
    ];
    const item = allItems.find((i) => i.id === entryId);
    if (!item) return;

    setDialogMode('edit');
    setDialogMealType(item.mealType);
    setDialogMealIndex(item.mealIndex);
    setEditingItemId(entryId);
    setInitialFormValues({
      name: item.name,
      amountValue: '', // amountText から値と単位を厳密に復元するのは後でやってもOK
      amountUnit: '',
      servingCount: '',
      note: item.note ?? '',
    });
    setDialogError(null);
    setDialogOpen(true);
  };

  const handleSubmitDialog = async (values: MealItemFormValues) => {
    try {
      setDialogSubmitting(true);
      setDialogError(null);

      const amountValue = values.amountValue
        ? Number(values.amountValue)
        : null;
      const servingCount = values.servingCount
        ? Number(values.servingCount)
        : null;
      const amountUnit = values.amountUnit || null;
      const note = values.note || null;

      if (dialogMode === 'create') {
        await createMealItem({
          date,
          meal_type: dialogMealType,
          meal_index: dialogMealType === 'main' ? dialogMealIndex : null,
          name: values.name,
          amount_value: amountValue,
          amount_unit: amountUnit,
          serving_count: servingCount,
          note,
        });
      } else {
        if (!editingItemId) {
          throw new Error('編集対象のIDがありません。');
        }
        await updateMealItem(editingItemId, {
          date,
          meal_type: dialogMealType,
          meal_index: dialogMealType === 'main' ? dialogMealIndex : null,
          name: values.name,
          amount_value: amountValue,
          amount_unit: amountUnit,
          serving_count: servingCount,
          note,
        });
      }

      setDialogOpen(false);
      refresh();
    } catch (e: any) {
      console.error('Failed to save meal item', e);
      setDialogError(
        e?.message ?? '食事の保存に失敗しました。入力内容を確認してください。'
      );
    } finally {
      setDialogSubmitting(false);
    }
  };

  const handleDeleteItem = async (entryId: string) => {
    if (!confirm('この記録を削除しますか？')) return;
    try {
      await deleteMealItem(entryId);
      refresh();
    } catch (e) {
      console.error('Failed to delete meal item', e);
      alert('削除に失敗しました。時間をおいて再度お試しください。');
    }
  };

  if (isLoading) {
    return <p className="text-sm text-slate-400">読み込み中...</p>;
  }

  if (error || !data) {
    return (
      <div className="space-y-2">
        <p className="text-sm text-rose-400">食事記録の取得に失敗しました。</p>
        <button
          className="text-xs text-emerald-400 underline"
          onClick={() => location.reload()}
        >
          再読み込み
        </button>
      </div>
    );
  }

  const { mealsPerDay, mainSlots, snacks } = data;

  return (
    <>
      <MealsHeader
        date={date}
        onChangeDate={changeDate}
        onBackToToday={backToToday}
      />
      <div className="mt-4 grid gap-4 md:grid-cols-[2fr,1fr]">
        <MainMealsSection
          mealsPerDay={mealsPerDay}
          slots={mainSlots}
          onAddItem={(mealIndex) => openCreateDialog('main', mealIndex)}
          onEditItem={openEditDialog}
          onDeleteItem={handleDeleteItem}
        />
        <SnackMealsSection
          items={snacks}
          onAddItem={() => openCreateDialog('snack', null)}
          onEditItem={openEditDialog}
          onDeleteItem={handleDeleteItem}
        />
      </div>

      <MealItemDialog
        open={dialogOpen}
        mode={dialogMode}
        mealType={dialogMealType}
        mealIndex={dialogMealIndex}
        initialValues={initialFormValues}
        onOpenChange={setDialogOpen}
        onSubmit={handleSubmitDialog}
        isSubmitting={dialogSubmitting}
        errorMessage={dialogError}
      />
    </>
  );
}
