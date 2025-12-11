// components/reports/ReportSection.tsx
import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';

type ReportSectionVariant = 'good' | 'improvement' | 'focus';

type ReportSectionProps = {
  title: string;
  items: string[];
  variant?: ReportSectionVariant;
  icon?: ReactNode;
};

export function ReportSection({
  title,
  items,
  variant = 'good',
  icon,
}: ReportSectionProps) {
  const accentClass =
    variant === 'good'
      ? 'text-emerald-400'
      : variant === 'improvement'
      ? 'text-amber-400'
      : 'text-sky-400';

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-3 md:p-4">
      <div className="mb-2 flex items-center gap-2">
        {icon && <span className={cn('text-xs', accentClass)}>{icon}</span>}
        <p className={cn('text-xs font-semibold', accentClass)}>{title}</p>
      </div>
      {items.length === 0 ? (
        <p className="text-xs text-slate-500">特になし</p>
      ) : (
        <ul className="space-y-1">
          {items.map((item, idx) => (
            <li key={idx} className="text-xs text-slate-200 leading-relaxed">
              ・{item}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
