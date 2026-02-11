/**
 * チュートリアル機能のContract層
 * バックエンドAPIとの型安全な通信を保証
 */

import { z } from 'zod';

// ===== チュートリアルID定義 =====
export const TutorialIds = [
  'onboarding_profile',   // プロフィール設定オンボーディング
  'onboarding_target',    // 目標設定オンボーディング
  'feature_today',        // 今日の食事記録機能紹介
  'feature_calendar',     // カレンダー機能紹介
  'feature_nutrition',    // 栄養分析機能紹介
] as const;

export type TutorialId = typeof TutorialIds[number];

// ===== Zodスキーマ定義 =====

/**
 * チュートリアル完了状況レスポンス
 * GET /api/tutorials/status
 */
export const TutorialStatusResponseSchema = z.object({
  completed: z.array(z.string()),
});

export type TutorialStatusResponse = z.infer<typeof TutorialStatusResponseSchema>;

/**
 * チュートリアル完了レスポンス
 * POST /api/tutorials/{id}/complete
 */
export const TutorialCompleteResponseSchema = z.object({
  tutorial_id: z.string(),
  completed_at: z.string(), // ISO datetime string
});

export type TutorialCompleteResponse = z.infer<typeof TutorialCompleteResponseSchema>;

// ===== react-joyride用の型定義 =====

/**
 * チュートリアルステップ定義
 */
export interface TutorialStep {
  target: string;          // セレクタ (例: '[data-tour="profile-form"]')
  content: string;         // 説明文
  title?: string;          // タイトル
  placement?: 'top' | 'bottom' | 'left' | 'right' | 'center';
  disableBeacon?: boolean; // ビーコンを無効化
}

/**
 * チュートリアル定義
 */
export interface TutorialDefinition {
  id: TutorialId;
  title: string;
  description: string;
  steps: TutorialStep[];
  autoStart?: boolean;     // 自動開始するか
  triggerSelector?: string; // 手動起動ボタンのセレクタ
}

// ===== 状態管理用の型 =====

/**
 * チュートリアルの実行状態
 */
export interface TutorialState {
  completedTutorials: TutorialId[];  // 完了済みチュートリアル
  currentTutorial: TutorialId | null; // 現在実行中のチュートリアル
  isRunning: boolean;                // チュートリアル実行中フラグ
  isLoading: boolean;                // ローディング状態
}

// ===== ユーティリティ型 =====

/**
 * チュートリアル完了確認
 */
export function isTutorialCompleted(
  tutorialId: TutorialId,
  completedTutorials: TutorialId[]
): boolean {
  return completedTutorials.includes(tutorialId);
}

/**
 * 有効なチュートリアルIDかチェック
 */
export function isValidTutorialId(id: string): id is TutorialId {
  return TutorialIds.includes(id as TutorialId);
}