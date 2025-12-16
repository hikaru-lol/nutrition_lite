// frontend/components/meals/MealsPage.tsx
'use client';

// next.js components
import { useRouter, useSearchParams } from 'next/navigation';

// hooks
import { useState } from 'react';

// ui components
import { PageHeader } from '@/components/layout/PageHeader';
import { Card } from '@/components/ui/card';

// lib
import { useMealsByDate, type MealSlot } from '@/lib/hooks/useMealsByDate';
import {
  recomputeMealAndDailyNutrition,
  type MealNutritionSummaryApi,
  type DailyNutritionSummaryApi,
} from '@/lib/api/nutrition';

// domain components
import { MealItemDialog, type MealItemFormValues } from './MealItemDialog';
import { MainMealsSection } from './MainMealsSection';
import { SnackMealsSection } from './SnackMealsSection';
import { MealNutritionChart } from './MealNutritionChart';

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

  const [mealNutritions, setMealNutritions] = useState<
    Record<string, MealNutritionSummaryApi>
  >({});
  const [dailyNutrition, setDailyNutrition] =
    useState<DailyNutritionSummaryApi | null>(null);
  const [nutritionLoadingKey, setNutritionLoadingKey] = useState<string | null>(
    null
  );
  const [nutritionError, setNutritionError] = useState<string | null>(null);

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
      ...data.mainSlots.flatMap((s: MealSlot) => s.items),
      ...data.snacks,
    ];
    const item = allItems.find((i) => i.id === entryId);
    if (!item) return;

    setDialogMode('edit');
    setDialogMealType(item.mealType);
    setDialogMealIndex(item.mealIndex ?? null);
    setEditingItemId(entryId);
    setInitialFormValues({
      name: item.name,
      amountValue: '', // amountText から復元するならここでパース
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
        // createMealItem は lib/api/meals.ts から import して使う想定
        const { createMealItem } = await import('@/lib/api/meals');
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
        const { updateMealItem } = await import('@/lib/api/meals');
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
    } catch (e: unknown) {
      console.error('Failed to save meal item', e);
      const message =
        e instanceof Error
          ? e.message
          : '食事の保存に失敗しました。入力内容を確認してください。';
      setDialogError(message);
    } finally {
      setDialogSubmitting(false);
    }
  };

  const handleDeleteItem = async (entryId: string) => {
    const ok = window.confirm('この記録を削除しますか？');
    if (!ok) return;

    try {
      const { deleteMealItem } = await import('@/lib/api/meals');
      await deleteMealItem(entryId);
      refresh();
    } catch (e) {
      console.error('Failed to delete meal item', e);
      window.alert('削除に失敗しました。時間をおいて再度お試しください。');
    }
  };

  const handleRecomputeMealNutrition = async (
    mealType: 'main' | 'snack',
    mealIndex?: number | null
  ) => {
    const key = `${mealType}-${mealIndex ?? 'snack'}-${date}`;
    try {
      setNutritionLoadingKey(key);
      setNutritionError(null);

      const res = await recomputeMealAndDailyNutrition({
        date,
        mealType,
        mealIndex: mealType === 'main' ? mealIndex ?? undefined : undefined,
      });

      setMealNutritions((prev) => ({
        ...prev,
        [key]: res.meal,
      }));
      setDailyNutrition(res.daily);
    } catch (e: unknown) {
      console.error('Failed to recompute meal nutrition', e);
      const message =
        e instanceof Error
          ? e.message
          : '栄養情報の計算に失敗しました。時間をおいて再度お試しください。';
      setNutritionError(message);
    } finally {
      setNutritionLoadingKey(null);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <PageHeader title="食事記録" />
        <p className="text-sm text-slate-400">読み込み中...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="space-y-2">
        <PageHeader title="食事記録" />
        <p className="text-sm text-rose-400">食事記録の取得に失敗しました。</p>
        <button
          className="text-xs text-emerald-400 underline"
          onClick={() => window.location.reload()}
        >
          再読み込み
        </button>
      </div>
    );
  }

  const { mealsPerDay, mainSlots, snacks } = data;

  return (
    <>
      <PageHeader
        title={`${formatDateJP(new Date(date))} の食事記録`}
        description="1日の食事内容を記録・編集し、必要に応じて栄養サマリを確認できます。"
      />

      {nutritionError && (
        <p className="mb-2 text-xs text-rose-400 bg-rose-500/10 border border-rose-500/40 rounded-lg px-3 py-2">
          {nutritionError}
        </p>
      )}

      {dailyNutrition && (
        <Card className="mb  -4">
          <p className="text-sm font-semibold text-slate-50 mb-2">
            この日の栄養サマリ（モック）
          </p>
          <p className="text-xs text-slate-400">
            各ミールの「栄養を計算」を実行すると、この日の総合的な栄養サマリが更新されます。
          </p>
          <MealNutritionChart
            nutrients={dailyNutrition.nutrients}
            title="1日トータル（代表的な栄養素）"
          />
        </Card>
      )}

      <div className="mt-4 grid gap-4 md:grid-cols-[2fr,1fr]">
        <MainMealsSection
          mealsPerDay={mealsPerDay}
          slots={mainSlots}
          onAddItem={(mealIndex) => openCreateDialog('main', mealIndex)}
          onEditItem={openEditDialog}
          onDeleteItem={handleDeleteItem}
          onRecomputeNutrition={(mealIndex) =>
            handleRecomputeMealNutrition('main', mealIndex)
          }
          getNutrition={(mealIndex) =>
            mealNutritions[`main-${mealIndex}-${date}`]
          }
          nutritionLoadingKey={nutritionLoadingKey}
          date={date}
        />
        <SnackMealsSection
          items={snacks}
          onAddItem={() => openCreateDialog('snack', null)}
          onEditItem={openEditDialog}
          onDeleteItem={handleDeleteItem}
          onRecomputeNutrition={() =>
            handleRecomputeMealNutrition('snack', null)
          }
          nutrition={mealNutritions[`snack-null-${date}`]}
          nutritionLoadingKey={nutritionLoadingKey}
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

function formatDateJP(date: Date) {
  const y = date.getFullYear();
  const m = date.getMonth() + 1;
  const d = date.getDate();
  const w = ['日', '月', '火', '水', '木', '金', '土'][date.getDay()];
  return `${y}年${m}月${d}日(${w})`;
}
