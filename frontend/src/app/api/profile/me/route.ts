import { NextRequest } from 'next/server';
import { proxyToBackend } from '@/shared/api/proxy';

export const runtime = 'nodejs';

function joinPath(a: string, b: string) {
  const left = a.endsWith('/') ? a.slice(0, -1) : a;
  const right = b.startsWith('/') ? b : `/${b}`;
  return `${left}${right}`;
}

function buildProfileMeBackendUrl(req: NextRequest) {
  const origin = process.env.BACKEND_INTERNAL_ORIGIN ?? 'http://127.0.0.1:8000';
  const prefix = process.env.BACKEND_API_PREFIX ?? '/api/v1';
  const path = '/profile/me';

  const base = joinPath(joinPath(origin, prefix), path);
  return `${base}${req.nextUrl.search}`;
}

export async function GET(req: NextRequest, ctx: any) {
  if (ctx?.params) await ctx.params;

  return proxyToBackend(req, buildProfileMeBackendUrl(req));
}

export async function PUT(req: NextRequest, ctx: any) {
  if (ctx?.params) await ctx.params;

  return proxyToBackend(req, buildProfileMeBackendUrl(req));
}
