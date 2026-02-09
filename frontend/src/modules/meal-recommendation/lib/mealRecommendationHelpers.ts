import {
  MealRecommendationCooldownError,
  MealRecommendationDailyLimitError,
  type MealRecommendationCardState,
} from '../contract/mealRecommendationContract';

/**
 * 404エラーかどうかを判定
 */
export function is404Error(error: unknown): boolean {
  const status = (error as { status?: number })?.status;
  const message = (error as { message?: string })?.message || '';
  return status === 404 ||
         message.includes('404') ||
         message.includes('not found') ||
         message.includes('Recommendation not found');
}

/**
 * カード状態を計算
 */
export function calculateCardState(
  isLoading: boolean,
  isGenerating: boolean,
  error: Error | null | undefined,
  recommendation: any | null
): MealRecommendationCardState {
  // ローディング状態
  if (isLoading || isGenerating) {
    return {
      status: 'loading',
      canGenerate: false,
    };
  }

  // エラー状態
  if (error) {
    let canGenerate = true;
    let nextGenerationTime: Date | undefined;
    let remainingGenerations: number | undefined;

    if (error instanceof MealRecommendationCooldownError) {
      canGenerate = false;
      nextGenerationTime = new Date(new Date().getTime() + error.minutes * 60 * 1000);
    } else if (error instanceof MealRecommendationDailyLimitError) {
      canGenerate = false;
      remainingGenerations = error.limit - error.currentCount;
    }

    return {
      status: error instanceof MealRecommendationCooldownError ||
              error instanceof MealRecommendationDailyLimitError ? 'rate-limited' : 'error',
      error,
      canGenerate,
      nextGenerationTime,
      remainingGenerations,
    };
  }

  // データが存在する場合
  if (recommendation) {
    return {
      status: 'available',
      recommendation,
      canGenerate: true,
    };
  }

  // 未生成状態
  return {
    status: 'empty',
    canGenerate: true,
  };
}
