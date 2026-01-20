// src/modules/target/model/targetGeneratorPageModel.ts

export type TargetGeneratorForm = {
  goal: 'lose' | 'maintain' | 'gain';
  activityLevel: 'low' | 'medium' | 'high';
  constraints?: {
    // 例: vegetarian / allergies / budget / etc（必要最低限だけ）
    dietaryPreference?: 'none' | 'vegetarian' | 'vegan';
  };
};

// 生成結果の最小表現（Data Contract へ寄せる）
export type GeneratedTargetSummary = {
  calories: number;
  protein_g: number;
  fat_g: number;
  carbs_g: number;
};

// ViewState: 画面の全状態（漏れなく）
export type TargetGeneratorViewState =
  | { type: 'loading_initial' } // 初期ロード（profile/target確認）
  | { type: 'needs_profile' } // Profile未作成
  | { type: 'ready'; form: TargetGeneratorForm; canGenerate: boolean }
  | { type: 'generating'; form: TargetGeneratorForm }
  | {
      type: 'generated';
      form: TargetGeneratorForm;
      result: GeneratedTargetSummary;
    }
  | {
      type: 'saving';
      form: TargetGeneratorForm;
      result: GeneratedTargetSummary;
    }
  | { type: 'saved'; result: GeneratedTargetSummary } // 保存完了
  | { type: 'unauthorized' } // 401/403
  | {
      type: 'error';
      message: string;
      retryAction: 'init' | 'generate' | 'save';
      form?: TargetGeneratorForm;
      result?: GeneratedTargetSummary;
    };

export type UseTargetGeneratorPageModel = {
  viewState: TargetGeneratorViewState;

  // UI操作（Viewから呼ぶ）
  setForm: (patch: Partial<TargetGeneratorForm>) => void;
  generate: () => Promise<void>;
  regenerate: () => Promise<void>;
  save: () => Promise<void>;
  retry: () => Promise<void>;
};
