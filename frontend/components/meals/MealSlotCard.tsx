// frontend/components/meals/MealSlotCard.tsx
'use client';

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import type { MealItemVM } from '@/lib/hooks/useMealsByDate';
import type { MealNutritionSummaryApi } from '@/lib/api/nutrition';
import { MealItemList } from '@/components/meals/MealItemList';

type MealSlotCardProps = {
  mealIndex: number;
  items: MealItemVM[];
  onAddClick: () => void;
  onEditClick: (id: string) => void;
  onDeleteClick: (id: string) => void;
  nutrition?: MealNutritionSummaryApi;
  onRecomputeNutrition: () => void;
  isNutritionLoading?: boolean;
};

export function MealSlotCard({
  mealIndex,
  items,
  onAddClick,
  onEditClick,
  onDeleteClick,
  nutrition,
  onRecomputeNutrition,
  isLoading = false,
  isNutritionLoading = false,
}: MealSlotCardProps & { isLoading?: boolean }) {
  const hasItems = items.length > 0;

  const loading = isLoading ?? isNutritionLoading;

  return (
    <Card>
      <div className="mb-2 flex items-center justify-between gap-2">
        <div>
          <p className="text-xs text-slate-400">{mealIndex} 回目の食事</p>
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
          <Button size="sm" variant="secondary" onClick={onAddClick}>
            食品を追加
          </Button>
        </div>
      </div>

      {hasItems ? (
        <MealItemList
          items={items}
          onEditClick={onEditClick}
          onDeleteClick={onDeleteClick}
        />
      ) : (
        <p className="text-xs text-slate-500">
          まだこの食事は記録されていません。
        </p>
      )}
    </Card>
  );
}
