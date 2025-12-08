// frontend/app/(public)/auth/login/page.tsx
'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { AuthCard } from '@/components/auth/AuthCard';
import { LoginForm, type LoginFormValues } from '@/components/auth/LoginForm';
import { login } from '@/lib/api/auth';
import { ApiError } from '@/lib/api/client';

export default function LoginPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);

  const handleSubmit = async (values: LoginFormValues) => {
    try {
      setIsSubmitting(true);
      setServerError(null);

      const user = await login(values.email, values.password);

      if (!user.hasProfile) {
        router.push('/onboarding/profile');
      } else {
        router.push('/');
      }
    } catch (e: any) {
      if (e instanceof ApiError && e.status === 401) {
        setServerError('メールアドレスかパスワードが正しくありません。');
      } else {
        setServerError(
          e?.message ??
            'ログインに失敗しました。時間をおいて再度お試しください。'
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AuthCard
      title="ログイン"
      description="メールアドレスとパスワードを入力して、続けてください。"
      footer={
        <p>
          アカウントをお持ちでない方は{' '}
          <Link
            href="/auth/register"
            className="text-emerald-400 hover:underline"
          >
            こちらから登録
          </Link>
          できます。
        </p>
      }
    >
      <LoginForm
        onSubmit={handleSubmit}
        isSubmitting={isSubmitting}
        serverError={serverError}
      />
    </AuthCard>
  );
}
