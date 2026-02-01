// src/shared/lib/errors.ts
export type ApiErrorKind =
  | 'unauthorized'
  | 'forbidden'
  | 'not_found'
  | 'validation'
  | 'conflict'
  | 'rate_limited'
  | 'server'
  | 'network'
  | 'unknown';

export class ApiError extends Error {
  readonly kind: ApiErrorKind;
  readonly status?: number;
  readonly details?: unknown;

  constructor(args: {
    kind: ApiErrorKind;
    message: string;
    status?: number;
    details?: unknown;
  }) {
    super(args.message);
    this.name = 'ApiError';
    this.kind = args.kind;
    this.status = args.status;
    this.details = args.details;
  }
}

export function isApiError(e: unknown): e is ApiError {
  return e instanceof ApiError;
}

/**
 * Backendのエラー形がどうであっても、可能な範囲で message/details を抽出して正規化する。
 * - { detail: "..." } / { message: "..." } / { error: { message } } などに耐性を持つ
 */
export async function parseApiError(res: Response): Promise<ApiError> {
  const status = res.status;

  let payload: any = undefined;
  try {
    const ct = res.headers.get('content-type') ?? '';
    if (ct.includes('application/json')) payload = await res.json();
    else payload = await res.text();
  } catch {
    // ignore
  }

  const message =
    (payload?.error?.message as string) ||
    (payload?.message as string) ||
    (payload?.detail as string) ||
    (typeof payload === 'string' ? payload : '') ||
    `Request failed (${status})`;

  const kind: ApiErrorKind =
    status === 401
      ? 'unauthorized'
      : status === 403
      ? 'forbidden'
      : status === 404
      ? 'not_found'
      : status === 409
      ? 'conflict'
      : status === 422 || status === 400
      ? 'validation'
      : status === 429
      ? 'rate_limited'
      : status >= 500
      ? 'server'
      : 'unknown';

  return new ApiError({ kind, message, status, details: payload });
}
