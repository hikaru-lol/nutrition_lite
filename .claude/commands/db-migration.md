---
description: データベースマイグレーションの作成と実行
---

データベースマイグレーションを作成・実行してください。

## マイグレーション作成

引数に応じて以下を実行：

### 新規マイグレーション作成（$ARGUMENTSがある場合）
```bash
cd backend
uv run alembic revision --autogenerate -m "$ARGUMENTS"
```

### マイグレーション実行
```bash
cd backend
uv run alembic upgrade head
```

## マイグレーションワークフロー

1. **モデル変更**
   - `backend/app/infra/db/models/`にSQLAlchemyモデルを追加・変更

2. **マイグレーション生成**
   ```bash
   uv run alembic revision --autogenerate -m "add_new_table"
   ```

3. **マイグレーションファイル確認**
   - `backend/alembic/versions/`に生成されたファイルを確認
   - 必要に応じて手動で修正

4. **マイグレーション実行**
   ```bash
   uv run alembic upgrade head
   ```

5. **ロールバック（必要時）**
   ```bash
   # 1つ前に戻る
   uv run alembic downgrade -1

   # 特定のリビジョンに戻る
   uv run alembic downgrade <revision>
   ```

## 現在の状態確認

```bash
# 現在のリビジョン
uv run alembic current

# 履歴表示
uv run alembic history

# 次に実行されるマイグレーション
uv run alembic show head
```

## 注意事項

- **本番環境**では必ずバックアップを取ってから実行
- **破壊的変更**（カラム削除、型変更）は慎重に
- **インデックス追加**は大規模テーブルでは時間がかかる
- **NOT NULL制約追加**は既存データを考慮

## トラブルシューティング

### マイグレーションが失敗した場合
1. エラーメッセージを確認
2. 必要に応じてロールバック
3. マイグレーションファイルを修正
4. 再実行

### テーブルが既に存在する場合
1. `alembic stamp head`で現在の状態をマーク
2. または手動でテーブルを削除してから実行

$ARGUMENTS