// frontend/components/ui/card.tsx
import * as React from 'react';
import { cn } from '@/lib/utils';

export type CardProps = React.HTMLAttributes<HTMLDivElement>;

export function Card({ className, ...props }: CardProps) {
  return (
    <div
      className={cn(
        'rounded-2xl border border-slate-800 bg-slate-900/60 p-4 md:p-5 shadow-lg shadow-slate-950/40',
        className
      )}
      {...props}
    />
  );
}
