import { NextRequest } from 'next/server';
import { backendUrl, proxyToBackend } from '@/shared/api/proxy';

type Ctx = { params: Promise<{ entry_id: string }> | { entry_id: string } };

export async function PATCH(req: NextRequest, ctx: Ctx) {
  const { entry_id } = await ctx.params;
  return proxyToBackend(req, backendUrl(`/meal-items/${entry_id}`));
}

export async function DELETE(req: NextRequest, ctx: Ctx) {
  const { entry_id } = await ctx.params;
  return proxyToBackend(req, backendUrl(`/meal-items/${entry_id}`));
}
