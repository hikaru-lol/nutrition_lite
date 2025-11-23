from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

BASE_AUTH = "/api/v1/auth"
BASE_PROFILE = "/api/v1/profile"


def _make_email(prefix: str) -> str:
    """テストごとにユニークなメールアドレスを生成するヘルパー。"""
    return f"{prefix}_{uuid4().hex}@example.com"


def _register_user(
    client: TestClient,
    *,
    email_prefix: str = "profile_user",
    password: str = "test-password",
    name: str = "Profile User",
):
    """
    AUTH の /auth/register を使ってユーザーを 1 人作成し、
    レスポンスとクッキーを返すヘルパー。
    """
    email = _make_email(email_prefix)
    resp = client.post(
        f"{BASE_AUTH}/register",
        json={
            "email": email,
            "password": password,
            "name": name,
        },
    )
    return email, password, resp


# ============================================================
# /profile/me - 認証まわり
# ============================================================


def test_get_profile_without_auth_returns_401(client: TestClient) -> None:
    # 認証情報なしで叩く
    client.cookies.clear()

    resp = client.get(f"{BASE_PROFILE}/me")
    assert resp.status_code == 401

    body = resp.json()
    # ErrorResponse の形に寄せていく想定だが、現時点では detail の可能性もあるので緩めにチェック
    assert "error" in body or "detail" in body


def test_get_profile_for_new_user_returns_401_user_not_found(client: TestClient) -> None:
    # ユーザー作成（ログイン状態になる）
    email, password, reg_resp = _register_user(
        client, email_prefix="profile_notfound")
    assert reg_resp.status_code == 201

    cookies = reg_resp.cookies

    # プロフィール未作成の状態で GET /profile/me
    resp = client.get(f"{BASE_PROFILE}/me", cookies=cookies)
    # 現状の実装では GetMyProfileUseCase が UserNotFoundError を投げ、401 になる想定
    assert resp.status_code == 401

    body = resp.json()
    if "error" in body:
        # auth_error_handler が USER_NOT_FOUND を返す想定
        assert body["error"]["code"] in (
            "USER_NOT_FOUND", "INVALID_CREDENTIALS")


# ============================================================
# /profile/me - 作成 & 取得
# ============================================================


def test_upsert_profile_creates_profile_and_get_me_returns_it(client: TestClient) -> None:
    email, password, reg_resp = _register_user(
        client, email_prefix="profile_create")
    assert reg_resp.status_code == 201

    cookies = reg_resp.cookies

    # プロフィール作成（PUT /profile/me）
    req = {
        "sex": "male",
        "birthdate": "1990-01-01",
        "height_cm": 175.0,
        "weight_kg": 70.5,
    }

    put_resp = client.put(
        f"{BASE_PROFILE}/me",
        json=req,
        cookies=cookies,
    )
    assert put_resp.status_code == 200

    body = put_resp.json()jx
    assert body["user_id"]  # uuid 文字列が入っているはず
    assert body["sex"] == req["sex"]
    assert body["birthdate"] == req["birthdate"]
    assert body["height_cm"] == req["height_cm"]
    assert body["weight_kg"] == req["weight_kg"]
    # 画像はまだ未対応なので None のままの想定
    assert body["image_id"] is None

    # その後 GET /profile/me で同じ値が返ってくることを確認
    get_resp = client.get(f"{BASE_PROFILE}/me", cookies=cookies)
    assert get_resp.status_code == 200

    get_body = get_resp.json()
    assert get_body["user_id"] == body["user_id"]
    assert get_body["sex"] == req["sex"]
    assert get_body["birthdate"] == req["birthdate"]
    assert get_body["height_cm"] == req["height_cm"]
    assert get_body["weight_kg"] == req["weight_kg"]
    assert get_body["image_id"] is None


def test_upsert_profile_updates_existing_profile(client: TestClient) -> None:
    email, password, reg_resp = _register_user(
        client, email_prefix="profile_update")
    assert reg_resp.status_code == 201

    cookies = reg_resp.cookies

    # 初回プロフィール作成
    req1 = {
        "sex": "female",
        "birthdate": "1985-05-10",
        "height_cm": 160.0,
        "weight_kg": 55.0,
    }
    resp1 = client.put(
        f"{BASE_PROFILE}/me",
        json=req1,
        cookies=cookies,
    )
    assert resp1.status_code == 200
    body1 = resp1.json()

    # 値を変更して再度 PUT（更新）
    req2 = {
        "sex": "female",
        "birthdate": "1985-05-10",
        "height_cm": 161.0,  # 身長だけ変更
        "weight_kg": 56.0,   # 体重も変更
    }
    resp2 = client.put(
        f"{BASE_PROFILE}/me",
        json=req2,
        cookies=cookies,
    )
    assert resp2.status_code == 200
    body2 = resp2.json()

    # user_id は変わらず、height/weight が更新されている想定
    assert body2["user_id"] == body1["user_id"]
    assert body2["height_cm"] == req2["height_cm"]
    assert body2["weight_kg"] == req2["weight_kg"]

    # GET /profile/me でも更新後の値が返ることを確認
    get_resp = client.get(f"{BASE_PROFILE}/me", cookies=cookies)
    assert get_resp.status_code == 200
    get_body = get_resp.json()
    assert get_body["height_cm"] == req2["height_cm"]
    assert get_body["weight_kg"] == req2["weight_kg"]
