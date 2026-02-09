// ========================================
// Public API Exports
// ========================================

// Contracts & Types
export * from './contract/mealContract';

// API Client
export * from './api/mealClient';

// Services (Layer 5)
export { useMealService } from './services/mealService';
export type { MealIdentifier, MealSection, MealValidationResult } from './services/mealService';

// Feature Logic (Layer 4)
export * from './hooks/mealOptimisticMutations';

export { useMealManager } from './hooks/useMealManager';
export type { MealManagerModel } from './hooks/useMealManager';

export { useMealCompletionCalculator } from './hooks/useMealCompletionCalculator';
export type { MealCompletionCalculatorModel, MealCompletionStatus } from './hooks/useMealCompletionCalculator';
