// components/meals/MainMealsSection.tsx
import type { MealSlot } from '@/lib/hooks/useMealsByDate';
import { MealSlotCard } from './MealSlotCard';

type MainMealsSectionProps = {
  mealsPerDay: number;
  slots: MealSlot[];
  onAddItem: (mealIndex: number) => void;
  onEditItem: (entryId: string) => void;
  onDeleteItem: (entryId: string) => void;
};

export function MainMealsSection({
  mealsPerDay,
  slots,
  onAddItem,
  onEditItem,
  onDeleteItem,
}: MainMealsSectionProps) {
  // slots にない mealIndex も空Cardを出したい場合は補完して表示しても良い
  const slotMap = new Map(slots.map((s) => [s.mealIndex, s.items]));
  const indices = Array.from({ length: mealsPerDay }, (_, i) => i + 1);

  return (
    <div className="space-y-3">
      {indices.map((index) => (
        <MealSlotCard
          key={index}
          mealIndex={index}
          items={slotMap.get(index) ?? []}
          onAddClick={() => onAddItem(index)}
          onEditClick={onEditItem}
          onDeleteClick={onDeleteItem}
        />
      ))}
    </div>
  );
}
