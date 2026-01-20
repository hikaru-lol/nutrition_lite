まずは、いま共有してくれた内容を「１枚の設計メモ」に落とし込むイメージでまとめていきます 👍
その上で、実際のディレクトリ／ファイル構成の“完成イメージ”も tree 形式で置いておきます。

---

## 1. バックエンド全体像の整理

### レイヤ構造（ざっくり）

- **API 層 (`app/api/http`)**

  - FastAPI のルータ・スキーマ・依存関係・エラーハンドラ。
  - **役割**: HTTP を受け取って DTO に変換 → DI から UseCase を解決 → 結果を HTTP レスポンスにマッピング。
  - ルータは極力「薄く」、ビジネスロジックは一切持たない。

- **Application 層 (`app/application`)**

  - ユースケース・DTO・ポート（インターフェース）。
  - 例: `ComputeMealNutritionUseCase`, `GenerateDailyNutritionReportUseCase`, `CreateTargetUseCase` など。
  - **役割**:

    - 1 ユースケース = 1 シナリオ（登録／ログイン／日次レポ生成など）。
    - RepostioryPort / LLMPort / ClockPort / UoWPort などのポートを受け取り、それを組み合わせて処理をオーケストレーション。
    - トランザクション境界（UoW）もここで意識する。

- **Domain 層 (`app/domain`)**

  - エンティティ・値オブジェクト・ドメインエラー。
  - 例: `User`, `Profile`, `FoodEntry`, `DailyNutritionReport`, `TargetDefinition`, `TargetNutrient` など。
  - **役割**:

    - ビジネスルールを表現する「純粋な」モデル。
    - ここは外部ライブラリに依存しない（なるべく Python 標準 + dataclass など）。

- **インフラ層 (`app/infra`)**

  - ポートを実際に実装するアダプタ。
  - 例:

    - `infra/db`: SQLAlchemy のモデル・リポジトリ・UoW 実装。
    - `infra/llm`: OpenAI / Stub の LLM クライアント。
    - `infra/security`: パスワードハッシュ、JWT トークンサービス。
    - `infra/storage`: MinIO / メモリ実装のストレージ。
    - `infra/time`: SystemClock 実装。

  - **役割**: 具体的な DB・外部サービス・ストレージなどの詳細をカプセル化。

- **DI & 設定 (`app/di`, `app/settings.py`)**

  - `container.py` で各ポートに対する実装を組み合わせて、UseCase を生成。
  - `USE_OPENAI_TARGET_GENERATOR`, `USE_OPENAI_DAILY_REPORT_GENERATOR` などの環境変数で Stub ↔ 本物を切り替え。

- **テスト (`tests`)**

  - `fakes/` で FakeRepository/UoW/LLM などを用意。
  - DI を上書きして「DB なし」「外部サービスなし」でユースケースを検証。
  - `integration/` で HTTP レベルのテスト、`integration_real/` で本物の DB/MinIO を使ったインテグレーションも可能。

---

## 2. ディレクトリ構造（全体像）

