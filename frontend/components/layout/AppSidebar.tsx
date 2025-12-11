// frontend/components/layout/AppSidebar.tsx
'use client';

import { usePathname } from 'next/navigation';
import { NavLink } from './NavLink';

export function AppSidebar() {
  const pathname = usePathname();

  const links = [
    { href: '/', label: 'Today' },
    { href: '/meals', label: 'Meals' },
    {
      href: '/reports/daily/' + new Date().toISOString().slice(0, 10),
      label: 'Daily Report',
    },
    { href: '/targets', label: 'Targets' },
    { href: '/recommendations/today', label: 'Recommendations' },
    { href: '/billing/plan', label: 'Billing' },
    { href: '/profile', label: 'Profile' },
  ];

  return (
    <aside className="hidden md:block w-56 border-r border-slate-800 px-3 py-6">
      <nav className="space-y-1">
        {links.map((link) => (
          <NavLink
            key={link.href}
            href={link.href}
            label={link.label}
            isActive={
              pathname === link.href || pathname.startsWith(link.href + '/')
            }
          />
        ))}
      </nav>
    </aside>
  );
}
