/**
 * チュートリアル機能のAPIクライアント
 * BFF (Next.js API Routes) 経由でバックエンドと通信
 */

import { clientApiFetch } from '@/shared/api/client';
import {
  type TutorialId,
  type TutorialStatusResponse,
  type TutorialCompleteResponse,
  TutorialStatusResponseSchema,
  TutorialCompleteResponseSchema,
} from '../contract/tutorialContract';

/**
 * チュートリアル完了状況を取得
 * GET /api/tutorials/status
 */
export async function fetchTutorialStatus(): Promise<TutorialStatusResponse> {
  const response = await clientApiFetch<unknown>('/tutorials/status');

  // レスポンスの型安全性を保証
  return TutorialStatusResponseSchema.parse(response);
}

/**
 * チュートリアルを完了済みとしてマーク
 * POST /api/tutorials/{id}/complete
 */
export async function completeTutorial(
  tutorialId: TutorialId
): Promise<TutorialCompleteResponse> {
  const response = await clientApiFetch<unknown>(`/tutorials/${tutorialId}/complete`, {
    method: 'POST',
  });

  // レスポンスの型安全性を保証
  return TutorialCompleteResponseSchema.parse(response);
}

/**
 * 指定されたチュートリアルが完了済みかチェック
 */
export async function isTutorialCompleted(tutorialId: TutorialId): Promise<boolean> {
  const status = await fetchTutorialStatus();
  return status.completed.includes(tutorialId);
}

/**
 * 完了済みチュートリアル数を取得
 */
export async function getCompletedTutorialCount(): Promise<number> {
  const status = await fetchTutorialStatus();
  return status.completed.length;
}