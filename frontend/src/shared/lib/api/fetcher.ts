// src/shared/lib/api/fetcher.ts
import { ensureRefreshed } from './refresh';

const API_BASE = '/api/v1';

export type ApiErrorShape = {
  error: {
    code: string;
    message: string;
  };
};

export class ApiError extends Error {
  readonly status: number;
  readonly code?: string;

  constructor(args: { status: number; message: string; code?: string }) {
    super(args.message);
    this.name = 'ApiError';
    this.status = args.status;
    this.code = args.code;
  }
}

async function readJsonSafely(res: Response): Promise<unknown | null> {
  const ct = res.headers.get('content-type') ?? '';
  if (!ct.includes('application/json')) return null;
  try {
    return await res.json();
  } catch {
    return null;
  }
}

function normalizeError(res: Response, body: unknown | null): ApiError {
  // OpenAPI: { error: { code, message } }
  if (body && typeof body === 'object' && 'error' in body) {
    const e = (body as { error: { code: string; message: string } }).error;
    const code = typeof e?.code === 'string' ? e.code : undefined;
    const message =
      typeof e?.message === 'string'
        ? e.message
        : res.statusText || 'Request failed';
    return new ApiError({ status: res.status, code, message });
  }
  return new ApiError({
    status: res.status,
    message: res.statusText || 'Request failed',
  });
}

export type ApiFetchOptions = Omit<RequestInit, 'body'> & {
  body?: unknown;
  /** 401 のとき refresh → retry を無効化したい場合 */
  skipAuthRefresh?: boolean;
};

async function doFetch(
  input: string,
  opts: ApiFetchOptions = {}
): Promise<Response> {
  const url = input.startsWith('http') ? input : `${API_BASE}${input}`;
  const headers = new Headers(opts.headers);

  if (opts.body !== undefined && !headers.has('content-type')) {
    headers.set('content-type', 'application/json');
  }

  return fetch(url, {
    ...opts,
    headers,
    credentials: 'include', // HttpOnly cookie auth
    body: opts.body === undefined ? undefined : JSON.stringify(opts.body),
  });
}

/**
 * apiFetch<T>:
 * - 2xx: JSON を返す（204なら undefined）
 * - 401: refresh して 1回だけリトライ（skipAuthRefresh=true ならしない）
 * - それ以外: ApiError を throw
 */
export async function apiFetch<T>(
  path: string,
  opts: ApiFetchOptions = {}
): Promise<T> {
  const res = await doFetch(path, opts);

  // 401 -> refresh -> retry (1回だけ)
  if (res.status === 401 && !opts.skipAuthRefresh) {
    const ok = await ensureRefreshed();
    if (ok) {
      const retryRes = await doFetch(path, { ...opts, skipAuthRefresh: true });
      if (retryRes.ok) {
        if (retryRes.status === 204) return undefined as T;
        const json = await readJsonSafely(retryRes);
        return json as T;
      }
      const retryBody = await readJsonSafely(retryRes);
      throw normalizeError(retryRes, retryBody);
    }
    // refresh 失敗 → そのまま 401 をエラーとして扱う
  }

  if (res.ok) {
    if (res.status === 204) return undefined as T;
    const json = await readJsonSafely(res);
    return json as T;
  }

  const body = await readJsonSafely(res);
  throw normalizeError(res, body);
}
