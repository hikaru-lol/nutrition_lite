// src/shared/lib/api/refresh.ts

let refreshPromise: Promise<boolean> | null = null;

/**
 * 401 が出たときに呼ぶ。
 * 同時多発しても refresh は 1回だけ実行され、他は同じPromiseを待つ。
 */
export async function ensureRefreshed(): Promise<boolean> {
  if (!refreshPromise) {
    refreshPromise = refreshOnce().finally(() => {
      refreshPromise = null;
    });
  }
  return refreshPromise;
}

async function refreshOnce(): Promise<boolean> {
  const res = await fetch('/api/v1/auth/refresh', {
    method: 'POST',
    credentials: 'include',
  });
  return res.ok;
}
