// src/modules/profile/model/hooks.ts
'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { profileApi } from '../api/client';
import type { ProfileRequest, ProfileResponse } from '../api/types';
import { profileKeys } from './keys';
import { authKeys } from '@/modules/auth/model/keys';

/**
 * Profile は「無い」という状態が起こりうる。
 * OpenAPI上は GET /profile/me が 401(=未認証 or profile not found) と書かれているが、
 * 実運用では "profile not found" を 404 で返す実装もよくある。
 *
 * ここでは UI 的に扱いやすいように、
 * - 401: 未ログイン扱い（上位のAuthGuardで処理）
 * - 404: プロフィール未作成として null を返す
 * に寄せたい場合は下の catch を調整する。
 *
 * ※現時点では「素直に例外を投げる」実装にしておき、必要に応じて null 化するのが安全。
 */
export function useProfileMe() {
  return useQuery({
    queryKey: profileKeys.me(),
    queryFn: profileApi.getMe,
  });
}

export function useUpsertProfileMe() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: ProfileRequest) => profileApi.upsertMe(body),
    onSuccess: (profile: ProfileResponse) => {
      // profile を即反映
      qc.setQueryData(profileKeys.me(), profile);

      // auth.me の has_profile が true になっている可能性が高いので再同期
      qc.invalidateQueries({ queryKey: authKeys.me() });
    },
  });
}
