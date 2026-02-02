import { NextRequest } from 'next/server';
import { proxyToBackend } from '@/shared/api/proxy';

const BACKEND_INTERNAL_ORIGIN =
  process.env.BACKEND_INTERNAL_ORIGIN ?? 'http://127.0.0.1:8000';
const BACKEND_API_PREFIX = process.env.BACKEND_API_PREFIX ?? '/api/v1';

function backendUrl(path: string, search: string) {
  return `${BACKEND_INTERNAL_ORIGIN}${BACKEND_API_PREFIX}${path}${search}`;
}

/**
 * カレンダー月次サマリーAPI
 * GET /api/calendar/monthly-summary?year=2024&month=12
 */
export async function GET(req: NextRequest) {
  // 常に認証付きエンドポイントを使用
  const endpoint = '/calendar/monthly-summary';

  return proxyToBackend(
    req,
    backendUrl(endpoint, req.nextUrl.search)
  );
}