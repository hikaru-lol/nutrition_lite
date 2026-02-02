import { z } from 'zod';

/**
 * カレンダー機能のAPI契約定義
 * バックエンドAPIスキーマとの整合性を保つ
 */

// カレンダー日次スナップショット
export const CalendarDaySnapshotSchema = z.object({
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'YYYY-MM-DD形式である必要があります'),
  has_meal_logs: z.boolean(),
  nutrition_achievement: z.number().nullable(),
  has_daily_report: z.boolean(),
});

// 月次カレンダーレスポンス
export const MonthlyCalendarResponseSchema = z.object({
  year: z.number().int().min(2000).max(3000),
  month: z.number().int().min(1).max(12),
  days: z.array(CalendarDaySnapshotSchema),
});

// 月次カレンダークエリパラメータ
export const MonthlyCalendarQuerySchema = z.object({
  year: z.number().int().min(2000).max(3000),
  month: z.number().int().min(1).max(12),
});

// TypeScript型を導出
export type CalendarDaySnapshot = z.infer<typeof CalendarDaySnapshotSchema>;
export type MonthlyCalendarResponse = z.infer<typeof MonthlyCalendarResponseSchema>;
export type MonthlyCalendarQuery = z.infer<typeof MonthlyCalendarQuerySchema>;

/**
 * UI層で使用するCalendarDayData型への変換関数
 */
export function toCalendarDayData(
  snapshot: CalendarDaySnapshot,
  isToday: boolean,
  isSelected: boolean
): import('@/shared/ui/calendar/Calendar').CalendarDayData {
  return {
    date: snapshot.date,
    hasMeals: snapshot.has_meal_logs,
    mealCount: undefined, // バックエンドから提供されていない
    goalAchievementPercentage: snapshot.nutrition_achievement ?? undefined,
    hasReport: snapshot.has_daily_report,
    isToday,
    isSelected,
  };
}