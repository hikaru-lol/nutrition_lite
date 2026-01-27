import { clientApiFetch } from '@/shared/api/client';
import {
  TodaySummarySchema,
  type TodaySummary,
} from '../contract/todayContract';

export async function fetchTodaySummary(date: string): Promise<TodaySummary> {
  const raw = await clientApiFetch<unknown>(
    `/today?date=${encodeURIComponent(date)}`
  );
  return TodaySummarySchema.parse(raw);
}
