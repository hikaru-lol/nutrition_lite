// Client-safe exports only
export { CalendarPage } from './ui/CalendarPage';
export { useCalendarModel } from './model/useCalendarModel';

// Re-export types for convenience
export type {
  CalendarDaySnapshot,
  MonthlyCalendarResponse,
  MonthlyCalendarQuery,
} from './contract/calendarContract';