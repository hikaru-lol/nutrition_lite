import { NextRequest } from 'next/server';
import { backendUrl, proxyToBackend } from '@/shared/api/proxy';

/**
 * カレンダー月次サマリーAPI
 * GET /api/calendar/monthly-summary?year=2024&month=12
 */
export async function GET(req: NextRequest) {
  return proxyToBackend(
    req,
    backendUrl('/calendar/monthly-summary', req.nextUrl.search)
  );
}
