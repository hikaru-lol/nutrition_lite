import { NextRequest } from 'next/server';
import { proxyToBackend } from '@/shared/api/proxy';

const BACKEND = process.env.BACKEND_INTERNAL_ORIGIN ?? 'http://127.0.0.1:8000';
const PREFIX = '/api/v1';

// GET /api/meal-recommendations - 食事提案一覧取得
export async function GET(req: NextRequest) {
  return proxyToBackend(
    req,
    `${BACKEND}${PREFIX}/meal-recommendations${req.nextUrl.search}`
  );
}