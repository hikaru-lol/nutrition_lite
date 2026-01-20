// src/modules/report/model/hooks.ts
'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { reportApi } from '../api/client';
import type {
  DailyNutritionReportResponse,
  GenerateDailyReportRequest,
} from '../api/types';
import { reportKeys } from './keys';
import { ApiError } from '@/shared/lib/api/fetcher';

/**
 * UIで扱いやすいように：
 * - 404（未生成）は null として返す（「まだ生成されていない」状態を作れる）
 * - それ以外は例外（AuthGuard/エラーUIで処理）
 */
async function getReportOrNull(
  date: string
): Promise<DailyNutritionReportResponse | null> {
  try {
    return await reportApi.getByDate(date);
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) return null;
    throw e;
  }
}

/** 指定日のレポート（未生成なら null） */
export function useDailyReport(date: string, opts?: { enabled?: boolean }) {
  return useQuery({
    queryKey: reportKeys.byDate(date),
    queryFn: () => getReportOrNull(date),
    enabled: opts?.enabled ?? Boolean(date),
  });
}

/**
 * レポート生成
 * - 成功：その日の report キャッシュを set
 * - 409（すでに存在）：UI側で「再取得」導線を出しやすい（例外として投げるので toast 等で処理）
 */
export function useGenerateDailyReport() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: GenerateDailyReportRequest) => reportApi.generate(body),
    onSuccess: (created) => {
      qc.setQueryData(reportKeys.byDate(created.date), created);
    },
  });
}
