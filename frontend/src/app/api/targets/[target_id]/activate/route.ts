import { NextRequest } from 'next/server';
import { backendUrl, proxyToBackend } from '@/shared/api/proxy';

type Ctx = { params: Promise<{ target_id: string }> | { target_id: string } };

export async function POST(req: NextRequest, ctx: Ctx) {
  const { target_id } = await ctx.params;
  return proxyToBackend(req, backendUrl(`/targets/${target_id}/activate`));
}
