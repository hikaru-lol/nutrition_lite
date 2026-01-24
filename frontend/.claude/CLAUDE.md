# Frontend Project Memory (Entry)

このセッションは **/frontend のみ**が対象。
../backend は read/write しない（permissions deny 済み）。

## 絶対ルール（崩さない）

- 依存方向：UI（modules/_/ui） → PageModel（modules/_/model） → API（modules/\*/api） → shared/api（fetcher） → BFF（src/app/api） → Backend
- UI は PageModel（hooks）だけを見る（API 直叩き/直 import 禁止）
- Backend 直叩き禁止（必ず BFF /api/\* 経由）
- server-only 混入禁止（client から server-only / next/headers を import しない）
- any 禁止（unknown → 正規化）
- (group) による URL 衝突を作らない

## 作業の出力フォーマット（毎回これ）

1. Plan（設計/方針）
2. 変更ファイル一覧
3. 実装（差分）
4. 検証コマンド（pnpm lint/typecheck/test）

詳細固定コンテキスト：
@docs/ai/CONTEXT.md

Feature Pack テンプレ：
@docs/ai/feature-pack-template.md
