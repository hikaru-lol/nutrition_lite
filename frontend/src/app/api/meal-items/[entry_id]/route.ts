import { NextRequest } from 'next/server';
import { proxyToBackend } from '@/shared/api/proxy';

const BACKEND_INTERNAL_ORIGIN =
  process.env.BACKEND_INTERNAL_ORIGIN ?? 'http://127.0.0.1:8000';
const BACKEND_API_PREFIX = process.env.BACKEND_API_PREFIX ?? '/api/v1';

function backendUrl(path: string) {
  return `${BACKEND_INTERNAL_ORIGIN}${BACKEND_API_PREFIX}${path}`;
}

type Ctx = { params: Promise<{ entry_id: string }> | { entry_id: string } };

export async function PATCH(req: NextRequest, ctx: Ctx) {
  const { entry_id } = await ctx.params;
  return proxyToBackend(req, backendUrl(`/meal-items/${entry_id}`));
}

export async function DELETE(req: NextRequest, ctx: Ctx) {
  const { entry_id } = await ctx.params;
  return proxyToBackend(req, backendUrl(`/meal-items/${entry_id}`));
}
