// frontend/components/ui/label.tsx
import * as React from 'react';
import { cn } from '@/shared/lib/utils';

export type LabelProps = React.LabelHTMLAttributes<HTMLLabelElement>;

export function Label({ className, ...props }: LabelProps) {
  return (
    <label
      className={cn('block text-xs font-medium text-slate-300 mb-1', className)}
      {...props}
    />
  );
}
