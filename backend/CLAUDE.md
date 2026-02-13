# FastAPI バックエンド

## このディレクトリについて

FastAPI ベースの RESTful API。クリーンアーキテクチャ + ポート&アダプターパターンを採用。

## 技術スタック

- **フレームワーク**: FastAPI 0.110+, Uvicorn
- **ORM**: SQLAlchemy 2.0, Alembic (マイグレーション)
- **バリデーション**: Pydantic v2
- **認証**: JWT (python-jose), bcrypt
- **データベース**: PostgreSQL (本番), SQLite (開発/テスト)
- **ストレージ**: MinIO (S3 互換)
- **AI**: OpenAI API
- **決済**: Stripe
- **パッケージマネージャ**: uv

## ディレクトリ構造

```
app/
├── api/http/              # HTTP インターフェース層
│   ├── routers/          # エンドポイント定義
│   ├── schemas/          # Pydantic リクエスト/レスポンス
│   ├── mappers/          # DTO ↔ Schema 変換
│   ├── dependencies/     # FastAPI 依存性 (認証等)
│   └── errors.py         # HTTPエラーハンドラ
│
├── application/           # アプリケーション層 (ユースケース)
│   ├── {domain}/
│   │   ├── use_cases/    # ビジネスロジック
│   │   ├── dto/          # データ転送オブジェクト
│   │   ├── ports/        # インターフェース定義
│   │   └── errors.py     # アプリケーションエラー
│   └── common/ports/     # 共通ポート (UoW等)
│
├── domain/                # ドメイン層 (ビジネスルール)
│   └── {domain}/
│       ├── entities.py   # エンティティ (集約ルート)
│       ├── value_objects.py  # 値オブジェクト
│       └── errors.py     # ドメインエラー
│
├── infra/                 # インフラストラクチャ層
│   ├── db/
│   │   ├── models/       # SQLAlchemy モデル
│   │   ├── repositories/ # リポジトリ実装
│   │   ├── uow/          # Unit of Work 実装
│   │   ├── base.py       # DB エンジン設定
│   │   └── session.py    # セッション管理
│   ├── security/         # JWT, パスワードハッシュ
│   ├── storage/          # MinIO/S3 ストレージ
│   ├── llm/              # OpenAI 統合
│   ├── billing/          # Stripe 決済
│   └── time/             # Clock 抽象化
│
├── di/
│   └── container.py      # 依存性注入コンテナ
│
└── settings.py           # 環境変数設定
```

## ドメイン一覧

| ドメイン    | 説明                       |
| ----------- | -------------------------- |
| `auth`      | 認証・ユーザー管理         |
| `profile`   | ユーザープロフィール       |
| `target`    | 栄養目標                   |
| `meal`      | 食事記録                   |
| `nutrition` | 栄養計算・レポート         |
| `billing`   | 課金・サブスクリプション   |

## コマンド

```bash
uv sync                                    # 依存関係インストール
uv run uvicorn app.main:app --reload       # 開発サーバー (localhost:8000)
uv run alembic upgrade head                # マイグレーション実行
uv run pytest -m "not real_integration" tests/unit/        # ユニットテスト
uv run pytest -m "not real_integration" tests/integration  # 統合テスト
uv run pytest -m "real_integration" --maxfail=1            # 実インフラテスト
uv run ruff check                          # Lint
uv run mypy app                            # 型チェック
```

## クリーンアーキテクチャ

### 依存関係の方向

```
api/http → application → domain ← infra
              ↑            ↑
              └── ports ───┘
```

### 層の責務

| 層            | 責務                                       |
| ------------- | ------------------------------------------ |
| `api/http`    | HTTP リクエスト/レスポンス処理             |
| `application` | ユースケース実行、DTO 変換                 |
| `domain`      | ビジネスルール、エンティティ、値オブジェクト |
| `infra`       | 外部サービス実装 (DB, API, Storage)        |

## 主要パターン

### ユースケースパターン

