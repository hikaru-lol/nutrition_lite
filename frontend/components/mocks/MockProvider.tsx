// frontend/components/mocks/MockProvider.tsx
'use client';

import { useEffect } from 'react';
import { isMockEnabled } from '@/lib/mocks';

/**
 * 開発環境でMSWを有効化するコンポーネント
 * 環境変数 NEXT_PUBLIC_USE_MOCK が 'true' の場合のみ有効化
 */
export function MockProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    // 環境変数の確認
    const useMock = isMockEnabled();

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
        }
      };

      initMocks().catch(console.error);
    }
  }, []);

  return <>{children}</>;
}
