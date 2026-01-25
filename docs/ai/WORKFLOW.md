# Workflow (Doc-in-Code / 安定量産)

## 1) Feature Pack を作る

- `docs/ai/FEATURE_PACK_TEMPLATE.md` を複製して `docs/ai/FEATURE_PACK.md` を作る
- 今回タスクの情報を埋める（目的/AC/変更対象/検証）

## 2) Plan → Patch → Verify

- Cursor に Context + 関連ファイルを @ で渡す
- まず Plan のみ
- 小さめ単位で patch
- lint/test を実行し、失敗ログを渡して修正

## 3) 最終レビュー（チェックリスト）

- FE: UI→Model→API→shared/api→BFF を守っている
- FE: server-only 混入がない
- FE: URL 衝突を作っていない
- BE: Clean Arch 依存方向を守っている
- Cross: OpenAPI/Contracts/BFF/Client を同期している
