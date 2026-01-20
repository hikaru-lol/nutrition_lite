// src/modules/report/api/types.ts

export type GenerateDailyReportRequest = {
  date: string; // YYYY-MM-DD
};

export type DailyNutritionReportResponse = {
  date: string; // YYYY-MM-DD
  summary: string;
  good_points: string[];
  improvement_points: string[];
  tomorrow_focus: string[];
  created_at: string; // ISO date-time
};
