/**
 * TodayPage関連のReact Query キー定義
 *
 * 階層構造でキャッシュを管理し、部分的な無効化を可能にする
 */

export const todayQueryKeys = {
  // 基本キー: 全てのTodayページデータ
  all: (date: string) => ['today', date] as const,

  // 食事関連
  meals: (date: string) => [...todayQueryKeys.all(date), 'meals'] as const,
  mealItems: (date: string) => [...todayQueryKeys.meals(date), 'items'] as const,

  // 目標関連
  targets: (date: string) => [...todayQueryKeys.all(date), 'targets'] as const,
  activeTarget: () => ['target', 'current'] as const,
  dailySummary: (date: string) => [...todayQueryKeys.targets(date), 'daily-summary'] as const,

  // 栄養関連
  nutrition: (date: string) => [...todayQueryKeys.all(date), 'nutrition'] as const,
  mealNutrition: (date: string, mealType: string, mealIndex?: number) => [
    ...todayQueryKeys.nutrition(date),
    'meal',
    mealType,
    ...(mealIndex !== undefined ? [mealIndex] : [])
  ] as const,

  // レポート関連
  reports: (date: string) => [...todayQueryKeys.all(date), 'reports'] as const,
  dailyReport: (date: string) => [...todayQueryKeys.reports(date), 'daily'] as const,

  // プロフィール関連（日付に依存しない）
  profile: () => ['profile', 'me'] as const,
} as const;

/**
 * 特定日付の全データを無効化
 */
export const invalidateAllTodayData = (date: string) => todayQueryKeys.all(date);

/**
 * 食事データのみを無効化
 */
export const invalidateMealData = (date: string) => todayQueryKeys.meals(date);

/**
 * 栄養データのみを無効化
 */
export const invalidateNutritionData = (date: string) => todayQueryKeys.nutrition(date);