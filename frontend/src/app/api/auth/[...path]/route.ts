import { NextRequest } from 'next/server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const ORIGIN = process.env.BACKEND_INTERNAL_ORIGIN ?? 'http://127.0.0.1:8000';
const PREFIX = process.env.BACKEND_AUTH_PREFIX ?? '/api/v1/auth';

type Ctx = { params: Promise<{ path: string[] }> };

function buildUpstreamUrl(req: NextRequest, pathSegments: string[]) {
  const tail = pathSegments.join('/');
  const search = req.nextUrl.search; // クエリ保持
  // tail が空でも壊れないように
  return tail
    ? `${ORIGIN}${PREFIX}/${tail}${search}`
    : `${ORIGIN}${PREFIX}${search}`;
}

async function proxy(req: NextRequest, pathSegments: string[]) {
  const url = buildUpstreamUrl(req, pathSegments);

  const body =
    req.method === 'GET' || req.method === 'HEAD'
      ? undefined
      : await req.arrayBuffer();

  const upstream = await fetch(url, {
    method: req.method,
    headers: {
      accept: req.headers.get('accept') ?? 'application/json',
      ...(req.headers.get('content-type')
        ? { 'content-type': req.headers.get('content-type')! }
        : {}),
      cookie: req.headers.get('cookie') ?? '',
      authorization: req.headers.get('authorization') ?? '',
    },
    body,
    cache: 'no-store',
  });

  // Set-Cookie を確実にブラウザへ返す
  const headers = new Headers();
  const ct = upstream.headers.get('content-type');
  if (ct) headers.set('content-type', ct);

  const location = upstream.headers.get('location');
  if (location) headers.set('location', location);

  const getSetCookie = (upstream.headers as any).getSetCookie?.bind(
    upstream.headers
  );
  const setCookies: string[] =
    typeof getSetCookie === 'function'
      ? getSetCookie()
      : upstream.headers.get('set-cookie')
      ? [upstream.headers.get('set-cookie')!]
      : [];

  for (const c of setCookies) headers.append('set-cookie', c);

  return new Response(await upstream.text(), {
    status: upstream.status,
    headers,
  });
}

async function handle(req: NextRequest, ctx: Ctx) {
  const { path } = await ctx.params; // ✅ ここがポイント
  return proxy(req, path);
}

export const GET = handle;
export const POST = handle;
export const PUT = handle;
export const PATCH = handle;
export const DELETE = handle;

export async function OPTIONS() {
  return new Response(null, { status: 204 });
}
