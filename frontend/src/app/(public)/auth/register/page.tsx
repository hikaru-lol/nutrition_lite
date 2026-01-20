// frontend/app/(public)/auth/register/page.tsx
// 'use client';

// import Link from 'next/link';
// import { useRouter } from 'next/navigation';
// import { useState } from 'react';
// import { AuthCard } from '@/components/auth/AuthCard';
// import {
//   RegisterForm,
//   type RegisterFormValues,
// } from '@/components/auth/RegisterForm';
// import { register } from '@/lib/api/auth';
// import { ApiError } from '@/lib/api/client';

// export default function RegisterPage() {
//   const router = useRouter();
//   const [isSubmitting, setIsSubmitting] = useState(false);
//   const [serverError, setServerError] = useState<string | null>(null);

//   const handleSubmit = async (values: RegisterFormValues) => {
//     try {
//       setIsSubmitting(true);
//       setServerError(null);

//       const user = await register(
//         values.name || null,
//         values.email,
//         values.password
//       );

//       if (!user.hasProfile) {
//         router.push('/onboarding/profile');
//       } else {
//         router.push('/');
//       }
//     } catch (e: unknown) {
//       if (e instanceof ApiError && e.status === 409) {
//         setServerError('このメールアドレスは既に登録されています。');
//       } else {
//         const message =
//           e instanceof Error
//             ? e.message
//             : '登録に失敗しました。時間をおいて再度お試しください。';
//         setServerError(message);
//       }
//     } finally {
//       setIsSubmitting(false);
//     }
//   };

//   return (
//     <AuthCard
//       title="アカウント作成"
//       description="まずはアカウントを作成して、7日間のトライアルを開始しましょう。"
//       footer={
//         <p>
//           すでにアカウントをお持ちの方は{' '}
//           <Link href="/auth/login" className="text-emerald-400 hover:underline">
//             ログイン
//           </Link>
//           してください。
//         </p>
//       }
//     >
//       <RegisterForm
//         onSubmit={handleSubmit}
//         isSubmitting={isSubmitting}
//         serverError={serverError}
//       />
//     </AuthCard>
//   );
// }

import { RegisterForm } from '@/modules/auth/ui/RegisterForm';
import Link from 'next/link';
import { Activity } from 'lucide-react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/shared/ui/card';

export default function RegisterPage() {
  return (
    // 修正点: 外側の div (min-h-screen, bg-gray-50) を削除。
    // AuthLayout がすでにそれらを提供しているため、ここは中身だけでOKです。
    <div className="w-full max-w-[400px] mx-auto space-y-6">
      {/* ロゴ・ブランディング部分 */}
      <div className="flex flex-col items-center space-y-2 text-center">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <Activity className="h-6 w-6" />
        </div>
        <h1 className="text-xl font-bold tracking-tight text-gray-900">
          Health Manager
        </h1>
      </div>

      {/* メインカード */}
      <Card className="border border-gray-100 shadow-md backdrop-blur-sm bg-white/80">
        <CardHeader className="space-y-1 pb-6">
          <CardTitle className="text-2xl font-bold tracking-tight text-center text-gray-900">
            アカウント作成
          </CardTitle>
          <CardDescription className="text-center text-gray-500">
            あなたの健康管理を、ここから始めましょう
          </CardDescription>
        </CardHeader>
        <CardContent>
          <RegisterForm />

          {/* フッターリンクエリア */}
          <div className="mt-6 flex flex-col items-center gap-2 text-center text-sm">
            <span className="text-gray-500">
              すでにアカウントをお持ちですか？
            </span>
            <Link
              href="/auth/login"
              className="font-medium text-primary underline-offset-4 hover:underline transition-all"
            >
              ログインして管理画面へ
            </Link>
          </div>
        </CardContent>
      </Card>

      {/* 利用規約などの補足リンク */}
      <p className="px-8 text-center text-xs text-gray-500">
        アカウントを作成することで、
        <Link
          href="/terms"
          className="underline underline-offset-4 hover:text-primary text-gray-700"
        >
          利用規約
        </Link>{' '}
        および{' '}
        <Link
          href="/privacy"
          className="underline underline-offset-4 hover:text-primary text-gray-700"
        >
          プライバシーポリシー
        </Link>{' '}
        に同意したものとみなされます。
      </p>
    </div>
  );
}