```text
backend/
├─ pyproject.toml
├─ uv.lock
├─ alembic/
│  ├─ versions/
│  └─ env.py
├─ alembic.ini
├─ docs/
│  ├─ backend_structure.md
│  ├─ openapi/
│  │  └─ nutrition_backend.yaml
│  └─ refactor_notes.md
├─ scripts/
│  ├─ smoke_target_generator.py
│  ├─ smoke_daily_report_generator.py
│  └─ ...
├─ nutrition_backend.egg-info/
├─ tests/
│  ├─ conftest.py
│  ├─ fakes/
│  │  ├─ fake_auth_uow.py
│  │  ├─ fake_meal_uow.py
│  │  ├─ fake_profile_uow.py
│  │  ├─ fake_target_uow.py
│  │  └─ fake_llm_services.py
│  ├─ unit/
│  │  ├─ application/
│  │  ├─ domain/
│  │  └─ infra/
│  ├─ integration/
│  │  └─ test_http_endpoints.py
│  └─ integration_real/
│     └─ test_real_db_minio.py
└─ app/
   ├─ main.py
   ├─ settings.py
   ├─ api/
   │  └─ http/
   │     ├─ routers/
   │     │  ├─ auth_route.py
   │     │  ├─ profile_route.py
   │     │  ├─ meal_route.py
   │     │  ├─ nutrition_route.py
   │     │  ├─ daily_report_route.py
   │     │  └─ target_route.py
   │     ├─ schemas/
   │     │  ├─ auth.py
   │     │  ├─ profile.py
   │     │  ├─ meal.py
   │     │  ├─ nutrition.py
   │     │  ├─ daily_report.py
   │     │  └─ target.py
   │     ├─ dependencies/
   │     │  ├─ auth.py
   │     │  ├─ db.py
   │     │  └─ llm.py
   │     ├─ cookies.py
   │     ├─ errors.py
   │     └─ mappers.py
   ├─ application/
   │  ├─ auth/
   │  │  ├─ dto/
   │  │  │  ├─ register_dto.py
   │  │  │  ├─ login_dto.py
   │  │  │  └─ auth_user_dto.py
   │  │  ├─ ports/
   │  │  │  ├─ user_repository_port.py
   │  │  │  ├─ password_hasher_port.py
   │  │  │  ├─ token_service_port.py
   │  │  │  ├─ clock_port.py
   │  │  │  └─ auth_uow_port.py
   │  │  └─ use_cases/
   │  │     ├─ register_user.py
   │  │     ├─ login_user.py
   │  │     ├─ logout_user.py
   │  │     ├─ refresh_token.py
   │  │     └─ delete_account.py
   │  ├─ profile/
   │  │  ├─ dto/
   │  │  ├─ ports/
   │  │  │  ├─ profile_repository_port.py
   │  │  │  ├─ profile_image_storage_port.py
   │  │  │  └─ profile_uow_port.py
   │  │  └─ use_cases/
   │  │     ├─ get_profile.py
   │  │     └─ upsert_profile.py
   │  ├─ meal/
   │  │  ├─ dto/
   │  │  ├─ ports/
   │  │  │  ├─ meal_repository_port.py
   │  │  │  └─ meal_uow_port.py
   │  │  └─ use_cases/
   │  │     ├─ create_food_entry.py
   │  │     ├─ update_food_entry.py
   │  │     ├─ delete_food_entry.py
   │  │     ├─ list_food_entries_by_date.py
   │  │     └─ check_daily_log_completion.py
   │  ├─ nutrition/
   │  │  ├─ dto/
   │  │  ├─ ports/
   │  │  │  ├─ nutrition_estimator_port.py
   │  │  │  ├─ nutrition_uow_port.py
   │  │  │  └─ daily_report_generator_port.py
   │  │  └─ use_cases/
   │  │     ├─ compute_meal_nutrition.py
   │  │     ├─ compute_daily_nutrition_summary.py
   │  │     └─ generate_daily_nutrition_report.py
   │  ├─ target/
   │  │  ├─ dto/
   │  │  ├─ ports/
   │  │  │  ├─ target_repository_port.py
   │  │  │  ├─ target_uow_port.py
   │  │  │  ├─ target_generator_port.py
   │  │  │  └─ profile_query_port.py
   │  │  └─ use_cases/
   │  │     ├─ create_target.py
   │  │     ├─ list_targets.py
   │  │     ├─ get_active_target.py
   │  │     ├─ update_target.py
   │  │     └─ activate_target.py
   │  └─ common/
   │     └─ pagination.py  (共通 DTO など)
   ├─ domain/
   │  ├─ auth/
   │  │  ├─ entities.py
   │  │  ├─ value_objects.py
   │  │  └─ errors.py
   │  ├─ profile/
   │  │  ├─ entities.py
   │  │  ├─ value_objects.py
   │  │  └─ errors.py
   │  ├─ meal/
   │  │  ├─ entities.py    # FoodEntry, Meal, etc.
   │  │  ├─ value_objects.py  # MealType, Amount, etc.
   │  │  └─ errors.py
   │  ├─ nutrition/
   │  │  ├─ entities.py    # MealNutritionSummary, DailyNutritionSummary, DailyNutritionReport
   │  │  ├─ value_objects.py
   │  │  └─ errors.py
   │  └─ target/
   │     ├─ entities.py    # TargetDefinition, TargetNutrient, TargetSnapshot
   │     ├─ value_objects.py
   │     └─ errors.py
   ├─ infra/
   │  ├─ db/
   │  │  ├─ base.py
   │  │  ├─ session.py
   │  │  ├─ models/
   │  │  │  ├─ user.py
   │  │  │  ├─ profile.py
   │  │  │  ├─ food_entry.py
   │  │  │  ├─ meal_nutrition_summary.py
   │  │  │  ├─ daily_nutrition_summary.py
   │  │  │  ├─ daily_nutrition_report.py
   │  │  │  └─ target.py
   │  │  ├─ repositories/
   │  │  │  ├─ sqlalchemy_user_repository.py
   │  │  │  ├─ sqlalchemy_profile_repository.py
   │  │  │  ├─ sqlalchemy_meal_repository.py
   │  │  │  ├─ sqlalchemy_nutrition_repository.py
   │  │  │  └─ sqlalchemy_target_repository.py
   │  │  └─ uow/
   │  │     ├─ auth_uow.py
   │  │     ├─ profile_uow.py
   │  │     ├─ meal_uow.py
   │  │     ├─ nutrition_uow.py
   │  │     └─ target_uow.py
   │  ├─ llm/
   │  │  ├─ openai_target_generator.py
   │  │  ├─ openai_daily_report_generator.py
   │  │  ├─ stub_target_generator.py
   │  │  └─ stub_daily_report_generator.py
   │  ├─ security/
   │  │  ├─ bcrypt_password_hasher.py
   │  │  └─ jwt_token_service.py
   │  ├─ storage/
   │  │  ├─ minio_profile_image_storage.py
   │  │  └─ in_memory_profile_image_storage.py
   │  └─ time/
   │     └─ system_clock.py
   ├─ di/
   │  └─ container.py
   └─ jobs/
      ├─ __init__.py
      └─ generate_meal_recommendations.py
```

