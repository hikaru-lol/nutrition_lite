# Feature Pack Template

## 目的（1 行）

- 例：ユーザーがオンボーディングでターゲットを生成し保存できるようにする

## 画面責務（1 行）

- 例：入力 → 生成 → 確認 → 保存までの状態遷移を提供する

## ViewState（union）

- idle
- loading
- success
- error
  （必要に応じて submitting / empty / unauthorized など追加）

## API（BFF endpoint + contract）

- BFF: /api/...
- contract: Zod schema（request/response）
- error: 正規化された AppError（unknown のまま扱わない）

## Acceptance Criteria（2〜5 行）

- 例：ログイン済みでアクセスするとフォームが表示される
- 例：生成を押すと loading → success に遷移し結果が表示される
- 例：保存で /api/... が 200 になり次画面へ遷移する

## Edge/Failure

- 認証切れ → login へ誘導
- ネットワークエラー → ErrorState
- 空データ → EmptyState

## 変更してよい範囲（必須）

- src/modules/<feature>/\*\*
- src/app/api/\*\*
- src/shared/api/\*\*（fetcher/正規化のみ）

## 禁止（必須）

- backend 直叩き禁止（必ず BFF 経由）
- UI から API 直呼び禁止（PageModel 経由）
- server-only 混入禁止
- any 禁止
- (group) による URL 衝突を作らない
