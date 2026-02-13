import { NextRequest } from 'next/server';
import { backendUrl, proxyToBackend } from '@/shared/api/proxy';

// GET /api/meal-recommendations/[date] - 特定日の食事提案取得
export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ date: string }> }
) {
  const { date } = await params;
  return proxyToBackend(req, backendUrl(`/meal-recommendations/${date}`));
}
