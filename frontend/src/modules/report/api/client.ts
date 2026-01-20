// src/modules/report/api/client.ts
import { apiFetch } from '@/shared/lib/api/fetcher';
import type {
  DailyNutritionReportResponse,
  GenerateDailyReportRequest,
} from './types';

export const reportApi = {
  getByDate: (date: string) => {
    const qs = new URLSearchParams({ date });
    return apiFetch<DailyNutritionReportResponse>(
      `/nutrition/daily/report?${qs.toString()}`
    );
  },

  generate: (body: GenerateDailyReportRequest) =>
    apiFetch<DailyNutritionReportResponse>('/nutrition/daily/report', {
      method: 'POST',
      body,
    }),
};
