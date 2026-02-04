// Public exports for meal-recommendation module

// UI Components
export { MealRecommendationCard } from './ui/MealRecommendationCard';
export { MealRecommendationDetailModal } from './ui/MealRecommendationDetailModal';

// Hooks
export { useMealRecommendationModel } from './model/useMealRecommendationModel';

// Types & Contracts
export type {
  MealRecommendation,
  RecommendedMeal,
  MealRecommendationCardState,
  GenerateMealRecommendationRequest,
  GenerateMealRecommendationResponse,
  GetMealRecommendationResponse,
  ListMealRecommendationsResponse,
} from './contract/mealRecommendationContract';

export {
  MealRecommendationCooldownError,
  MealRecommendationDailyLimitError,
} from './contract/mealRecommendationContract';

// API
export { mealRecommendationApi } from './api/mealRecommendationClient';