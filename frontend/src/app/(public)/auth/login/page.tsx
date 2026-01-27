'use client';

import { useRouter } from 'next/navigation';
import { LoginForm } from '@/modules/auth/ui/LoginForm';

export default function LoginPage() {
  const router = useRouter();
  return (
    <div className="min-h-screen grid place-items-center p-6">
      <LoginForm onSuccess={() => router.replace('/profile')} />
    </div>
  );
}
