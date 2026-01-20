// src/modules/target/api/types.ts

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

export type TargetNutrient = {
  code: NutrientCode;
  amount: number;
  unit: string;
  source: NutrientSource;
};

export type TargetResponse = {
  id: string;
  user_id: string;
  title: string;
  goal_type: GoalType;
  goal_description: string | null;
  activity_level: ActivityLevel;
  is_active: boolean;
  nutrients: TargetNutrient[];
  llm_rationale: string | null;
  disclaimer: string | null;
  created_at: string;
  updated_at: string;
};

export type TargetListResponse = {
  items: TargetResponse[];
};

export type CreateTargetRequest = {
  title: string;
  goal_type: GoalType;
  goal_description?: string | null;
  activity_level: ActivityLevel;
};

export type UpdateTargetNutrient = {
  code: NutrientCode;
  amount?: number | null;
  unit?: string | null;
};

export type UpdateTargetRequest = {
  title?: string | null;
  goal_type?: GoalType; // nullable指定なしのため null は基本入れない想定
  goal_description?: string | null;
  activity_level?: ActivityLevel;
  llm_rationale?: string | null;
  disclaimer?: string | null;
  nutrients?: UpdateTargetNutrient[] | null;
};
