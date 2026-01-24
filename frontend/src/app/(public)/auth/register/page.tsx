'use client';

import { useRouter } from 'next/navigation';
import { RegisterForm } from '@/modules/auth/ui/RegisterForm';

export default function RegisterPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen grid place-items-center p-6">
      <RegisterForm onSuccess={() => router.replace('/auth/login')} />
    </div>
  );
}
