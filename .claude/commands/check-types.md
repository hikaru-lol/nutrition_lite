---
description: 型チェックとLintを実行（フロントエンド・バックエンド）
---

プロジェクト全体の型チェックとLintを実行してください。

## フロントエンド

### 型チェック
```bash
cd frontend
pnpm typecheck
```

### Lint
```bash
cd frontend
pnpm lint
```

### 自動修正
```bash
cd frontend
pnpm lint --fix
```

## バックエンド

### 型チェック（mypy）
```bash
cd backend
uv run mypy app
```

### Lint（ruff）
```bash
cd backend
uv run ruff check
```

### フォーマット確認
```bash
cd backend
uv run ruff format --check
```

### 自動修正
```bash
cd backend
uv run ruff check --fix
uv run ruff format
```

## チェック項目

### TypeScript/React
- 型エラーがないこと
- `any`型を使用していないこと（`unknown`を使用）
- ESLintルールに準拠
- 未使用のimportがないこと
- React Hook依存配列が正しいこと

### Python/FastAPI
- 型アノテーションが正しいこと
- Pydantic モデルの検証
- 未使用のimportがないこと
- PEP 8準拠のフォーマット
- docstringの有無（重要な関数）

## エラーが出た場合

1. **型エラー**
   - 明示的な型アノテーションを追加
   - 型ガードを使用
   - ジェネリクスを適切に指定

2. **Lintエラー**
   - 自動修正可能なものは`--fix`オプションで修正
   - 手動修正が必要なものは個別に対応

3. **フォーマットエラー**
   - 自動フォーマッタを実行

## CI/CDでの実行

これらのチェックはGitHub Actionsでも自動実行されます。
プッシュ前にローカルで実行することを推奨します。

$ARGUMENTS