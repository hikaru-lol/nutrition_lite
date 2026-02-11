import { clientApiFetch } from '@/shared/api/client';
import {
  MealAndDailyNutritionResponseSchema,
  DailyNutritionReportResponseSchema,
  GenerateDailyReportRequestSchema,
  type MealAndDailyNutritionResponse,
  type DailyNutritionReport,
} from '../contract/nutritionContract';
import type { MealType } from '@/modules/meal/contract/mealContract';

/**
 * 食事と1日の栄養サマリーを取得（既存データのみ、計算なし）
 */
export async function getNutritionData(params: {
  date: string;
  meal_type: MealType;
  meal_index: number | null;
}): Promise<MealAndDailyNutritionResponse> {
  const searchParams = new URLSearchParams();
  searchParams.set('date', params.date);
  searchParams.set('meal_type', params.meal_type);
  if (params.meal_index !== null) {
    searchParams.set('meal_index', String(params.meal_index));
  }

  const raw = await clientApiFetch<unknown>(
    `/nutrition/meal?${searchParams.toString()}`,
    { method: 'GET' }
  );
  return MealAndDailyNutritionResponseSchema.parse(raw);
}

/**
 * 食事と1日の栄養サマリーを再計算・取得
 * @deprecated 後方互換性のため残存。新規実装では getNutritionData または computeNutritionData を使用
 */
export async function recomputeMealAndDaily(params: {
  date: string;
  meal_type: MealType;
  meal_index: number | null;
}): Promise<MealAndDailyNutritionResponse> {
  // 既存の呼び出しを壊さないよう、まずは取得を試行
  try {
    return await getNutritionData(params);
  } catch (error) {
    // 404の場合は計算実行（後方互換性）
    if (error instanceof Error && error.message.includes('404')) {
      return await computeNutritionData(params);
    }
    throw error;
  }
}

/**
 * 食事と1日の栄養サマリーをOpenAIで計算・取得
 */
export async function computeNutritionData(params: {
  date: string;
  meal_type: MealType;
  meal_index: number | null;
}): Promise<MealAndDailyNutritionResponse> {
  const searchParams = new URLSearchParams();
  searchParams.set('date', params.date);
  searchParams.set('meal_type', params.meal_type);
  if (params.meal_index !== null) {
    searchParams.set('meal_index', String(params.meal_index));
  }

  const raw = await clientApiFetch<unknown>(
    `/nutrition/meal/compute?${searchParams.toString()}`,
    { method: 'POST' }
  );
  return MealAndDailyNutritionResponseSchema.parse(raw);
}

/**
 * 日次レポートを取得（404 の場合は null を返す）
 */
export async function getDailyReport(
  date: string
): Promise<DailyNutritionReport | null> {
  try {
    const raw = await clientApiFetch<unknown>(
      `/nutrition/daily/report?date=${encodeURIComponent(date)}`,
      { method: 'GET' }
    );
    return DailyNutritionReportResponseSchema.parse(raw);
  } catch (err) {
    // 404 = レポート未作成として扱う
    if (err instanceof Error && err.message.includes('404')) {
      return null;
    }
    throw err;
  }
}

/**
 * 日次レポートを生成
 * - 201: 新規生成成功 → parse して返す
 * - 409: 既存あり → null を返す（呼び出し元で refetch してもらう）
 */
export async function generateDailyReport(
  date: string
): Promise<DailyNutritionReport | null> {
  const body = GenerateDailyReportRequestSchema.parse({ date });

  try {
    const raw = await clientApiFetch<unknown>('/nutrition/daily/report', {
      method: 'POST',
      body,
    });
    return DailyNutritionReportResponseSchema.parse(raw);
  } catch (err) {
    // 409 = 既存あり → refetch してもらう想定で null を返す
    if (err instanceof Error && err.message.includes('409')) {
      return null;
    }
    throw err;
  }
}
