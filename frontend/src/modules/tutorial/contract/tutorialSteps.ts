/**
 * チュートリアルステップ定義
 * 各チュートリアルの表示内容とターゲット要素を定義
 */

import type { TutorialId } from './tutorialContract';
import type { Step } from 'react-joyride';

// ========================================
// Tutorial Steps Definition
// ========================================

export const TUTORIAL_STEPS: Record<TutorialId, Step[]> = {
  feature_today: [
    {
      target: '[data-tour="today-title"]',
      content: 'ここはTodayページです。今日の栄養状況を一目で確認できます。',
      placement: 'bottom' as const,
      disableBeacon: true,
    },
    {
      target: '[data-tour="daily-summary"]',
      content: '本日のサマリーカードです。摂取カロリーや主要栄養素の情報が表示されます。',
      placement: 'bottom' as const,
    },
    {
      target: '[data-tour="meal-list"]',
      content: '食事ログ一覧です。朝食・昼食・夕食・間食を追加・編集できます。「+」ボタンで新しい食事を追加しましょう。',
      placement: 'top' as const,
    },
    {
      target: '[data-tour="target-progress"]',
      content: '目標達成度が表示されます。設定した栄養目標に対する今日の摂取状況を確認できます。',
      placement: 'top' as const,
    },
    {
      target: '[data-tour="daily-report"]',
      content: 'AI生成の日次レポートです。食事内容を分析してアドバイスをもらえます。「レポートを生成する」ボタンでAI分析を開始できます。',
      placement: 'top' as const,
    },
  ],

  onboarding_profile: [
    {
      target: '[data-tour="profile-title"]',
      content: 'プロフィール設定へようこそ！栄養目標を正確に計算するために、基本的な情報を入力しましょう。',
      placement: 'bottom' as const,
      disableBeacon: true,
    },
    {
      target: '[data-tour="profile-sex"]',
      content: '性別を選択してください。基礎代謝の計算に使用されます。',
      placement: 'bottom' as const,
    },
    {
      target: '[data-tour="profile-birthdate"]',
      content: '生年月日を入力してください。年齢に応じた栄養所要量を計算します。',
      placement: 'bottom' as const,
    },
    {
      target: '[data-tour="profile-body"]',
      content: '身長と体重を入力してください。BMIや基礎代謝量の計算に必要です。',
      placement: 'top' as const,
    },
    {
      target: '[data-tour="profile-submit"]',
      content: '情報を保存すると、次の目標設定ページに進みます。後からも変更できます。',
      placement: 'top' as const,
    },
  ],

  onboarding_target: [
    {
      target: '[data-tour="target-title"]',
      content: 'ターゲット生成ページへようこそ！プロフィール情報を元に、個人に最適化された栄養目標を自動生成します。',
      placement: 'bottom' as const,
      disableBeacon: true,
    },
    {
      target: '[data-tour="target-title-field"]',
      content: 'ターゲットの名前を入力してください。後から管理しやすいよう、分かりやすい名前をつけましょう。',
      placement: 'bottom' as const,
    },
    {
      target: '[data-tour="target-goal-type"]',
      content: '目標タイプを選択してください。減量、増量、維持など、あなたの目標に合わせて選択すると、最適なカロリー設定が計算されます。',
      placement: 'bottom' as const,
    },
    {
      target: '[data-tour="target-activity-level"]',
      content: '日常の活動レベルを選択してください。これに基づいて必要な総カロリーが計算されます。',
      placement: 'bottom' as const,
    },
    {
      target: '[data-tour="target-description"]',
      content: '具体的な目標を入力することで、AIがより個人に合った栄養プランを提案できます（任意）。',
      placement: 'top' as const,
    },
    {
      target: '[data-tour="target-submit"]',
      content: 'すべての情報を入力したら、ターゲットを生成してください。AIがあなた専用の栄養目標を計算します。',
      placement: 'top' as const,
    },
  ],

  feature_calendar: [
    {
      target: '[data-tour="calendar-header"]',
      content: 'カレンダー機能へようこそ！過去や未来の日付を選択して、食事記録を確認・編集できます。',
      placement: 'bottom' as const,
      disableBeacon: true,
    },
    {
      target: '[data-tour="calendar-main"]',
      content: 'カレンダーで任意の日付をクリックすると、その日の詳細を確認できます。色付きの日付は食事記録がある日を示しています。',
      placement: 'right' as const,
    },
    {
      target: '[data-tour="calendar-date-info"]',
      content: '選択した日付の概要情報が表示されます。食事記録の有無、目標達成度、AIレポートの状況を一目で確認できます。',
      placement: 'top' as const,
    },
    {
      target: '[data-tour="calendar-detail-header"]',
      content: '選択日の詳細セクションです。ここにその日の食事記録、栄養分析、目標達成度が表示されます。',
      placement: 'left' as const,
    },
    {
      target: '[data-tour="daily-summary"]',
      content: 'Todayページと同じように、選択した日の栄養サマリーが表示されます。過去のデータも含めて分析できます。',
      placement: 'top' as const,
    },
  ],

  feature_nutrition: [
    {
      target: '[data-tour="daily-summary"]',
      content: '栄養分析機能へようこそ！ここでは日々の栄養状況を詳細に分析できます。まず本日のサマリーカードから始めましょう。',
      placement: 'bottom' as const,
      disableBeacon: true,
    },
    {
      target: '[data-tour="meal-list"]',
      content: '各食事の「分析」ボタンをクリックすると、その食事の詳細な栄養分析が表示されます。食事ごとの栄養バランスを確認できます。',
      placement: 'top' as const,
    },
    {
      target: '[data-tour="target-progress"]',
      content: '目標達成度チャートです。主要栄養素、ミネラル、ビタミンなどの摂取状況を視覚的に確認できます。',
      placement: 'top' as const,
    },
    {
      target: '[data-tour="daily-report"]',
      content: 'AI生成の日次レポートで、栄養バランスや改善点についてのアドバイスが得られます。「レポートを生成する」ボタンで分析を開始できます。',
      placement: 'top' as const,
    },
  ],
};

// ========================================
// Helper Functions
// ========================================

/**
 * 指定されたチュートリアルIDのステップを取得
 */
export function getTutorialSteps(tutorialId: TutorialId): Step[] {
  return TUTORIAL_STEPS[tutorialId] || [];
}

/**
 * 全チュートリアル数を取得
 */
export function getTutorialCount(): number {
  return Object.keys(TUTORIAL_STEPS).length;
}

/**
 * 全チュートリアルIDを取得
 */
export function getAllTutorialIds(): TutorialId[] {
  return Object.keys(TUTORIAL_STEPS) as TutorialId[];
}
