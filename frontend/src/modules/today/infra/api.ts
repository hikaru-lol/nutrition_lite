import { apiClient } from '@/shared/lib/apiClient';
import { components } from '@/shared/api/schema';

// API定義から型を取得
export type TodaySummary = components['schemas']['TodaySummaryResponse'];

export const fetchTodaySummary = async (): Promise<TodaySummary> => {
  // 日付はバックエンドがサーバー時刻(JST)で判定するため、パラメータ不要
  const res = await apiClient.get<TodaySummary>('/today');
  return res.data;
};
