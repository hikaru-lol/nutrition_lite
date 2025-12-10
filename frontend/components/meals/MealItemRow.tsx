// frontend/components/meals/MealItemRow.tsx
'use client';

import type { MealItemVM } from '@/lib/hooks/useMealsByDate';
import { cn } from '@/lib/utils';

type MealItemRowProps = {
  item: MealItemVM;
  onEdit: () => void;
  onDelete: () => void;
};

export function MealItemRow({ item, onEdit, onDelete }: MealItemRowProps) {
  return (
    <li
      className={cn(
        'flex items-center justify-between rounded-xl border border-slate-800',
        'bg-slate-900/80 px-3 py-2 text-xs'
      )}
    >
      <div className="flex-1 min-width-0">
        <p className="text-slate-100 truncate">{item.name}</p>
        {item.amountText && (
          <p className="text-[11px] text-slate-400">{item.amountText}</p>
        )}
        {item.note && (
          <p className="mt-0.5 text-[11px] text-slate-500 line-clamp-2">
            {item.note}
          </p>
        )}
      </div>
      <div className="ml-3 flex items-center gap-2">
        <button
          type="button"
          className="text-[11px] text-slate-400 hover:text-slate-50"
          onClick={onEdit}
        >
          編集
        </button>
        <button
          type="button"
          className="text-[11px] text-rose-400 hover:text-rose-300"
          onClick={onDelete}
        >
          削除
        </button>
      </div>
    </li>
  );
}
