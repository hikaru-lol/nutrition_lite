// frontend/components/meals/MealItemList.tsx
'use client';

import type { MealItemVM } from '@/lib/hooks/useMealsByDate';
import { MealItemRow } from './MealItemRow';

type MealItemListProps = {
  items: MealItemVM[];
  onEditClick: (id: string) => void;
  onDeleteClick: (id: string) => void;
};

export function MealItemList({
  items,
  onEditClick,
  onDeleteClick,
}: MealItemListProps) {
  return (
    <ul className="space-y-1">
      {items.map((item) => (
        <MealItemRow
          key={item.id}
          item={item}
          onEdit={() => onEditClick(item.id)}
          onDelete={() => onDeleteClick(item.id)}
        />
      ))}
    </ul>
  );
}
