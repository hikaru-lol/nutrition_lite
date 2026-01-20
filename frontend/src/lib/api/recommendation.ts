// frontend/lib/api/recommendation.ts
import { apiGet, apiPost } from './client';

export type RecommendationResponseApi = {
  id: string;
  user_id: string;
  generated_for_date: string; // "YYYY-MM-DD"
  body: string;
  tips: string[];
  created_at: string;
};

export async function fetchLatestRecommendation(): Promise<RecommendationResponseApi> {
  return apiGet<RecommendationResponseApi>('/nutrition/recommendation/latest');
}

export async function fetchRecommendationByDate(
  date: string
): Promise<RecommendationResponseApi> {
  return apiGet<RecommendationResponseApi>(
    `/nutrition/recommendation?date=${encodeURIComponent(date)}`
  );
}

export async function generateRecommendation(
  date: string
): Promise<RecommendationResponseApi> {
  return apiPost<RecommendationResponseApi>('/nutrition/recommendation', {
    base_date: date,
  });
}
