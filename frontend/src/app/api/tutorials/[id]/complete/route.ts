import { NextRequest } from 'next/server';
import { backendUrl, proxyToBackend } from '@/shared/api/proxy';

interface RouteParams {
  params: Promise<{ id: string }>;
}

/**
 * POST /api/tutorials/[id]/complete
 * チュートリアル完了をマーク
 */
export async function POST(req: NextRequest, { params }: RouteParams) {
  const { id } = await params;
  return proxyToBackend(req, backendUrl(`/tutorials/${id}/complete`));
}
