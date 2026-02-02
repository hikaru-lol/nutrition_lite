import { NextRequest } from 'next/server';
import { proxyToBackend } from '@/shared/api/proxy';

const BACKEND = process.env.BACKEND_INTERNAL_ORIGIN ?? 'http://127.0.0.1:8000';
const PREFIX = '/api/v1';

/**
 * GET /api/tutorials/status
 * チュートリアル完了状況を取得
 */
export async function GET(req: NextRequest) {
  return proxyToBackend(req, `${BACKEND}${PREFIX}/tutorials/status`);
}