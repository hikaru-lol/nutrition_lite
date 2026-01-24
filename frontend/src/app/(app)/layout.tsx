// src/app/(app)/layout.tsx
import 'server-only';
import { redirect } from 'next/navigation';
import { fetchCurrentUserServer } from '@/modules/auth/server';
import { fetchProfileServer } from '@/modules/profile/server';
import { fetchActiveTargetServer } from '@/modules/targets/server';

export default async function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  try {
    await fetchCurrentUserServer();
  } catch {
    redirect('/auth/login');
  }

  const profile = await fetchProfileServer().catch(() => null);
  if (!profile) redirect('/profile');

  const activeTarget = await fetchActiveTargetServer().catch(() => null);
  if (!activeTarget) redirect('/target');

  return <>{children}</>;
}
