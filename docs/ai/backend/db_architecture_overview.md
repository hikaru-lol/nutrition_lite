ご提示いただいたバックエンドのDB関連処理の設計、非常に洗練されていますね。クリーンアーキテクチャの原則に基づき、テスタビリティと保守性が高く考慮されているのが伝わります。

以下に、再利用しやすいMarkdown形式でまとめました。

---

# Backend DB Architecture & Implementation Guide

## 1. アーキテクチャ概要

本プロジェクトでは、**クリーンアーキテクチャ**および**ポート＆アダプター（ヘキサゴナルアーキテクチャ）**を採用し、データアクセス詳細をビジネスロジックから分離します。

* **ドメイン層**: 純粋なビジネスロジックとエンティティ定義。
* **アプリケーション層**: ユースケース、DTO、およびリポジトリ/UoWのインターフェース（ポート）定義。
* **インフラ層**: SQLAlchemyを用いたデータアクセスの具体的な実装（アダプター）。
* **HTTP層**: FastAPIなどのエンドポイント（コントローラー）。

## 2. ディレクトリ構成

```text
app/infra/db/
├── base.py                 # SQLAlchemy基本設定 (DeclarativeBase)
├── session.py              # セッション管理・Factory
├── models/                 # SQLAlchemy ORMモデル
│   ├── __init__.py
│   ├── user.py             # ユーザー
│   ├── profile.py          # プロフィール
│   ├── target.py           # 目標・目標栄養素
│   ├── meal.py             # 食事エントリ
│   ├── meal_nutrition.py   # 食事栄養サマリ
│   ├── daily_nutrition.py  # 日次栄養サマリ
│   └── billing_account.py  # 課金・契約情報
├── repositories/           # リポジトリパターン実装
│   ├── user_repository.py
│   ├── target_repository.py
│   └── ...
└── uow/                    # Unit of Workの実装
    ├── sqlalchemy_base.py  # 共通UoW基底クラス
    ├── auth.py             # 認証関連UoW
    ├── target.py           # 目標設定関連UoW
    └── ...

```

## 3. SQLAlchemyモデル定義

主要なデータモデルの役割は以下の通りです。

| モデル名 | テーブル名 | 説明 |
| --- | --- | --- |
| `UserModel` | `users` | 基本情報、プラン、トライアル期限 |
| `ProfileModel` | `profiles` | ユーザー詳細（Userと1:1） |
| `TargetModel` | `targets` | 栄養目標の定義本体 |
| `TargetNutrientModel` | `target_nutrients` | 目標栄養素の具体的な数値 |
| `FoodEntryModel` | `food_entries` | 個別の食事記録（ログ） |

### 技術的特徴

* **ID管理**: PostgreSQLのUUIDを主キーとして採用。
* **整合性**: `relationship`での適切な`cascade`設定。
* **追跡**: 全テーブルに `created_at`, `updated_at`, `deleted_at`（論理削除用）を保持。
* **パフォーマンス**: クエリ頻度に基づいたインデックスの最適化。

## 4. リポジトリパターン

ドメインエンティティとDBモデルの橋渡しを行い、データアクセスを抽象化します。

### 実装の責務

1. **変換**: ドメインエンティティ  SQLAlchemyモデルの相互変換。
2. **CRUD**: 標準的なデータ操作の隠蔽。
3. **最適化**: `selectinload` や `joinedload` を用いたN+1問題の解決。

```python
class SqlAlchemyTargetRepository(TargetRepositoryPort):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, user_id: UserId, target_id: TargetId) -> TargetDefinition | None:
        stmt = select(TargetModel).where(TargetModel.id == target_id)
        model = self._session.execute(stmt).scalar_one_or_none()
        return self._to_entity(model) if model else None

```

## 5. Unit of Work (UoW) パターン

複数のリポジトリを跨ぐ操作において、トランザクションの原子性（ACID）を保証します。

### メリット

* **自動管理**: `__exit__` による自動的な `commit`/`rollback`。
* **一貫性**: 1つのユースケース内で同一セッションを共有。

```python
class SqlAlchemyTargetUnitOfWork(SqlAlchemyUnitOfWorkBase, TargetUnitOfWorkPort):
    def _on_enter(self, session: Session) -> None:
        # リポジトリにセッションを注入
        self.target_repo = SqlAlchemyTargetRepository(session)
        self.target_snapshot_repo = SqlAlchemyTargetSnapshotRepository(session)

```

## 6. セッション管理設定

SQLAlchemy 2.0 スタイルに準拠したセッション管理を行います。

* **Engine設定**: `pool_pre_ping=True` によるコネクション生存確認。
* **セッション生成**: FastAPIの `Depends` を用いた自動クローズ制御。

```python
def get_db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

```

## 7. マイグレーション (Alembic)

* `alembic/env.py`: アプリケーションの設定（`DATABASE_URL`）と同期。
* **自動検出**: `Base.metadata` を参照し、モデルの変更を自動でリビジョンファイルへ反映。

## 8. エラーハンドリング

DB固有の例外（`IntegrityError` 等）を、アプリケーションが理解できる**ドメイン例外**に変換して送出します。これにより、インフラ層のコードが上位層に漏洩するのを防ぎます。

## 9. テスト戦略

1. **ユニットテスト**: `FakeRepository` / `FakeUnitOfWork` を使用し、高速に実行。
2. **統合テスト**: インメモリSQLiteを使用してDBスキーマとの適合性を検証。
3. **実機テスト**: PostgreSQL 16 コンテナを使用し、実際の挙動を検証。

