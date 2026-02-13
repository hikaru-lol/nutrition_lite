import { NextRequest } from 'next/server';
import { backendUrl, proxyToBackend } from '@/shared/api/proxy';

// POST /api/meal-recommendations/generate - 食事提案生成
export async function POST(req: NextRequest) {
  return proxyToBackend(req, backendUrl('/meal-recommendations/generate'));
}
