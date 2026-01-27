import { NextRequest } from 'next/server';
import { proxyToBackend } from '@/shared/api/proxy';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const ORIGIN = process.env.BACKEND_INTERNAL_ORIGIN ?? 'http://127.0.0.1:8000';
const PREFIX = process.env.BACKEND_TARGET_PREFIX ?? '/api/v1/targets';

function buildUpstreamUrl(req: NextRequest, pathSegments: string[]) {
  const tail = pathSegments.length > 0 ? `/${pathSegments.join('/')}` : '';
  const search = req.nextUrl.search;
  return `${ORIGIN}${PREFIX}${tail}${search}`;
}

type RouteContext = { params: Promise<{ path?: string[] }> };

async function handle(req: NextRequest, ctx: RouteContext) {
  const { path = [] } = await ctx.params;
  const url = buildUpstreamUrl(req, path);
  return proxyToBackend(req, url);
}

export const GET = handle;
export const POST = handle;
export const PUT = handle;
export const PATCH = handle;
export const DELETE = handle;
