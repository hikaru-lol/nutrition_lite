// frontend/lib/api/targets.ts
import { apiGet, apiPost, apiPatch } from './client';

export type GoalType =
  | 'weight_loss'
  | 'maintain'
  | 'weight_gain'
  | 'health_improve';

export type ActivityLevel = 'low' | 'normal' | 'high';

export type NutrientCode =
  | 'carbohydrate'
  | 'fat'
  | 'protein'
  | 'water'
  | 'fiber'
  | 'sodium'
  | 'iron'
  | 'calcium'
  | 'vitamin_d'
  | 'potassium';

export type NutrientSource = 'llm' | 'manual' | 'user_input' | 'aggregated';

export type TargetNutrientApi = {
  code: NutrientCode;
  amount: number;
  unit: string;
  source: NutrientSource;
};

export type TargetResponseApi = {
  id: string;
  user_id: string;
  title: string;
  goal_type: GoalType;
  goal_description: string | null;
  activity_level: ActivityLevel;
  is_active: boolean;
  nutrients: TargetNutrientApi[];
  llm_rationale: string | null;
  disclaimer: string | null;
  created_at: string;
  updated_at: string;
};

export type TargetListResponseApi = {
  items: TargetResponseApi[];
};

export type CreateTargetRequestApi = {
  title: string;
  goal_type: GoalType;
  goal_description?: string | null;
  activity_level: ActivityLevel;
};

export async function fetchTargets(): Promise<TargetResponseApi[]> {
  const res = await apiGet<TargetListResponseApi>('/targets');
  return res.items;
}

export async function fetchActiveTarget(): Promise<TargetResponseApi> {
  return apiGet<TargetResponseApi>('/targets/active');
}

export async function createTarget(
  body: CreateTargetRequestApi
): Promise<TargetResponseApi> {
  return apiPost<TargetResponseApi>('/targets', body);
}

export async function activateTarget(
  targetId: string
): Promise<TargetResponseApi> {
  return apiPost<TargetResponseApi>(`/targets/${targetId}/activate`);
}
