import { NextRequest } from 'next/server';
import { proxyToBackend } from '@/shared/api/proxy';

const BACKEND_ORIGIN =
  process.env.BACKEND_INTERNAL_ORIGIN ?? 'http://127.0.0.1:8000';

// 例：Backend 側を /api/v1/today?date=YYYY-MM-DD と仮定
export async function GET(req: NextRequest) {
  const upstream = `${BACKEND_ORIGIN}/api/v1/today${req.nextUrl.search}`;
  return proxyToBackend(req, upstream);
}
