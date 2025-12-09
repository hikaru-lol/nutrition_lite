// frontend/components/mocks/MockProvider.tsx
'use client';

import { useEffect, useState } from 'react';

/**
 * 開発環境でMSWを有効化するコンポーネント
 * 環境変数 NEXT_PUBLIC_USE_MOCK が 'true' の場合のみ有効化
 */
export function MockProvider({ children }: { children: React.ReactNode }) {
  const [isMockEnabled, setIsMockEnabled] = useState(false);

  useEffect(() => {
    // 環境変数の確認
    const useMock = process.env.NEXT_PUBLIC_USE_MOCK === 'true';

    if (useMock && typeof window !== 'undefined') {
      // クライアントサイドでのみMSWを初期化
      const initMocks = async () => {
        const { worker } = await import('@/lib/mocks/browser');

        // 開発環境でのみ有効化
        if (process.env.NODE_ENV === 'development') {
          await worker.start({
            onUnhandledRequest: 'bypass', // ハンドルされていないリクエストはそのまま通す
            serviceWorker: {
              url: '/mockServiceWorker.js',
            },
          });
          console.log('✅ MSWモックが有効化されました');
          setIsMockEnabled(true);
        }
      };

      initMocks().catch(console.error);
    }
  }, []);

  return <>{children}</>;
}
