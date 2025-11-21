import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

pytestmark = pytest.mark.real_integration  # このファイル内のテストは real_integration マーク付き


def _make_client() -> TestClient:
    # USE_FAKE_INFRA=false で起動されている前提なので、
    # create_app() は本番と同じ DI (SqlAlchemy + MinIO) で組み立てられる
    app = create_app()
    return TestClient(app)


def test_register_login_profile_flow_real():
    """
    実際の Postgres + MinIO を使ったエンドツーエンドテスト。

    フロー:
      1. /auth/register でユーザー登録 (Cookie 発行)
      2. /auth/me で認証情報が有効か確認
      3. /profile/me (PUT) でプロフィール作成
      4. /profile/me (GET) でプロフィールが永続化されていることを確認
    """
    client = _make_client()

    # 1. ユニークなメールアドレスでユーザー登録
    email = f"realtest_{uuid.uuid4().hex}@example.com"
    password = "RealTestPassword123!"

    register_resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "name": "Real User",
        },
    )

    assert register_resp.status_code == 201, register_resp.text
    data = register_resp.json()
    assert "user" in data
    assert data["user"]["email"] == email

    # TestClient は Set-Cookie を内部の CookieJar に反映してくれるので、
    # 以降のリクエストでは明示的に cookies= を渡さなくても大丈夫。

    # 2. /auth/me で現在のユーザーを取得できることを確認
    me_resp = client.get("/api/v1/auth/me")
    assert me_resp.status_code == 200, me_resp.text
    me_data = me_resp.json()
    assert me_data["user"]["email"] == email
    user_id = me_data["user"]["id"]

    # 3. /profile/me に対してプロフィールを作成 (PUT)
    profile_payload = {
        "sex": "male",
        "birthdate": "1990-01-02",
        "height_cm": 175.5,
        "weight_kg": 68.2,
    }

    upsert_resp = client.put("/api/v1/profile/me", json=profile_payload)
    assert upsert_resp.status_code == 200, upsert_resp.text
    profile_data = upsert_resp.json()

    assert profile_data["user_id"] == user_id
    assert profile_data["sex"] == profile_payload["sex"]
    assert profile_data["birthdate"] == profile_payload["birthdate"]
    assert profile_data["height_cm"] == profile_payload["height_cm"]
    assert profile_data["weight_kg"] == profile_payload["weight_kg"]
    # 画像はまだ API から渡していないので None のはず
    assert profile_data["image_id"] is None

    # 4. /profile/me (GET) でも同じプロフィールが取得できることを確認
    get_profile_resp = client.get("/api/v1/profile/me")
    assert get_profile_resp.status_code == 200, get_profile_resp.text
    get_profile_data = get_profile_resp.json()

    assert get_profile_data == profile_data
