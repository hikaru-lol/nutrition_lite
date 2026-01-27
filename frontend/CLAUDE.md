# フロントエンド

## アーキテクチャ

- FSD + BFF の図解
- 依存方向のルール

## ディレクトリ規約

- modules/, app/, shared/ 等の役割

## 既存モジュール一覧

- 現在あるモジュールのリスト

## ルーティング

- パスとルートグループの対応

## 新規モジュール作成チェックリスト

- 何を作る必要があるか

## 詳細ルール参照先

- .cursor/rules/10-_, 20-_, 30-_, 40-_, 50-\* への参照

```

**なぜ必要か：**
- Feature Sliced Designは独自の構造なので、明示的に説明が必要
- BE作業時には不要な情報なので、分離しておく

---

### CLAUDE.mdの階層的な読み込み
```

/workspace で起動
→ /workspace/CLAUDE.md を読む

/workspace/backend で起動
→ /workspace/CLAUDE.md を読む
→ /workspace/backend/CLAUDE.md を読む（より具体的な情報で補完）

/workspace/frontend で起動
→ /workspace/CLAUDE.md を読む
→ /workspace/frontend/CLAUDE.md を読む
