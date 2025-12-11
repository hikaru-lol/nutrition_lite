// frontend/components/layout/NavLink.tsx
'use client';

import Link from 'next/link';
import { cn } from '@/lib/utils';

type NavLinkProps = {
  href: string;
  label: string;
  icon?: React.ReactNode;
  isActive?: boolean;
};

export function NavLink({ href, label, icon, isActive }: NavLinkProps) {
  return (
    <Link
      href={href}
      className={cn(
        'flex items-center gap-2 rounded-xl px-3 py-2 text-sm transition-colors',
        'text-slate-300 hover:bg-slate-800 hover:text-slate-50',
        isActive && 'bg-slate-800 text-emerald-400'
      )}
    >
      {icon && <span className="text-base">{icon}</span>}
      <span>{label}</span>
    </Link>
  );
}
