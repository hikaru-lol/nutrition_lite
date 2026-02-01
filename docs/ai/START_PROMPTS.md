# Cursor スタートプロンプト（コピペ）

## A) Frontend: Plan only

@docs/ai/frontend/CONTEXT.md
@docs/ai/FEATURE_PACK.md
@frontend/src/...（入口 + 周辺 2〜3 ファイル）

「まず Plan のみ。変更ファイル一覧、方針、リスク、テスト方針を出して」

## B) Backend: Plan only

@docs/ai/backend/CONTEXT.md
@docs/ai/FEATURE_PACK.md
@backend/...（入口 + 周辺）

「まず Plan のみ。変更ファイル一覧、方針、リスク、テスト方針を出して」

## C) Implement

「上の Plan に沿って最小差分で実装して。最後に Verify（コマンド/テスト）を書いて」

## D) Fix failures

「このエラーログを直して。原因 → 修正 → 必要なら追加テスト → 再実行コマンドの順で」
