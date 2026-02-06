// ========================================
// Public API Exports
// ========================================

// Main Page Component
export { TodayPage } from './ui/TodayPage';
export { TodayPageContent } from './ui/TodayPageContent';

// Current Implementation Model (5-layer architecture)
export { useTodayPageModel } from './model/useTodayPageModel';
export { useTodayNutritionProgress } from './hooks/useTodayNutritionProgress';

// Layer 4: Feature Logic
export { useDailyReportManagement } from './hooks/useDailyReportManagement';
export type { DailyReportManagementModel } from './hooks/useDailyReportManagement';

// Layer 2: UI Orchestration
export { useNutritionAnalysisState } from './ui/hooks/useNutritionAnalysisState';
export type { NutritionAnalysisStateModel } from './ui/hooks/useNutritionAnalysisState';

// Services (Layer 5)
export { useNutritionService } from '../nutrition/services/nutritionService';
export { useNutritionProgressService } from '../nutrition-progress/services/nutritionProgressService';
export { useTargetService } from '../target/services/targetService';
export { useMealService } from '../meal/services/mealService';

// Types
export type {
  TodayNutritionProgressModel,
  NutrientProgress,
} from './hooks/useTodayNutritionProgress';

export type {
  NutritionDetailsData,
} from '../nutrition/types/nutritionTypes';

// Utility Functions
export { formatLocalDateYYYYMMDD } from './types/todayTypes';
