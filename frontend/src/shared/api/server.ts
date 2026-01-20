// src/shared/api/server.ts
import { cookies } from 'next/headers';
import { API_BASE_URL } from '@/shared/config/env';
import { parseApiError } from '@/shared/lib/errors';

type ServerApiFetchOptions = {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body?: unknown;
  headers?: Record<string, string>;
  /**
   * ガード用途なので no-store を推奨（セッション状態のズレ防止）
   */
  cache?: RequestCache;
};

export async function serverApiFetch<T>(
  path: string,
  opts: ServerApiFetchOptions = {}
): Promise<T> {
  const url = `${API_BASE_URL}${path}`;
  const cookieHeader = cookies().toString();

  const res = await fetch(url, {
    method: opts.method ?? 'GET',
    cache: opts.cache ?? 'no-store',
    headers: {
      Accept: 'application/json',
      ...(opts.body ? { 'Content-Type': 'application/json' } : {}),
      ...(cookieHeader ? { Cookie: cookieHeader } : {}),
      ...(opts.headers ?? {}),
    },
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });

  if (!res.ok) throw await parseApiError(res);

  if (res.status === 204) return undefined as T;
  const ct = res.headers.get('content-type') ?? '';
  if (!ct.includes('application/json'))
    return (await res.text()) as unknown as T;
  return (await res.json()) as T;
}
