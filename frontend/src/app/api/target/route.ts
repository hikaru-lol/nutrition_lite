import { NextRequest } from 'next/server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const ORIGIN = process.env.BACKEND_INTERNAL_ORIGIN ?? 'http://127.0.0.1:8000';
const PREFIX = process.env.BACKEND_TARGET_PREFIX ?? '/api/v1/target';

function buildUpstreamUrl(req: NextRequest, pathSegments: string[]) {
  const tail = pathSegments.join('/');
  const search = req.nextUrl.search;
  return `${ORIGIN}${PREFIX}/${tail}${search}`;
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
      'content-type': req.headers.get('content-type') ?? 'application/json',
      cookie: req.headers.get('cookie') ?? '',
      authorization: req.headers.get('authorization') ?? '',
    },
    body,
    cache: 'no-store',
  });

  const headers = new Headers();
  const ct = upstream.headers.get('content-type');
  if (ct) headers.set('content-type', ct);

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

export async function GET(
  req: NextRequest,
  ctx: { params: { path: string[] } }
) {
  return proxy(req, ctx.params.path);
}
export async function POST(
  req: NextRequest,
  ctx: { params: { path: string[] } }
) {
  return proxy(req, ctx.params.path);
}
export async function PUT(
  req: NextRequest,
  ctx: { params: { path: string[] } }
) {
  return proxy(req, ctx.params.path);
}
export async function PATCH(
  req: NextRequest,
  ctx: { params: { path: string[] } }
) {
  return proxy(req, ctx.params.path);
}
export async function DELETE(
  req: NextRequest,
  ctx: { params: { path: string[] } }
) {
  return proxy(req, ctx.params.path);
}
