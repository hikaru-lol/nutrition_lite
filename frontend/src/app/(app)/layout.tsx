// src/app/(app)/layout.tsx
import { redirect } from 'next/navigation';
import { fetchCurrentUserServer } from '@/modules/auth/server';
import { AppLayout } from '@/shared/ui/layout/AppLayout';
import { TutorialProvider } from '@/modules/tutorial';

// TODO: 認証・プロファイル・ターゲットのガードを実装する

export default async function Layout({ children }: { children: React.ReactNode }) {
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

  return (
    <TutorialProvider>
      <AppLayout user={user} showSidebar={true}>
        {children}
      </AppLayout>
    </TutorialProvider>
  );
}
