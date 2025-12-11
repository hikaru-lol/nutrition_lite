// frontend/lib/hooks/useCurrentUser.ts
'use client';

import { useEffect, useState } from 'react';
import { fetchMe, type CurrentUser } from '@/lib/api/auth';
import { ApiError } from '@/lib/api/client';

export function useCurrentUser() {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      console.log('useCurrentUser load');
      try {
        setIsLoading(true);
        const me = await fetchMe();
        if (!cancelled) setUser(me);
      } catch (e) {
        if (e instanceof ApiError && e.status === 401) {
          // 未ログイン
          if (!cancelled) setUser(null);
        } else {
          console.error('Failed to fetch current user', e);
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    };

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  return { user, isLoading };
}
