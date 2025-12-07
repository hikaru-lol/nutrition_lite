// components/meals/MealSlotCard.tsx
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import type { MealItemVM } from '@/lib/hooks/useMealsByDate';
import { MealItemList } from './MealItemList';

type MealSlotCardProps = {
  mealIndex: number;
  items: MealItemVM[];
  onAddClick: () => void;
  onEditClick: (id: string) => void;
  onDeleteClick: (id: string) => void;
};

export function MealSlotCard({
  mealIndex,
  items,
  onAddClick,
  onEditClick,
  onDeleteClick,
}: MealSlotCardProps) {
  return (
    <Card>
      <div className="mb-2 flex items-center justify-between">
        <div>
          <p className="text-xs text-slate-400">{mealIndex} 回目の食事</p>
        </div>
        <Button size="sm" variant="secondary" onClick={onAddClick}>
          食品を追加
        </Button>
      </div>

      {items.length === 0 ? (
        <p className="text-xs text-slate-500">
          まだこの食事は記録されていません。
        </p>
      ) : (
        <MealItemList
          items={items}
          onEditClick={onEditClick}
          onDeleteClick={onDeleteClick}
        />
      )}
    </Card>
  );
}
