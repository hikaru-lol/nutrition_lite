// frontend/components/layout/PageHeader.tsx
import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';

type PageHeaderProps = {
  title: string;
  description?: string;
  actions?: ReactNode;
  className?: string;
};

export function PageHeader({
  title,
  description,
  actions,
  className,
}: PageHeaderProps) {
  return (
    <div
      className={cn(
        'mb-4 flex flex-col gap-2 md:mb-6 md:flex-row md:items-center md:justify-between',
        className
      )}
    >
      <div>
        <h1 className="text-xl md:text-2xl font-semibold text-slate-50">
          {title}
        </h1>
        {description && (
          <p className="mt-1 text-xs md:text-sm text-slate-400">
            {description}
          </p>
        )}
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  );
}
