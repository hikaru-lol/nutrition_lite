// frontend/components/mocks/MockProvider.tsx
'use client';

import { useEffect, useState } from 'react';
import { isMockEnabled } from '@/lib/mocks';

/**
 * 開発環境で MSW を有効化するコンポーネント
 * 環境変数 NEXT_PUBLIC_USE_MOCK が 'true' の場合のみ有効化
 *
 * ★ 変更点：
 *   - MSW の起動が完了するまで children をレンダリングしない
 *   - 起動完了後に初めて children（AppShell など）を描画する
 */
export function MockProvider({ children }: { children: React.ReactNode }) {
  const useMock = isMockEnabled();

  // モックを使わない場合は最初から ready = true（= 即 children を描画）
  const [ready, setReady] = useState(() => {
    if (!useMock) return true;
    // 本番など development 以外では MSW を使わない前提
    if (process.env.NODE_ENV !== 'development') return true;
    return false; // dev + mock 有効のときだけ「起動待ち」状態からスタート
  });

  useEffect(() => {
    // モックを使わない or 本番環境なら何もしない
    if (!useMock) return;
    if (process.env.NODE_ENV !== 'development') return;

    let cancelled = false;

    const initMocks = async () => {
      try {
        // クライアントサイドでのみ MSW を初期化
        const { worker } = await import('@/lib/mocks/browser');

        await worker.start({
          onUnhandledRequest: 'bypass', // ハンドルされていないリクエストはそのまま通す
          serviceWorker: {
            url: '/mockServiceWorker.js',
          },
        });

        if (!cancelled) {
          console.log('✅ MSWモックが有効化されました');
          setReady(true); // ★ 起動完了 → children を描画してOK
        }
      } catch (err) {
        console.error('MSW の初期化に失敗しました', err);
        // 失敗してもアプリがまったく表示されないのはつらいので、
        // fail-open で ready にしておく（必要に応じてここは変えてOK）
        if (!cancelled) {
          setReady(true);
        }
      }
    };

    void initMocks();

    return () => {
      cancelled = true;
    };
  }, [useMock]);

  // ★ MSW 起動待ちの間は、アプリ本体を描画せずローディング画面だけ出す
  if (!ready) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-50 flex items-center justify-center">
        <p className="text-sm text-slate-400">モックサーバー起動中...</p>
      </div>
    );
  }

  // ★ MSW 起動後（またはモック無効のとき）は、通常どおり children を描画
  return <>{children}</>;
}
