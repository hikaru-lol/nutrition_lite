// src/shared/api/client.ts
import { API_BASE_URL } from '@/shared/config/env';
import { ApiError, parseApiError } from '@/shared/lib/errors';

type ApiFetchOptions = {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body?: unknown;
  headers?: Record<string, string>;
  signal?: AbortSignal;
  /**
   * 401時に refresh を1回だけ試す（成功したら元リクエストをリトライ）
   */
  retryOnUnauthorized?: boolean;
};

/**
 * refresh は “循環依存” しがちなので、ここだけ関数参照で差し替えできる形にする
 */
let refreshFn: (() => Promise<boolean>) | null = null;
export function registerRefresh(fn: () => Promise<boolean>) {
  refreshFn = fn;
}

async function rawFetch(
  path: string,
  opts: ApiFetchOptions
): Promise<Response> {
  const url = `${API_BASE_URL}${path}`;
  const res = await fetch(url, {
    method: opts.method ?? 'GET',
    credentials: 'include',
    headers: {
      Accept: 'application/json',
      ...(opts.body ? { 'Content-Type': 'application/json' } : {}),
      ...(opts.headers ?? {}),
    },
    body: opts.body ? JSON.stringify(opts.body) : undefined,
    signal: opts.signal,
  });
  return res;
}

export async function apiFetch<T>(
  path: string,
  opts: ApiFetchOptions = {}
): Promise<T> {
  try {
    const res = await rawFetch(path, opts);

    if (res.ok) {
      // 空ボディ対応
      if (res.status === 204) return undefined as T;
      const ct = res.headers.get('content-type') ?? '';
      if (!ct.includes('application/json'))
        return (await res.text()) as unknown as T;
      return (await res.json()) as T;
    }

    // 401 → refresh → 1回だけリトライ
    if (res.status === 401 && opts.retryOnUnauthorized !== false && refreshFn) {
      const ok = await refreshFn();
      if (ok) {
        const retryRes = await rawFetch(path, {
          ...opts,
          retryOnUnauthorized: false,
        });
        if (retryRes.ok) {
          if (retryRes.status === 204) return undefined as T;
          const ct2 = retryRes.headers.get('content-type') ?? '';
          if (!ct2.includes('application/json'))
            return (await retryRes.text()) as unknown as T;
          return (await retryRes.json()) as T;
        }
        throw await parseApiError(retryRes);
      }
    }

    throw await parseApiError(res);
  } catch (e: any) {
    if (e instanceof ApiError) throw e;
    // ネットワーク・CORS・タイムアウト等
    throw new ApiError({
      kind: 'network',
      message: e?.message ?? 'Network error',
      details: e,
    });
  }
}
