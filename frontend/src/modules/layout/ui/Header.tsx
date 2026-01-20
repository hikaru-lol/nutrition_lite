// src/modules/layout/ui/Header.tsx
'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Loader2 } from 'lucide-react';

import { Button } from '@/shared/ui/button'; // Sharedは使ってOK
import { useCurrentUser, useLogout } from '@/modules/auth/hooks/useMe'; // Module同士の連携はApp層で行うのが理想だが、UIコンポーネントとしての凝集度を高めるためここでImport

export const Header = () => {
  const router = useRouter();
  const { data: user, isLoading } = useCurrentUser();
  const { mutate: logout, isPending: isLogoutPending } = useLogout();

  const handleLogout = () => {
    logout(undefined, {
      onSuccess: () => {
        router.push('/auth/login');
      },
    });
  };

  return (
    // Rule C: マージンを持たせない (親が配置する)
    <header className="w-full border-b bg-white">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <Link href="/" className="text-xl font-bold">
          Fitness App
        </Link>

        <div>
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin text-gray-400" />
          ) : user?.user ? (
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium">
                {user.user.name || user.user.email} さん
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={handleLogout}
                disabled={isLogoutPending}
              >
                ログアウト
              </Button>
            </div>
          ) : (
            <div className="flex gap-2">
              <Button variant="ghost" size="sm" asChild>
                <Link href="/auth/login">ログイン</Link>
              </Button>
              <Button size="sm" asChild>
                <Link href="/auth/register">登録</Link>
              </Button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
