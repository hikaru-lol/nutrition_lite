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

/**
 * モックが有効化されているかどうかを判定
 * @returns モックが有効化されている場合 true
 */
export const isMockEnabled = (): boolean => {
  return process.env.NEXT_PUBLIC_USE_MOCK === 'true';
};
