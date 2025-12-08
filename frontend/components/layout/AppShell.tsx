// frontend/components/layout/AppShell.tsx
'use client';

import type { ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { AppHeader } from './AppHeader';
import { AppSidebar } from './AppSidebar';
import { useCurrentUser } from '@/lib/hooks/useCurrentUser';

type AppShellProps = {
  children: ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  const router = useRouter();
  const { user, isLoading } = useCurrentUser();

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/auth/login');
    }
  }, [isLoading, user, router]);

  if (isLoading || !user) {
    // ローディング or リダイレクト待ち
    return (
      <div className="min-h-screen bg-slate-950 text-slate-50 flex items-center justify-center">
        <p className="text-sm text-slate-400">読み込み中...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50">
      <AppHeader
        userName={user.name ?? user.email}
        plan={user.plan}
        trialEndsAt={user.trialEndsAt}
        // onLogout は後で
      />
      <div className="flex">
        <AppSidebar />
        <main className="flex-1 px-4 py-6 md:px-8 md:py-8">{children}</main>
      </div>
    </div>
  );
}
