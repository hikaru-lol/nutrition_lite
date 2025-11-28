# Backend Directory Structure

最終更新: 2025-11-28（自動生成）

## ルート直下

- `README.md` – プロジェクト概要とセットアップ手順。
- `pyproject.toml` / `uv.lock` – Poetry/uv ベースのビルド・依存管理設定。
- `alembic/` + `alembic.ini` – DB マイグレーション設定とスクリプト (`versions/` に履歴)。
- `nutrition_backend.egg-info/` – `pip install -e .` 実行時に生成されるメタデータ。
- `docs/` – 設計資料、要件、OpenAPI 仕様など。
- `tests/` – ユニット/統合テスト、Fake 実装、pytest 設定。
- `app/` – FastAPI アプリケーション本体。
- `.\*.venv`, `.pytest_cache/` – ローカル実行用の一時ディレクトリ（バージョン管理から除外推奨）。

## `app/` 配下

- `app/main.py` – FastAPI アプリ作成・ルータ登録・例外ハンドラ設定。
- `app/settings.py` – アプリケーション設定／環境変数の読み込み。
- `app/api/http/` – HTTP レイヤ (routers, schemas, cookies,エラーハンドラ等)。
- `app/application/` – UseCase や DTO を含むアプリケーション層。`auth/`, `meal/`, `profile/` などドメイン単位で整理。
- `app/domain/` – エンティティ・値オブジェクト・ドメインエラー。`auth/`, `nutrition/` 等で分割。
- `app/infra/` – DB リポジトリ、セキュリティ、LLM 連携などインフラ層の実装。
- `app/di/` – `container.py` による依存性解決（FastAPI 依存注入用ファクトリ）。
- `app/jobs/` – バッチ／バックグラウンドジョブ（例: `generate_meal_recommendations.py`）。

## `tests/` 配下

- `tests/conftest.py` – FastAPI TestClient と Fake UoW/Ports の共通フィクスチャ。
- `tests/fakes/` – テスト専用の `InMemoryUserRepository`, `FakeTokenService` 等。
- `tests/unit/` – ユースケース/ドメイン単位のユニットテスト。更に `application/`, `domain/`, `infra/` で整理。
- `tests/integration/api/` – FastAPI エンドポイントを TestClient で叩く統合テスト。
- `tests/integration_real/` – 実 DB/インフラを用いた統合テスト想定のフォルダ。
- `tests/application/` – アプリ層テストのサンプル（今後拡張予定）。

## その他

- `docs/openapi/openapi.yaml` – API 仕様書。
- `docs/plan/`, `docs/refactor/`, `docs/要件&仕様/` – 計画書や要件定義。
- `.pytest_cache/`, `.venv/` – 実行時に生成される一時キャッシュ/仮想環境 (gitignore 対象)。

上記構造を基に、ドメイン毎に `app/domain`→`application`→`api` の流れで依存が一方向となるよう整理されています。Tests では Fake 実装を共有して高速なユニット/統合テストを実現しています。
