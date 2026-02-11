// src/app/(onboarding)/layout.tsx
import { redirect } from 'next/navigation';
import { fetchCurrentUserServer } from '@/modules/auth/server';
import { AppLayout } from '@/shared/ui/layout/AppLayout';
import { TutorialProvider } from '@/modules/tutorial';

export default async function OnboardingLayout(props: {
  children: React.ReactNode;
}) {
  let user = null;

  try {
    const currentUser = await fetchCurrentUserServer();
    user = {
      name: currentUser?.name || 'ユーザー',
      email: currentUser?.email || '',
    };
  } catch {
    // 認証失敗の場合はログインページにリダイレクト
    redirect('/auth/login');
  }

  // オンボーディング用の軽量レイアウト（サイドバーなし）
  return (
    <TutorialProvider>
      <AppLayout user={user} showSidebar={false}>
        <div className="max-w-2xl mx-auto">
          {props.children}
        </div>
      </AppLayout>
    </TutorialProvider>
  );
}
