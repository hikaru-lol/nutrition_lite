
# Backend Testing Strategy & Implementation Guide

## 1. テスト構造概要

テストコードは、実行速度と検証対象の範囲（スコープ）に応じて3層に分離されています。

```text
tests/
├── conftest.py              # 全体共通設定・共通Fakeフィクスチャ
├── unit/                    # 【ユニットテスト】(30ファイル)
│   ├── conftest.py          # ユニットテスト専用設定
│   ├── application/         # ユースケース単体テスト
│   └── infra/               # インフラ実装単体テスト
├── integration/             # 【統合テスト：Fake】(11ファイル)
│   └── api/                 # APIエンドポイントテスト（Fakeインフラ使用）
├── integration_real/        # 【実インフラテスト】(4ファイル)
│   └── api/                 # 実DB・MinIOを使用したエンドツーエンドテスト
└── fakes/                   # テスト用Fake実装（InMemoryリポジトリ等）

```

## 2. テスト設定と環境分離

### Pytest マーカー設定 (`pyproject.toml`)

実インフラを使用するテストを明示的にマークし、誤って重いテストや外部依存のあるテストが走るのを防ぎます。

```toml
[tool.pytest.ini_options]
markers = [
    "real_integration: tests that hit real infra (real DB, MinIO, etc.)",
]

```

### フィクスチャ管理

* **`tests/conftest.py`**: インメモリリポジトリやFakeサービス（Hasher, Clock）を提供。`autouse=True` のリセット機能により、各テスト間の独立性を確保。
* **`tests/unit/conftest.py`**: ユースケース向けの `FakeAuthUnitOfWork` 等を提供。
* **`tests/integration/api/conftest.py`**: APIテスト用の `TestClient` や、認証済み状態を再現する `authed_client` を提供。

## 3. Fake実装パターン

外部依存を排除し、高速なテストを実現するためにポート（インターフェース）に基づいたFakeを実装します。

### リポジトリFake（メモリ内保持）

```python
class InMemoryUserRepository(UserRepositoryPort):
    def __init__(self) -> None:
        self._users_by_id: Dict[str, User] = {}
        self._users_by_email: Dict[str, User] = {}

    def clear(self) -> None: # テストごとに状態をクリア
        self._users_by_id.clear()
        self._users_by_email.clear()

```

### サービスFake

* **FakePasswordHasher**: 高速化のため、実際のハッシュ計算を行わず文字列接頭辞のみを付与。
* **FixedClock**: 時刻を固定し、`tick()` 等のメソッドで時間を進める操作を可能にする。

## 4. テストタイプ別の特徴

| テスト種類 | 対象 | 依存関係 | 実行速度 |
| --- | --- | --- | --- |
| **ユニットテスト** | ユースケース・ドメインモデル | Fakeリポジトリ・サービス | 極めて高速 |
| **統合テスト (Fake)** | APIエンドポイント | Fakeインフラ・TestClient | 高速 |
| **実インフラテスト** | 全レイヤー貫通 | 実DB (PostgreSQL)・MinIO | 低速 |

## 5. 実行コマンド体系

### 通常の開発フロー（高速テスト）

```bash
# ユニットテストとAPI統合テスト(Fake)を実行
uv run pytest -m "not real_integration" tests/unit/
uv run pytest -m "not real_integration" tests/integration/

```

### デプロイ前・CI確認（実インフラ）

```bash
# 実インフラテストのみを実行
uv run pytest -m "real_integration" --maxfail=1

```

### 品質担保（静的解析）

```bash
uv run mypy app      # 型チェック
uv run ruff check    # リンター・フォーマッタ

```

## 6. 主要設計原則

1. **3層テスト構造**: Unit → Integration(Fake) → Integration(Real) で網羅性と速度を両立。
2. **Fake First**: 開発時はFake実装を用いた高速テストを基本とする。
3. **状態独立性**: `autouse` フィクスチャによる自動リセットで、テスト順序に依存しない。
4. **環境分離**: 環境変数による機能（OpenAI等）のモック化。