※ 実際のファイル名はプロジェクト現状に合わせて微調整して OK です。
　ここでは「整理された最終形のイメージ」として書いています。

---

## 3. ドメインごとの内容整理

### Auth

- **UseCase**

  - `register_user`, `login_user`, `logout_user`, `refresh_token`, `delete_account`, `get_current_user`。

- **Ports**

  - `UserRepositoryPort`, `PasswordHasherPort`, `TokenServicePort`, `AuthUnitOfWorkPort`, `ClockPort`。

- **HTTP**

  - `auth_route.py`:

    - Cookie セット・クリア（`set_auth_cookies`, `clear_auth_cookies`）を担当。
    - `AuthError` 系を `errors.py` の共通ハンドラで HTTP にマッピング。

### Profile

- UseCase: `GetProfileUseCase`, `UpsertProfileUseCase`。
- Ports: `ProfileRepositoryPort`, `ProfileImageStoragePort`, `ProfileUnitOfWorkPort`。
- HTTP: `profile_route.py` で認証必須、DTO ↔ Pydantic スキーマ変換。

### Meal Tracking

- UseCase:

  - CRUD: `CreateFoodEntryUseCase`, `UpdateFoodEntryUseCase`, `DeleteFoodEntryUseCase`, `ListFoodEntriesByDateUseCase`。
  - `CheckDailyLogCompletionUseCase`（プロフィール情報と Meal Repo を使って「その日が記録完了か」を判定）。

- Ports: `MealUnitOfWorkPort`, `MealRepositoryPort`。
- HTTP: `meal_route.py` からユースケース呼び出し → 更新された Meal に応じて Nutrition 再計算をトリガー。

### Nutrition

- UseCase:

  - `ComputeMealNutritionUseCase` → `MealNutritionSummary` を作成。
  - `ComputeDailyNutritionSummaryUseCase` → 食事ごとの summary を集計して 1 日分に。
  - `GenerateDailyNutritionReportUseCase` → DailyLog 完了 + TargetSnapshot + DailySummary をチェックして LLM でテキスト生成。

- Ports:

  - `NutritionEstimatorPort`（Stub/LLM/DB 等で差し替え可能）。
  - `DailyReportGeneratorPort`（Stub or OpenAI）。
  - `NutritionUnitOfWorkPort`。

- HTTP:

  - `nutrition_route.py`, `daily_report_route.py` などからユースケースを利用。
  - `DailyLogNotCompletedError`, `DailyLogProfileNotFoundError`, `DailyNutritionReportAlreadyExistsError` を HTTP エラーにマッピング。

### Targets

- UseCase:

  - `CreateTargetUseCase`（17 栄養素 + rationale + disclaimer を LLM で生成）。
  - `ListTargetsUseCase`, `GetTargetUseCase`, `UpdateTargetUseCase`, `ActivateTargetUseCase`。

- Ports:

  - `TargetRepositoryPort`, `TargetUnitOfWorkPort`, `TargetGeneratorPort`, `ProfileQueryPort`。

- HTTP:

  - `target_route.py` で DTO ↔ スキーマ変換、ログ出力。

---

## 4. DI / 設定の役割

- `app/settings.py`

  - DB 接続文字列、JWT 秘密鍵、OpenAI API キー、フラグ（`USE_OPENAI_TARGET_GENERATOR` など）を一元管理。

- `app/di/container.py`

  - 主要な factory:

    - `get_db_session()`, `get_auth_uow()`, `get_meal_uow()` …
    - `get_target_generator()`（Stub or OpenAI）、`get_daily_report_generator()` など。
    - `get_register_user_use_case()`, `get_compute_daily_nutrition_summary_use_case()` など。

  - 「リクエスト単位の UoW」「アプリ全体で 1 個の LLM クライアント」など、ライフタイムもここで統制。

---

## 5. リクエストの流れ（例：日次レポート生成）

1. `/daily-report/generate` に HTTP POST
2. `daily_report_route.py`

   - リクエストボディ → `GenerateDailyReportRequest` (Pydantic)
   - `Depends(get_generate_daily_nutrition_report_use_case)` で UseCase 解決

3. `GenerateDailyNutritionReportUseCase`

   - `DailyLogCompletionChecker` UseCase や `NutritionUnitOfWorkPort`, `DailyReportGeneratorPort` を利用して

     - ログ完了確認 → ターゲットスナップショット取得 → DailySummary 取得 → LLM にプロンプト投げる

4. `DailyNutritionReport` エンティティを作成 → UoW を通じて DB に保存 → DTO 返却。
5. Router が DTO → HTTP レスポンススキーマに詰め直して返却。

---

このあたりを `docs/backend_structure.md` にほぼコピペで入れて、
・上半分が「アーキテクチャの考え方」
・下半分が「ディレクトリ構成と各ディレクトリの責務」

みたいにしておくと、今後リファクタするときも見通しがかなり良くなると思います 💪
