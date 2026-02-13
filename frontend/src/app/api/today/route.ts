import { NextRequest } from 'next/server';
import { backendUrl, proxyToBackend } from '@/shared/api/proxy';

// 例：Backend 側を /api/v1/today?date=YYYY-MM-DD と仮定
export async function GET(req: NextRequest) {
  return proxyToBackend(req, backendUrl('/today', req.nextUrl.search));
}
