import { NextRequest } from 'next/server';
import { backendUrl, proxyToBackend } from '@/shared/api/proxy';

// GET /api/meal-recommendations - 食事提案一覧取得
export async function GET(req: NextRequest) {
  return proxyToBackend(
    req,
    backendUrl('/meal-recommendations', req.nextUrl.search)
  );
}
