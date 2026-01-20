// frontend/lib/mocks/server.ts
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

// サーバー環境（テスト用）のMSWセットアップ
export const server = setupServer(...handlers);
