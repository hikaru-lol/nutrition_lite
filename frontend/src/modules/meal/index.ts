// ========================================
// Public API Exports
// ========================================

// Contracts & Types
export * from './contract/mealContract';

// API Client
export * from './api/mealClient';

// Legacy Model (段階的移行中)
export * from './model/mealHooks';

// Services (Layer 5)
export { useMealService } from './services/mealService';
export type { MealIdentifier, MealSection, MealValidationResult } from './services/mealService';

// Feature Logic (Layer 4)
export { useMealManagement } from './hooks/useMealManagement';
export type { MealManagementModel } from './hooks/useMealManagement';

export { useMealCompletionStatus } from './hooks/useMealCompletionStatus';
export type { MealCompletionStatusModel, MealCompletionStatus } from './hooks/useMealCompletionStatus';
