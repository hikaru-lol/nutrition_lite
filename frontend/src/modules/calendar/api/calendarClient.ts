import { clientApiFetch } from '@/shared/api/client';
import {
  MonthlyCalendarResponseSchema,
  MonthlyCalendarQuerySchema,
  type MonthlyCalendarResponse,
  type MonthlyCalendarQuery,
} from '../contract/calendarContract';

/**
 * 月次カレンダーデータを取得
 * @param year 年（2000-3000）
 * @param month 月（1-12）
 * @returns 月次カレンダーデータ
 */
export async function fetchMonthlyCalendar(
  year: number,
  month: number
): Promise<MonthlyCalendarResponse> {
  // パラメータをバリデーション
  const query: MonthlyCalendarQuery = MonthlyCalendarQuerySchema.parse({
    year,
    month,
  });

  // クエリパラメータを構築
  const params = new URLSearchParams({
    year: String(query.year),
    month: String(query.month),
  });

  // API呼び出し (BFFが開発環境の切り替えを処理)
  const raw = await clientApiFetch<unknown>(
    `/calendar/monthly-summary?${params.toString()}`,
    {
      method: 'GET',
    }
  );

  // レスポンスをバリデーション
  return MonthlyCalendarResponseSchema.parse(raw);
}