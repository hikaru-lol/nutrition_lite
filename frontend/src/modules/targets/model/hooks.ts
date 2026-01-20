// src/modules/target/model/hooks.ts
'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { targetApi } from '../api/client';
import type {
  CreateTargetRequest,
  TargetListResponse,
  TargetResponse,
  UpdateTargetRequest,
} from '../api/types';
import { targetKeys } from './keys';

function upsertTargetInList(
  list: TargetListResponse | undefined,
  updated: TargetResponse
): TargetListResponse | undefined {
  if (!list) return list;
  const items = list.items.map((t) => (t.id === updated.id ? updated : t));
  // create 時は先頭に来る仕様（newest first）に合わせたいなら、存在しなければ unshift
  if (!items.some((t) => t.id === updated.id)) {
    items.unshift(updated);
  }
  return { items };
}

export function useTargets(params?: { limit?: number; offset?: number }) {
  return useQuery({
    queryKey: targetKeys.list(params),
    queryFn: () => targetApi.list(params),
  });
}

export function useActiveTarget() {
  return useQuery({
    queryKey: targetKeys.active(),
    queryFn: targetApi.getActive,
  });
}

export function useTargetById(targetId: string, opts?: { enabled?: boolean }) {
  return useQuery({
    queryKey: targetKeys.byId(targetId),
    queryFn: () => targetApi.getById(targetId),
    enabled: opts?.enabled ?? true,
  });
}

export function useCreateTarget(params?: {
  list?: { limit?: number; offset?: number };
}) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: CreateTargetRequest) => targetApi.create(body),
    onSuccess: (created) => {
      // list 反映（該当の list params があるならそこへ）
      const listKey = targetKeys.list(params?.list);
      qc.setQueryData<TargetListResponse | undefined>(listKey, (prev) =>
        upsertTargetInList(prev, created)
      );

      // byId 反映
      qc.setQueryData(targetKeys.byId(created.id), created);

      // active が切り替わる可能性がある（「初回ターゲットならactive」）
      qc.invalidateQueries({ queryKey: targetKeys.active() });

      // list 全体も他paramsがあるなら安全にinvalidate（軽量ならこれが無難）
      qc.invalidateQueries({ queryKey: targetKeys.list() });
    },
  });
}

export function useUpdateTarget(
  targetId: string,
  params?: { list?: { limit?: number; offset?: number } }
) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: UpdateTargetRequest) => targetApi.update(targetId, body),
    onSuccess: (updated) => {
      // byId
      qc.setQueryData(targetKeys.byId(updated.id), updated);

      // list（特定paramsがあるならそこへ、なければ全体invalidateでもOK）
      if (params?.list) {
        qc.setQueryData<TargetListResponse | undefined>(
          targetKeys.list(params.list),
          (prev) => upsertTargetInList(prev, updated)
        );
      }
      qc.invalidateQueries({ queryKey: targetKeys.list() });

      // activeにも反映されうる（active target を編集した場合）
      qc.setQueryData<TargetResponse | undefined>(targetKeys.active(), (prev) =>
        prev?.id === updated.id ? updated : prev
      );
    },
  });
}

export function useActivateTarget(params?: {
  list?: { limit?: number; offset?: number };
}) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (targetId: string) => targetApi.activate(targetId),
    onSuccess: (activated) => {
      // active は確定でこれ
      qc.setQueryData(targetKeys.active(), activated);

      // byId
      qc.setQueryData(targetKeys.byId(activated.id), activated);

      // list: is_active が変わるので安全にinvalidate（またはローカルで is_active を整合）
      qc.invalidateQueries({ queryKey: targetKeys.list() });
      if (params?.list)
        qc.invalidateQueries({ queryKey: targetKeys.list(params.list) });
    },
  });
}
