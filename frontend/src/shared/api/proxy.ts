import 'server-only';
import { NextRequest, NextResponse } from 'next/server';

export async function proxyToBackend(req: NextRequest, backendUrl: string) {
  const body =
    req.method === 'GET' || req.method === 'HEAD'
      ? undefined
      : await req.text();

  const res = await fetch(backendUrl, {
    method: req.method,
    // Cookie / Authorization を backend に転送
    headers: {
      'content-type': req.headers.get('content-type') ?? 'application/json',
      accept: req.headers.get('accept') ?? 'application/json',
      cookie: req.headers.get('cookie') ?? '',
      authorization: req.headers.get('authorization') ?? '',
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

  // 204 No Content の場合、ボディなしで返す（Next.js は 200 に変換）
  if (res.status === 204) {
    return new NextResponse(null, { status: 200, headers });
  }

  return new NextResponse(await res.text(), { status: res.status, headers });
}
