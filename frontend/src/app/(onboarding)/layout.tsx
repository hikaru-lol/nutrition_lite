// src/app/(onboarding)/layout.tsx
import { redirect } from 'next/navigation';
import { fetchCurrentUserServer } from '@/modules/auth/server';

export default async function OnboardingLayout(props: {
  children: React.ReactNode;
}) {
  const ok = await fetchCurrentUserServer()
    .then(() => true)
    .catch(() => false);

  if (!ok) redirect('/auth/login');
  return <>{props.children}</>;
}
