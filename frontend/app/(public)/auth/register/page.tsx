'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { AuthCard } from '@/components/auth/AuthCard';
import {
  RegisterForm,
  type RegisterFormValues,
} from '@/components/auth/RegisterForm';
// import { register, fetchMe } from "@/lib/api/auth"; // 実装予定

export default function RegisterPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);

  const handleSubmit = async (values: RegisterFormValues) => {
    try {
      setIsSubmitting(true);
      setServerError(null);

      // TODO: 実際のAPI呼び出しに差し替え
      // await register(values.name, values.email, values.password);
      // const me = await fetchMe();
      // if (!me.hasProfile) {
      //   router.push("/onboarding/profile");
      // } else {
      //   router.push("/");
      // }

      router.push('/onboarding/profile');
    } catch (e: any) {
      setServerError(
        e?.message ?? '登録に失敗しました。時間をおいて再度お試しください。'
      );
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
