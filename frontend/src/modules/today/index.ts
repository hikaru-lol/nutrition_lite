// ========================================
// Public API Exports
// ========================================

// Main Page Component
export { TodayPage } from './ui/TodayPage';

// Legacy Model (Phase 6で削除予定)
export { useTodayPageModel } from './model/useTodayPageModel';

// ========================================
// New Architecture Exports (Phase 5+)
// ========================================

// Context & Hooks
export { TodayPageProvider, useTodayPageContext } from './context/TodayPageContext';
export {
  useTodayMeals,
  useTodayTargets,
  useTodayNutrition,
  useTodayReports,
  useTodayProfile,
  useTodayModals,
} from './context/TodayPageContext';

// Domain Hooks (直接利用も可能)
export { useTodayMeals as useTodayMealsDirect } from './model/useTodayMeals';
export { useTodayTargets as useTodayTargetsDirect } from './model/useTodayTargets';
export { useTodayNutrition as useTodayNutritionDirect } from './model/useTodayNutrition';
export { useTodayReports as useTodayReportsDirect } from './model/useTodayReports';
export { useTodayProfile as useTodayProfileDirect } from './model/useTodayProfile';
export { useTodayModals as useTodayModalsDirect } from './model/useTodayModals';

// Integrated Data Hook
export { useTodayPageData } from './model/useTodayPageData';

// Layout Components
export { TodayPageLayout } from './ui/TodayPageLayout';

// Section Components
export {
  DailySummarySection,
  CaloriesSummarySection,
  PFCSummarySection,
} from './ui/sections/DailySummarySection';

export {
  MealListSection,
  MealCountSection,
  LatestMealSection,
} from './ui/sections/MealListSection';

export {
  TargetProgressSection,
  PFCProgressSection,
  TargetAchievementSection,
} from './ui/sections/TargetProgressSection';

export {
  DailyReportSection,
  ReportStatusSection,
  ReportGenerateSection,
} from './ui/sections/DailyReportSection';

export {
  TodayModalsContainer,
  SpecificModalContainer,
} from './ui/sections/TodayModalsContainer';

// Types
export type {
  TodayPageContextValue,
  TodayMealsModel,
  TodayTargetsModel,
  TodayNutritionModel,
  TodayReportsModel,
  TodayProfileModel,
  TodayModalsModel,
  MigrationFlags,
} from './types/todayTypes';

// Query Keys
export { todayQueryKeys } from './lib/queryKeys';

// ========================================
// Development & Testing (開発環境のみ)
// ========================================

// テスト用コンポーネント
export { TodayPageTest } from './ui/TodayPageTest';
export { TodayPageMigrationTest } from './ui/TodayPageMigrationTest';

// Utility Functions
export { formatLocalDateYYYYMMDD } from './types/todayTypes';
