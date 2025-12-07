'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { useState } from 'react';
import { MealsHeader } from './MealsHeader';
import { MainMealsSection } from './MainMealsSection';
import { SnackMealsSection } from './SnackMealsSection';
import { MealItemDialog, type MealItemFormValues } from './MealItemDialog';
import { useMealsByDate } from '@/lib/hooks/useMealsByDate';

export function MealsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const paramDate = searchParams.get('date');
  const today = new Date().toISOString().slice(0, 10);
  const date = paramDate ?? today;

  const { data, isLoading, error } = useMealsByDate(date);

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
      amountValue: '', // TODO: parse amountText から復元するなら
      amountUnit: '',
      servingCount: '',
      note: item.note ?? '',
    });
    setDialogOpen(true);
  };

  const handleSubmitDialog = async (values: MealItemFormValues) => {
    // TODO: 実際の API 呼び出し:
    // if (dialogMode === "create") { POST /meal-items }
    // if (dialogMode === "edit") { PATCH /meal-items/{editingItemId} }
    // その後 useMealsByDate の再フェッチ
    setDialogOpen(false);
  };

  const handleDeleteItem = async (entryId: string) => {
    // TODO: DELETE /meal-items/{entryId} → 再フェッチ
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
      />
    </>
  );
}
