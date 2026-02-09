/**
 * Today Module - Public API
 *
 * Todayページに関連する公開インターフェース
 */

// ========================================
// Components
// ========================================

export { TodayPage } from './ui/TodayPage';

// ========================================
// Hooks - Layer 3 & 4
// ========================================

// Layer 3: Page Aggregation
export { useTodayPageModel } from './model/useTodayPageModel';

// Layer 4: Feature Logic
export { useTodayNutritionCalculator } from './hooks/useTodayNutritionCalculator';
export { useDailyReportManager } from './hooks/useDailyReportManager';

// ========================================
// Types
// ========================================

export type {
  NutrientProgress,
  TodayMealItemFormValues,
} from './contract/todayContract';

export type {
  TodayNutritionCalculatorModel,
} from './hooks/useTodayNutritionCalculator';

export type {
  DailyReportManagerModel,
} from './hooks/useDailyReportManager';

// ========================================
// Utilities
// ========================================

export { formatLocalDateYYYYMMDD } from './contract/todayContract';
