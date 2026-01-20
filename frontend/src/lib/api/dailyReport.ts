// frontend/lib/api/dailyReport.ts
import { apiGet, apiPost } from './client';

export type DailyNutritionReportResponse = {
  date: string; // "YYYY-MM-DD"
  summary: string;
  good_points: string[];
  improvement_points: string[];
  tomorrow_focus: string[];
  created_at: string;
};

export async function fetchDailyReport(
  date: string
): Promise<DailyNutritionReportResponse> {
  return apiGet<DailyNutritionReportResponse>(
    `/nutrition/daily/report?date=${encodeURIComponent(date)}`
  );
}

export async function generateDailyReport(
  date: string
): Promise<DailyNutritionReportResponse> {
  return apiPost<DailyNutritionReportResponse>('/nutrition/daily/report', {
    date,
  });
}