```python
# application/target/use_cases/create_target.py
class CreateTargetUseCase:
    def __init__(
        self,
        uow: TargetUnitOfWorkPort,
        generator: TargetGeneratorPort,
        clock: ClockPort,
    ):
        self._uow = uow
        self._generator = generator
        self._clock = clock

    def execute(self, input_dto: CreateTargetInputDTO) -> TargetDTO:
        with self._uow as uow:
            # 1. ビジネスルール検証
            existing = uow.target_repo.list_by_user(user_id, limit=6)
            if len(existing) >= 5:
                raise TargetLimitExceededError()

            # 2. ドメインロジック実行
            target = TargetDefinition(...)
            uow.target_repo.add(target)

            # 3. 自動コミット (UoW __exit__)
            return _to_dto(target)
```

### リポジトリパターン

```python
# application/target/ports/target_repository_port.py (インターフェース)
class TargetRepositoryPort(Protocol):
    def add(self, target: TargetDefinition) -> None: ...
    def get_by_id(self, user_id: UserId, target_id: TargetId) -> TargetDefinition | None: ...
    def list_by_user(self, user_id: UserId, limit: int) -> list[TargetDefinition]: ...

# infra/db/repositories/target_repository.py (実装)
class SqlAlchemyTargetRepository(TargetRepositoryPort):
    def __init__(self, session: Session):
        self._session = session

    def add(self, target: TargetDefinition) -> None:
        model = self._to_model(target)
        self._session.add(model)

    def get_by_id(self, user_id: UserId, target_id: TargetId) -> TargetDefinition | None:
        stmt = select(TargetModel).where(...)
        model = self._session.execute(stmt).scalar_one_or_none()
        return self._to_entity(model) if model else None
```

### Unit of Work パターン

```python
# infra/db/uow/target.py
class SqlAlchemyTargetUnitOfWork(TargetUnitOfWorkPort):
    target_repo: TargetRepositoryPort

    def __enter__(self):
        self._session = self._session_factory()
        self.target_repo = SqlAlchemyTargetRepository(self._session)
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self._session.commit()    # 成功時: コミット
        else:
            self._session.rollback()  # 失敗時: ロールバック
        self._session.close()
```

### ルート定義

```python
# api/http/routers/target_route.py
@router.post("", status_code=201, response_model=TargetResponse)
def create_target(
    request: CreateTargetRequest,
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: CreateTargetUseCase = Depends(get_create_target_use_case),
) -> TargetResponse:
    input_dto = CreateTargetInputDTO(
        user_id=current_user.id,
        title=request.title,
        ...
    )
    result = use_case.execute(input_dto)
    return target_dto_to_schema(result)
```

## 依存性注入 (DI)

```python
# di/container.py
def get_create_target_use_case(
    uow: TargetUnitOfWorkPort = Depends(get_target_uow),
    generator: TargetGeneratorPort = Depends(get_target_generator),
    clock: ClockPort = Depends(get_clock),
) -> CreateTargetUseCase:
    return CreateTargetUseCase(uow, generator, clock)

# 環境変数によるスイッチング
def get_target_generator() -> TargetGeneratorPort:
    if settings.USE_OPENAI_TARGET_GENERATOR:
        return OpenAITargetGenerator(...)
    return StubTargetGenerator()
```

## 認証

### Cookie ベース JWT

```python
# api/http/dependencies/auth.py
def get_current_user_dto(
    access_token: str | None = Cookie(alias="ACCESS_TOKEN"),
    token_service: TokenServicePort = Depends(get_token_service),
    use_case: GetCurrentUserUseCase = Depends(...),
) -> AuthUserDTO:
    if not access_token:
        raise InvalidAccessTokenError("Access token missing")

    payload = token_service.verify_access_token(access_token)
    return use_case.execute(payload.user_id)
```

### トークン設定

| 項目           | 値                  |
| -------------- | ------------------- |
| Algorithm      | HS256               |
| Access Token   | 15 分 (設定可能)    |
| Refresh Token  | 7 日                |
| Cookie         | HttpOnly, SameSite=Lax |

## エラーハンドリング

### ドメインエラー階層

```python
# domain/auth/errors.py
class AuthError(Exception): ...
class EmailAlreadyUsedError(AuthError): ...
class InvalidCredentialsError(AuthError): ...

# domain/target/errors.py
class TargetError(Exception): ...
class MaxTargetsReachedError(TargetError): ...
class NoActiveTargetError(TargetError): ...
```

