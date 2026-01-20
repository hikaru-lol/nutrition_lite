/**
 * Target Generator (Onboarding)
 *
 * Responsibility:
 * - Profile を前提に、栄養目標(Target)を自動生成し、確認して保存する。
 *
 * UI Spec:
 * - 入力: 目的(goal)・活動量(activityLevel)・制約(optional) を指定できる
 * - 操作: Generate / Regenerate / Save
 * - 表示: 生成結果のサマリ（Calories, PFC）と必要なら主要項目
 * - 共通状態: Loading / Empty / Error / Unauthorized は shared/ui を使う
 *
 * Acceptance Criteria:
 * - AC1: 必須入力が不足している場合 Generate は実行できず理由が表示される
 * - AC2: Generate 中はローディング表示＋二重送信不可（連打しても1回のみ）
 * - AC3: 生成成功時、主要目標（Calories/PFC）が読みやすく表示される
 * - AC4: Save 成功時、完了が明確（Toast 等）で、再読込しても保持される
 * - AC5: Profile 未作成は needs_profile として扱い Profile 作成導線を提示する
 * - AC6: 401/403 は unauthorized として扱い login もしくは適切な導線を提示する
 * - AC7: 5xx/timeout は error でリトライ可能。生成結果/入力は不必要に消えない
 *
 * Edge/Failure (top 3):
 * - E1: needs_profile（Profileが存在しない/不完全）
 * - E2: unauthorized（認証切れ・権限なし）
 * - E3: api_error（生成/保存の失敗、タイムアウト）
 */

export function TargetGeneratorPage() {
  // const m = useTargetGeneratorPageModel()
  // switch (m.viewState.type) {
  //   case 'loading_initial': return <PageSkeleton ... />
  //   case 'needs_profile':   return <EmptyState ... profile導線 />
  //   case 'ready':           return <Form ... Generate disabled={!canGenerate} />
  //   case 'generating':      return <Form ... loading />
  //   case 'generated':       return <Result ... Save />
  //   case 'saving':          return <Result ... saving />
  //   case 'saved':           return <Success ... next CTA to /app/today />
  //   case 'unauthorized':    return <ErrorState ... login導線 />
  //   case 'error':           return <ErrorState ... retry button calls m.retry />
  // }
}
