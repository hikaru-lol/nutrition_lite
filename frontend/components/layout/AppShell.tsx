'use client';

import type { ReactNode } from 'react';
import { AppHeader } from './AppHeader';
import { AppSidebar } from './AppSidebar';
// 仮の useCurrentUser フック（実装は別途）
import { useCurrentUser } from '@/lib/hooks/useCurrentUser';

type AppShellProps = {
  children: ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  const { user, isLoading } = useCurrentUser();

  // ローディング中は簡易スケルトンでOK
  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-50 flex items-center justify-center">
        <p className="text-sm text-slate-400">読み込み中...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50">
      <AppHeader
        appName="Nutrition Lite"
        userName={user?.name}
        plan={user?.plan}
        trialEndsAt={user?.trialEndsAt ?? null}
        // onLogout はあとで実装
      />
      <div className="flex">
        <AppSidebar />
        <main className="flex-1 px-4 py-6 md:px-8 md:py-8">{children}</main>
      </div>
    </div>
  );
}
