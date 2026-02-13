import { NextRequest } from 'next/server';
import { backendUrl, proxyToBackend } from '@/shared/api/proxy';

/**
 * GET /api/tutorials/status
 * チュートリアル完了状況を取得
 */
export async function GET(req: NextRequest) {
  return proxyToBackend(req, backendUrl('/tutorials/status'));
}
