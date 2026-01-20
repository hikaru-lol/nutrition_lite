// src/app/(onboarding)/target/layout.tsx
import { redirect } from 'next/navigation';
import { fetchCurrentUserServer } from '@/modules/auth';

export default async function OnboardingTargetLayout(props: {
  children: React.ReactNode;
}) {
  const { user } = await fetchCurrentUserServer();

  if (!user.has_profile) redirect('/onboarding/profile');
  // targetは未作成でもOK（ここで作るため）
  return <>{props.children}</>;
}
