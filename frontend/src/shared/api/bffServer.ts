import 'server-only';
import { headers } from 'next/headers';

function getOriginFromHeaders(h: Headers): string {
  const host = h.get('x-forwarded-host') ?? h.get('host');
  const proto = h.get('x-forwarded-proto') ?? 'http';
  if (!host) throw new Error('Cannot resolve origin (missing host header)');
  return `${proto}://${host}`;
}

export async function bffServerFetch<T>(
  path: string,
  init: RequestInit = {}
): Promise<T> {
  const h = await headers();
  const origin = getOriginFromHeaders(h);

  const res = await fetch(`${origin}${path}`, {
    ...init,
    // server -> server なので cookie は自動で載らないケースがあるため明示
    headers: {
      ...(init.headers ?? {}),
      cookie: h.get('cookie') ?? '',
      accept: 'application/json',
    },
    cache: 'no-store',
  });

  if (!res.ok) throw new Error(`bffServerFetch failed: ${res.status}`);
  return (await res.json()) as T;
}
