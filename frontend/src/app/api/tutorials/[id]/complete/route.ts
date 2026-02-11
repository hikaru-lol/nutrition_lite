import { NextRequest } from 'next/server';
import { proxyToBackend } from '@/shared/api/proxy';

const BACKEND = process.env.BACKEND_INTERNAL_ORIGIN ?? 'http://127.0.0.1:8000';
const PREFIX = '/api/v1';

interface RouteParams {
  params: Promise<{ id: string }>;
}

/**
 * POST /api/tutorials/[id]/complete
 * チュートリアル完了をマーク
 */
export async function POST(req: NextRequest, { params }: RouteParams) {
  const { id } = await params;
  return proxyToBackend(req, `${BACKEND}${PREFIX}/tutorials/${id}/complete`);
}