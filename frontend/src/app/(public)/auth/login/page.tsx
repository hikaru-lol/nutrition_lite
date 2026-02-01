'use client';

import { useRouter } from 'next/navigation';
import { LoginForm } from '@/modules/auth/ui/LoginForm';
import { fetchProfile } from '@/modules/profile/api/profileClient';

export default function LoginPage() {
  const router = useRouter();

  const handleLoginSuccess = async () => {
    try {
      // プロフィールの存在を確認
      const profile = await fetchProfile();

      if (profile) {
        // プロフィールが既に存在する場合は今日のページへ
        router.replace('/today');
      } else {
        // プロフィールが未設定の場合はプロフィール設定へ
        router.replace('/profile');
      }
    } catch (error) {
      // エラーの場合はとりあえずプロフィールページへ（安全側に倒す）
      console.error('Profile check failed:', error);
      router.replace('/profile');
    }
  };

  return (
    <div className="min-h-screen grid place-items-center p-6">
      <LoginForm onSuccess={handleLoginSuccess} />
    </div>
  );
}
