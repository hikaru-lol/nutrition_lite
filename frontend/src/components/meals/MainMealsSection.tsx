// frontend/components/meals/MainMealsSection.tsx
'use client';

import type { MealSlot } from '@/lib/hooks/useMealsByDate';
import type { MealNutritionSummaryApi } from '@/lib/api/nutrition';
import { MealSlotCard } from './MealSlotCard';

type MainMealsSectionProps = {
  mealsPerDay: number;
  slots: MealSlot[];
  onAddItem: (mealIndex: number) => void;
  onEditItem: (entryId: string) => void;
  onDeleteItem: (entryId: string) => void;
  onRecomputeNutrition: (mealIndex: number) => void;
  getNutrition: (mealIndex: number) => MealNutritionSummaryApi | undefined;
  nutritionLoadingKey?: string | null;
  date: string;
};

export function MainMealsSection({
  mealsPerDay,
  slots,
  onAddItem,
  onEditItem,
  onDeleteItem,
  onRecomputeNutrition,
  getNutrition,
  nutritionLoadingKey,
  date,
}: MainMealsSectionProps) {
  const slotMap = new Map<number, MealSlot['items']>();
  slots.forEach((s) => {
    slotMap.set(s.mealIndex, s.items);
  });

  const indices = Array.from({ length: mealsPerDay }, (_, i) => i + 1);

  return (
    <div className="space-y-3">
      {indices.map((index) => {
        const nutritionKey = `main-${index}-${date}`;
        return (
          <MealSlotCard
            key={index}
            mealIndex={index}
            items={slotMap.get(index) ?? []}
            onAddClick={() => onAddItem(index)}
            onEditClick={onEditItem}
            onDeleteClick={onDeleteItem}
            nutrition={getNutrition(index)}
            onRecomputeNutrition={() => onRecomputeNutrition(index)}
            isNutritionLoading={nutritionLoadingKey === nutritionKey}
          />
        );
      })}
    </div>
  );
}
