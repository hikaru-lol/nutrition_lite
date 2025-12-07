import type { ReactNode } from 'react';
import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';

type AuthCardProps = {
  title: string;
  description?: string;
  children: ReactNode;
  footer?: ReactNode;
  className?: string;
};

export function AuthCard({
  title,
  description,
  children,
  footer,
  className,
}: AuthCardProps) {
  return (
    <Card className={cn('w-full max-w-md mx-auto', className)}>
      <div className="mb-4">
        <h1 className="text-lg md:text-xl font-semibold text-slate-50">
          {title}
        </h1>
        {description && (
          <p className="mt-1 text-xs md:text-sm text-slate-400">
            {description}
          </p>
        )}
      </div>
      <div className="space-y-4">{children}</div>
      {footer && (
        <div className="mt-6 border-t border-slate-800 pt-3 text-xs text-slate-400">
          {footer}
        </div>
      )}
    </Card>
  );
}
