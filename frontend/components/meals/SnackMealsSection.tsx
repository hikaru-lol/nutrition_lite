// frontend/components/meals/SnackMealsSection.tsx
'use client';

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import type { MealItemVM } from '@/lib/hooks/useMealsByDate';
import type { MealNutritionSummaryApi } from '@/lib/api/nutrition';
import { MealItemList } from './MealItemList';

type SnackMealsSectionProps = {
  items: MealItemVM[];
  onAddItem: () => void;
  onEditItem: (id: string) => void;
  onDeleteItem: (id: string) => void;
  onRecomputeNutrition: () => void;
  nutrition?: MealNutritionSummaryApi;
  nutritionLoadingKey?: string | null;
};

export function SnackMealsSection({
  items,
  onAddItem,
  onEditItem,
  onDeleteItem,
  onRecomputeNutrition,
  nutrition,
  nutritionLoadingKey,
}: SnackMealsSectionProps) {
  const hasItems = items.length > 0;
  const loading = nutritionLoadingKey === 'snack-null';

  return (
    <Card>
      <div className="mb-2 flex items-center justify-between">
        <div>
          <p className="text-xs text-slate-400">間食</p>
          {nutrition && (
            <p className="mt-1 text-[11px] text-slate-300">
              {nutrition.nutrients
                .slice(0, 3)
                .map((n) => `${n.code}: ${n.amount}${n.unit}`)
                .join(' / ')}
            </p>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={onRecomputeNutrition}
            disabled={!hasItems || loading}
          >
            {loading ? '計算中...' : '栄養を計算'}
          </Button>
          <Button size="sm" variant="secondary" onClick={onAddItem}>
            間食を追加
          </Button>
        </div>
      </div>

      {hasItems ? (
        <MealItemList
          items={items}
          onEditClick={onEditItem}
          onDeleteClick={onDeleteItem}
        />
      ) : (
        <p className="text-xs text-slate-500">間食はまだ記録されていません。</p>
      )}
    </Card>
  );
}
