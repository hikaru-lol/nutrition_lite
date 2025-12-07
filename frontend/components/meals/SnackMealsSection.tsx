// components/meals/SnackMealsSection.tsx
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import type { MealItemVM } from '@/lib/hooks/useMealsByDate';
import { MealItemList } from './MealItemList';

type SnackMealsSectionProps = {
  items: MealItemVM[];
  onAddItem: () => void;
  onEditItem: (id: string) => void;
  onDeleteItem: (id: string) => void;
};

export function SnackMealsSection({
  items,
  onAddItem,
  onEditItem,
  onDeleteItem,
}: SnackMealsSectionProps) {
  return (
    <Card>
      <div className="mb-2 flex items-center justify-between">
        <p className="text-xs text-slate-400">間食</p>
        <Button size="sm" variant="secondary" onClick={onAddItem}>
          間食を追加
        </Button>
      </div>
      {items.length === 0 ? (
        <p className="text-xs text-slate-500">間食はまだ記録されていません。</p>
      ) : (
        <MealItemList
          items={items}
          onEditClick={onEditItem}
          onDeleteClick={onDeleteItem}
        />
      )}
    </Card>
  );
}
