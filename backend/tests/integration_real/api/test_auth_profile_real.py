import pytest
from fastapi.testclient import TestClient
from app.main import create_app

pytestmark = pytest.mark.real_integration  # このファイル内のテストは real_integration マーク付き


def _make_client() -> TestClient:
    app = create_app()  # Fake override は USE_FAKE_INFRA=false で無効化されている前提
    return TestClient(app)


def test_register_login_profile_flow_real():
    client = _make_client()

    # 1. 正しい DATABASE_URL (Postgres) と MinIO が起動している前提で /auth/register を叩く
    ...
