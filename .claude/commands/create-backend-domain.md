---
description: バックエンドに新しいドメインを作成（クリーンアーキテクチャ構成）
---

バックエンドに新しいドメイン「$ARGUMENTS」を作成してください。

## 作成するファイル構成

```
backend/app/
├── domain/$ARGUMENTS/
│   ├── __init__.py
│   ├── entities.py      # エンティティ定義
│   ├── value_objects.py # 値オブジェクト定義
│   └── errors.py        # ドメインエラー定義
│
├── application/$ARGUMENTS/
│   ├── __init__.py
│   ├── dto/
│   │   ├── __init__.py
│   │   └── $ARGUMENTS_dto.py
│   ├── ports/
│   │   ├── __init__.py
│   │   ├── $ARGUMENTS_repository_port.py
│   │   └── $ARGUMENTS_uow_port.py
│   ├── use_cases/
│   │   ├── __init__.py
│   │   ├── create_$ARGUMENTS.py
│   │   ├── get_$ARGUMENTS.py
│   │   ├── update_$ARGUMENTS.py
│   │   └── delete_$ARGUMENTS.py
│   └── errors.py
│
├── infra/db/
│   ├── models/
│   │   └── $ARGUMENTS_model.py
│   ├── repositories/
│   │   └── $ARGUMENTS_repository.py
│   └── uow/
│       └── $ARGUMENTS.py
│
└── api/http/
    ├── routers/
    │   └── $ARGUMENTS_route.py
    ├── schemas/
    │   └── $ARGUMENTS.py
    └── mappers/
        └── $ARGUMENTS_mapper.py
```

## 実装の流れ

1. **Domain層**
   - エンティティを定義（ID、必須フィールド）
   - 値オブジェクトを定義（Email、Status等）
   - ドメインエラーを定義（NotFound、Invalid等）

2. **Application層**
   - DTOを定義（入出力データ構造）
   - ポート（インターフェース）を定義
   - ユースケースを実装（ビジネスロジック）

3. **Infrastructure層**
   - SQLAlchemyモデルを定義
   - リポジトリ実装（ポートを実装）
   - Unit of Work実装

4. **API層**
   - Pydanticスキーマを定義
   - FastAPIルーターを実装
   - DTO⇔スキーマのマッパーを実装

5. **DI Container**
   - `di/container.py`に依存性を登録

6. **テスト**
   - ユニットテストを作成
   - 統合テストを作成

## 命名規則

- エンティティ: `${Name}Definition`
- 値オブジェクト: `${Name}Id`, `${Name}Status`
- ユースケース: `${Action}${Name}UseCase`
- リポジトリ: `${Name}RepositoryPort` / `SqlAlchemy${Name}Repository`
- DTO: `${Name}DTO`, `Create${Name}InputDTO`
- エラー: `${Name}NotFoundError`, `Invalid${Name}Error`

$ARGUMENTS