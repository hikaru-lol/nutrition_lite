import { clientApiFetch } from '@/shared/api/client';
import type {
  GenerateMealRecommendationRequest,
  GenerateMealRecommendationResponse,
  GetMealRecommendationResponse,
  ListMealRecommendationsResponse,
} from '../contract/mealRecommendationContract';
import {
  MealRecommendationCooldownError,
  MealRecommendationDailyLimitError,
} from '../contract/mealRecommendationContract';

// =============================================================================
// エラーハンドリング
// =============================================================================

function parseMealRecommendationError(error: Error): Error {
  const message = error.message;

  // 429エラー（制限）の詳細処理
  if (message.includes('Please wait') && message.includes('minutes')) {
    const matches = message.match(/(\d+)\s*minutes/);
    if (matches) {
      const minutes = parseInt(matches[1], 10);
      return new MealRecommendationCooldownError(minutes);
    }
  }

  if (message.includes('Daily limit reached')) {
    const matches = message.match(/(\d+)\/(\d+)/);
    if (matches) {
      const current = parseInt(matches[1], 10);
      const limit = parseInt(matches[2], 10);
      return new MealRecommendationDailyLimitError(current, limit);
    }
  }

  return error;
}

// =============================================================================
// APIクライアント関数
// =============================================================================

export const mealRecommendationApi = {
  /**
   * 食事提案を生成
   */
  async generate(data: GenerateMealRecommendationRequest): Promise<GenerateMealRecommendationResponse> {
    try {
      return await clientApiFetch<GenerateMealRecommendationResponse>('/meal-recommendations/generate', {
        method: 'POST',
        body: data,
      });
    } catch (error) {
      throw parseMealRecommendationError(error as Error);
    }
  },

  /**
   * 食事提案リストを取得
   */
  async list(params: { limit?: number } = {}): Promise<ListMealRecommendationsResponse> {
    const searchParams = new URLSearchParams();
    if (params.limit) {
      searchParams.set('limit', params.limit.toString());
    }

    const path = searchParams.toString()
      ? `/meal-recommendations?${searchParams.toString()}`
      : '/meal-recommendations';

    return await clientApiFetch<ListMealRecommendationsResponse>(path);
  },

  /**
   * 特定日の食事提案を取得
   */
  async getByDate(date: string): Promise<GetMealRecommendationResponse> {
    return await clientApiFetch<GetMealRecommendationResponse>(`/meal-recommendations/${date}`);
  },
};