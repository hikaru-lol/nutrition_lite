import 'server-only';
import { NextRequest } from 'next/server';

export async function proxyToBackend(req: NextRequest, backendUrl: string) {
  const body =
    req.method === 'GET' || req.method === 'HEAD'
      ? undefined
      : await req.text();

  const res = await fetch(backendUrl, {
    method: req.method,
    // Cookie を backend に転送（me/logout 等に必要）
    headers: {
      'content-type': req.headers.get('content-type') ?? 'application/json',
      accept: req.headers.get('accept') ?? 'application/json',
      cookie: req.headers.get('cookie') ?? '',
    },
    body,
    cache: 'no-store',
  });

  // backend の Set-Cookie をブラウザへそのまま返す（ログインで必須）
  const headers = new Headers();
  const setCookies = (res.headers as any).getSetCookie?.() ?? [];
  for (const c of setCookies) headers.append('set-cookie', c);

  const ct = res.headers.get('content-type');
  if (ct) headers.set('content-type', ct);

  return new Response(await res.text(), { status: res.status, headers });
}