### HTTP エラーマッピング

```python
# api/http/errors.py
@app.exception_handler(AuthError)
def auth_error_handler(request, exc):
    if isinstance(exc, InvalidCredentialsError):
        return JSONResponse(status_code=401, content={"detail": str(exc)})
    return JSONResponse(status_code=400, content={"detail": str(exc)})
```

## 値オブジェクト

```python
# domain/target/value_objects.py
class UserId:
    value: str

class TargetId:
    value: str

class GoalType(str, Enum):
    WEIGHT_LOSS = "weight_loss"
    MAINTAIN = "maintain"
    WEIGHT_GAIN = "weight_gain"
    HEALTH_IMPROVE = "health_improve"

class ActivityLevel(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"

class NutrientCode(str, Enum):
    CARBOHYDRATE = "carbohydrate"
    FAT = "fat"
    PROTEIN = "protein"
    # ... 10種類
```

## テスト構造

```
tests/
├── unit/                  # ユニットテスト (モック使用)
│   ├── application/      # ユースケーステスト
│   └── infra/            # インフラ実装テスト
├── integration/           # 統合テスト (フェイク実装)
│   └── api/              # API エンドポイントテスト
├── integration_real/      # 実インフラテスト
│   └── api/              # 実 DB/MinIO 使用
└── fakes/                 # インメモリフェイク実装
    ├── auth_repositories.py
    ├── target_repositories.py
    └── ...
```

### テストマーカー

```python
@pytest.mark.real_integration
def test_with_real_db():
    # PostgreSQL, MinIO を使用するテスト
    ...
```

## 環境変数

### 必須設定

```bash
DATABASE_URL=postgresql+psycopg2://app:app@db:5432/app
JWT_SECRET_KEY=your-secret-key
```

### フィーチャーフラグ

```bash
USE_FAKE_INFRA=true                          # true: インメモリ, false: 実インフラ
USE_OPENAI_TARGET_GENERATOR=false            # OpenAI 目標生成
USE_OPENAI_NUTRITION_ESTIMATOR=false         # OpenAI 栄養推定
USE_OPENAI_DAILY_REPORT_GENERATOR=false      # OpenAI 日次レポート
USE_OPENAI_MEAL_RECOMMENDATION_GENERATOR=false
```

### 外部サービス

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Stripe
STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID=price_...

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=nutrition-dev
```

## API エンドポイント

| モジュール | エンドポイント                                    |
| ---------- | ------------------------------------------------- |
| auth       | POST /register, /login, /refresh, /logout, DELETE /account |
| profile    | GET /profile, PUT /profile                        |
| target     | GET/POST /targets, GET/PATCH/DELETE /targets/{id}, POST /targets/{id}/activate |
| meal       | GET/POST /meals, PATCH/DELETE /meals/{id}         |
| nutrition  | POST /nutrition/compute, GET /nutrition/daily     |
| billing    | POST /billing/checkout, GET /billing/portal       |

## 新規機能実装の流れ

1. **domain/**: エンティティ、値オブジェクト、ドメインエラー
2. **application/dto/**: 入出力 DTO
3. **application/ports/**: リポジトリ等のインターフェース
4. **application/use_cases/**: ユースケース実装
5. **infra/db/models/**: SQLAlchemy モデル
6. **infra/db/repositories/**: リポジトリ実装
7. **infra/db/uow/**: Unit of Work 実装
8. **api/http/schemas/**: Pydantic スキーマ
9. **api/http/routers/**: エンドポイント実装
10. **di/container.py**: DI 登録
11. **tests/**: テスト作成

## 命名規則

| 対象           | 規則                                    |
| -------------- | --------------------------------------- |
| エンドポイント | `/api/v1/{resource}`                    |
| ユースケース   | `{Action}{Entity}UseCase`               |
| リポジトリ     | `{Entity}RepositoryPort` / `SqlAlchemy{Entity}Repository` |
| DTO            | `{Entity}DTO`, `{Action}{Entity}InputDTO` |
| スキーマ       | `{Entity}Request`, `{Entity}Response`   |
| エラー         | `{Entity}{Problem}Error`                |
