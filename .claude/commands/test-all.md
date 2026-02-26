---
description: すべてのテストを実行（バックエンド・フロントエンド）
---

プロジェクトのすべてのテストを実行してください。

## バックエンドテスト

### 1. ユニットテスト
```bash
cd backend
uv run pytest -m "not real_integration" tests/unit/ -v
```

### 2. 統合テスト（Fake実装）
```bash
cd backend
uv run pytest -m "not real_integration" tests/integration/ -v
```

### 3. 実統合テスト（実インフラ）
```bash
cd backend
# PostgreSQL と MinIO が起動している必要があります
uv run pytest -m "real_integration" tests/integration_real/ -v --maxfail=1
```

### 4. 型チェック
```bash
cd backend
uv run mypy app
```

### 5. Lint
```bash
cd backend
uv run ruff check
uv run ruff format --check
```

## フロントエンドテスト

### 1. 型チェック
```bash
cd frontend
pnpm typecheck
```

### 2. Lint
```bash
cd frontend
pnpm lint
```

### 3. ビルドテスト
```bash
cd frontend
pnpm build
```

## 実行順序

1. まずLintとフォーマットチェック
2. 型チェック
3. ユニットテスト
4. 統合テスト
5. ビルドテスト

## 成功基準

- すべてのテストがPASS
- 型エラーなし
- Lintエラーなし
- ビルドエラーなし

$ARGUMENTS