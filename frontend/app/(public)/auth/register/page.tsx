// frontend/app/(public)/auth/register/page.tsx
'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { AuthCard } from '@/components/auth/AuthCard';
import {
  RegisterForm,
  type RegisterFormValues,
} from '@/components/auth/RegisterForm';
import { register } from '@/lib/api/auth';
import { ApiError } from '@/lib/api/client';

export default function RegisterPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);

  const handleSubmit = async (values: RegisterFormValues) => {
    try {
      setIsSubmitting(true);
      setServerError(null);

      const user = await register(
        values.name || null,
        values.email,
        values.password
      );

      if (!user.hasProfile) {
        router.push('/onboarding/profile');
      } else {
        router.push('/');
      }
    } catch (e: any) {
      if (e instanceof ApiError && e.status === 409) {
        setServerError('このメールアドレスは既に登録されています。');
      } else {
        setServerError(
          e?.message ?? '登録に失敗しました。時間をおいて再度お試しください。'
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AuthCard
      title="アカウント作成"
      description="まずはアカウントを作成して、7日間のトライアルを開始しましょう。"
      footer={
        <p>
          すでにアカウントをお持ちの方は{' '}
          <Link href="/auth/login" className="text-emerald-400 hover:underline">
            ログイン
          </Link>
          してください。
        </p>
      }
    >
      <RegisterForm
        onSubmit={handleSubmit}
        isSubmitting={isSubmitting}
        serverError={serverError}
      />
    </AuthCard>
  );
}
