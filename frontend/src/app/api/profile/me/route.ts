import { NextRequest } from 'next/server';
import { backendUrl, proxyToBackend } from '@/shared/api/proxy';

export const runtime = 'nodejs';

export async function GET(req: NextRequest, ctx: any) {
  if (ctx?.params) await ctx.params;

  return proxyToBackend(req, backendUrl('/profile/me', req.nextUrl.search));
}

export async function PUT(req: NextRequest, ctx: any) {
  if (ctx?.params) await ctx.params;

  return proxyToBackend(req, backendUrl('/profile/me', req.nextUrl.search));
}
