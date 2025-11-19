# Nutrition Backend

FastAPI と SQLAlchemy で構成された栄養管理アプリ向けバックエンドです。まずは認証まわりを作り込み、Cookie ベースのアクセストークン / リフレッシュトークン運用を支えるユースケースとドメイン層を整備しています。今後 API を拡張しやすいようにクリーンアーキテクチャ寄りのレイヤー構成・DI コンテナ・ユニットテスト群を用意済みです。

## リポジトリ構成

- `backend/app` – FastAPI アプリ本体。`api`(HTTP I/F), `application`(ユースケース), `domain`, `infra`, `di`, `settings` でレイヤーを分離。
- `backend/tests` – application/domain 層を中心にした unit / integration テスト。
- `backend/docs` – OpenAPI スナップショットや refactor メモなど技術ドキュメント。
- `docs/GIT_WORKFLOW.md` – ブランチ戦略や PR 運用ルール。
- `scripts/` – 将来的な補助スクリプト置き場。

## セットアップ

### 前提

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) または標準 `pip`
- (推奨) ローカル DB: SQLite もしくは PostgreSQL

### 依存関係のインストール

```bash
cd backend
uv sync                     # 推奨: uv によるロックファイル運用
# もしくは
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

### 主な環境変数（`app/settings.py`）

| 変数 | デフォルト | 役割 |
| --- | --- | --- |
| `ENV` | `local` | 実行環境タグ。ログや将来の分岐に使用予定。 |
| `DATABASE_URL` | `sqlite+pysqlite:///:memory:` | SQLAlchemy 用接続。ローカル開発では `sqlite:///./local.db`、本番では PostgreSQL を指定。 |
| `JWT_SECRET_KEY` / `JWT_ALGORITHM` | `dev-secret-change-me` / `HS256` | 署名キーとアルゴリズム。 |
| `ACCESS_TOKEN_TTL_MINUTES` | `15` | アクセストークン寿命（分）。 |
| `REFRESH_TOKEN_TTL_DAYS` | `7` | リフレッシュトークン寿命（日）。 |
| `BACKEND_DOMAIN` | `localhost` | Cookie に紐づくドメイン。 |
| `COOKIE_SECURE` / `COOKIE_SAMESITE` | `False` / `lax` | Set-Cookie の制御。HTTPS 本番では `COOKIE_SECURE=1` 推奨。 |

`.env` を backend 直下に置き、`uvicorn` 起動前に読み込ませる運用が簡単です。

### サーバー起動

```bash
cd backend
uv run uvicorn app.main:app --reload
# または (仮想環境有効化済みなら)
uvicorn app.main:app --reload
```

- Swagger UI: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

## 実装されている認証 API

| Method | Path | 説明 |
| --- | --- | --- |
| `POST /api/v1/auth/register` | ユーザー作成 & 自動ログイン。成功時に HTTP-only `ACCESS_TOKEN` / `REFRESH_TOKEN` をセット。 |
| `POST /api/v1/auth/login` | メール + パスワードで認証し、Cookie にトークンを書き込み。 |
| `POST /api/v1/auth/logout` | 現状はクライアント側 Cookie を削除（将来的にサーバーサイド無効化予定）。 |
| `GET /api/v1/auth/me` | Cookie のアクセストークンから現在のユーザー情報を返却。 |
| `DELETE /api/v1/auth/me` | 自アカウント削除 + Cookie クリア。 |
| `POST /api/v1/auth/refresh` | `REFRESH_TOKEN` Cookie から新しいトークンペアを払い出し。 |

FastAPI レイヤーでは DTO/Schema を使ったバリデーションを行い、`app.application` 配下のユースケースがドメインルールを実装、`app.infra` が SQLAlchemy リポジトリ・Bcrypt ハッシャー・JWT サービスを担います。DI は `app.di.container` で管理しており、テスト時には各 Port を差し替え可能です。

## テスト

```bash
cd backend
uv run pytest      # もしくは pytest
```

- `tests/unit` : ユースケース単位の検証。フェイクリポジトリを使って振る舞いを担保。
- `tests/integration` : 実際の SQLAlchemy セッション・JWT 実装と合わせた疎通確認。

## 今後の追加に向けて

- 認証以外の機能追加時も、application 層に新ユースケース・infra にリポジトリ実装を足すだけで API へ組み込み可能です。
- `backend/docs/openapi` に API スナップショットを置いているので、更新時は `uv run uvicorn ...` + `curl` 等で随時確認してください。
- 運用ルールや PR の流れは `docs/GIT_WORKFLOW.md` を参照。
