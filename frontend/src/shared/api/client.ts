// src/shared/api/client.ts
export type ClientApiOptions = {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body?: unknown;
  headers?: Record<string, string>;
};

export async function clientApiFetch<T>(
  path: string,
  opts: ClientApiOptions = {}
): Promise<T> {
  const res = await fetch(`/api${path}`, {
    method: opts.method ?? 'GET',
    headers: {
      accept: 'application/json',
      ...(opts.body ? { 'content-type': 'application/json' } : {}),
      ...(opts.headers ?? {}),
    },
    body: opts.body ? JSON.stringify(opts.body) : undefined,
    cache: 'no-store',
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(text || `API Error: ${res.status}`);
  }

  if (res.status === 204) return undefined as T;

  // 空のレスポンスの場合（204 → 200 変換対応）
  const text = await res.text();
  if (!text) return undefined as T;

  return JSON.parse(text) as T;
}
