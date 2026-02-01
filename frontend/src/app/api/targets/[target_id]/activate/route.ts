import { NextRequest } from 'next/server';
import { proxyToBackend } from '@/shared/api/proxy';

const BACKEND_INTERNAL_ORIGIN =
  process.env.BACKEND_INTERNAL_ORIGIN ?? 'http://127.0.0.1:8000';
const BACKEND_API_PREFIX = process.env.BACKEND_API_PREFIX ?? '/api/v1';

function backendUrl(path: string) {
  return `${BACKEND_INTERNAL_ORIGIN}${BACKEND_API_PREFIX}${path}`;
}

type Ctx = { params: Promise<{ target_id: string }> | { target_id: string } };

export async function POST(req: NextRequest, ctx: Ctx) {
  const { target_id } = await ctx.params;
  return proxyToBackend(req, backendUrl(`/targets/${target_id}/activate`));
}
