// src/shared/api/contracts/target.ts
export type TargetGenerateRequest = {
  goal: 'lose' | 'maintain' | 'gain';
  activity_level: 'low' | 'medium' | 'high';
  dietary_preference?: 'none' | 'vegetarian' | 'vegan';
};

export type TargetSummary = {
  calories: number;
  protein_g: number;
  fat_g: number;
  carbs_g: number;
};

export type TargetGenerateResponse = {
  result: TargetSummary;
};

export type TargetSaveRequest = {
  target: TargetSummary;
};

export type TargetSaveResponse = {
  ok: boolean;
  target: TargetSummary;
};
