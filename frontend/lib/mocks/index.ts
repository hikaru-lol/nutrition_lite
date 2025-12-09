// frontend/lib/mocks/index.ts
/**
 * MSWモックの有効化/無効化を管理
 *
 * 環境変数 NEXT_PUBLIC_USE_MOCK が 'true' の場合にモックを有効化します
 *
 * 使用方法:
 * 1. .env.local に NEXT_PUBLIC_USE_MOCK=true を追加
 * 2. 開発サーバーを再起動
 */

export const isMockEnabled = () => {
  if (typeof window === 'undefined') {
    // サーバーサイドでは環境変数を直接確認
    return process.env.NEXT_PUBLIC_USE_MOCK === 'true';
  }
  // クライアントサイドでは window に設定された値を確認
  return (window as any).__USE_MOCK__ === true;
};
