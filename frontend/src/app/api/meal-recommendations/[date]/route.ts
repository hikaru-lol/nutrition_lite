import { NextRequest } from 'next/server';
import { proxyToBackend } from '@/shared/api/proxy';

const BACKEND = process.env.BACKEND_INTERNAL_ORIGIN ?? 'http://127.0.0.1:8000';
const PREFIX = '/api/v1';

// GET /api/meal-recommendations/[date] - 特定日の食事提案取得
export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ date: string }> }
) {
  const { date } = await params;
  return proxyToBackend(
    req,
    `${BACKEND}${PREFIX}/meal-recommendations/${date}`
  );
}