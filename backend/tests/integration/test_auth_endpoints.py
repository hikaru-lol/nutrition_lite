
from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

BASE_URL = "/api/v1/auth"


def _make_email(prefix: str) -> str:
    """テストごとに一意なメールアドレスを作るヘルパー。"""
    return f"{prefix}_{uuid4().hex}@example.com"


def _assert_auth_cookies_set(response):
    # TestClient はレスポンス時点の CookieJar を持っている
    assert "ACCESS_TOKEN" in response.cookies
    assert "REFRESH_TOKEN" in response.cookies


def _assert_auth_cookies_cleared(response):
    # delete_cookie 後は CookieJar から削除されている前提
    assert "ACCESS_TOKEN" not in response.cookies
    assert "REFRESH_TOKEN" not in response.cookies


# ============================================================
# /auth/register
# ============================================================

def test_register_success(client: TestClient):
    email = _make_email("register_ok")

    resp = client.post(
        f"{BASE_URL}/register",
        json={
            "email": email,
            "password": "test-password",
            "name": "Test User",
        },
    )

    assert resp.status_code == 201
    body = resp.json()

    assert "user" in body
    assert body["user"]["email"] == email
    assert body["user"]["plan"] == "trial"
    _assert_auth_cookies_set(resp)


def test_register_duplicate_email_returns_409(client: TestClient):
    email = _make_email("register_dup")
    payload = {
        "email": email,
        "password": "test-password",
        "name": "Dup User",
    }

    # 1回目は成功
    resp1 = client.post(f"{BASE_URL}/register", json=payload)
    assert resp1.status_code == 201

    # 2回目は 409 + EMAIL_ALREADY_IN_USE
    resp2 = client.post(f"{BASE_URL}/register", json=payload)
    assert resp2.status_code == 409
    body = resp2.json()
    assert body["error"]["code"] == "EMAIL_ALREADY_IN_USE"


def test_register_validation_error_returns_400(client: TestClient):
    # password を送らないなど、Pydantic バリデーションを失敗させる
    resp = client.post(
        f"{BASE_URL}/register",
        json={
            "email": "not-an-email",
        },
    )

    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"


# ============================================================
# /auth/login
# ============================================================

def test_login_success_sets_cookies(client: TestClient):
    email = _make_email("login_ok")
    password = "test-password"

    # まず登録
    client.post(
        f"{BASE_URL}/register",
        json={
            "email": email,
            "password": password,
            "name": "Login User",
        },
    )

    # ログイン
    resp = client.post(
        f"{BASE_URL}/login",
        json={"email": email, "password": password},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["user"]["email"] == email
    _assert_auth_cookies_set(resp)


def test_login_invalid_credentials_returns_401(client: TestClient):
    email = _make_email("login_invalid")
    password = "correct-password"

    client.post(
        f"{BASE_URL}/register",
        json={
            "email": email,
            "password": password,
            "name": "Login Invalid User",
        },
    )

    resp = client.post(
        f"{BASE_URL}/login",
        json={"email": email, "password": "wrong-password"},
    )

    assert resp.status_code == 401
    body = resp.json()
    # auth_error_handler で INVALID_CREDENTIALS を返す想定
    assert body["error"]["code"] == "INVALID_CREDENTIALS"


def test_login_validation_error_returns_400(client: TestClient):
    resp = client.post(
        f"{BASE_URL}/login",
        json={"email": "invalid-email-format"},
    )

    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"


# ============================================================
# /auth/me (GET)
# ============================================================

def test_get_me_returns_current_user(client: TestClient):
    email = _make_email("me_ok")
    password = "test-password"

    client.post(
        f"{BASE_URL}/register",
        json={
            "email": email,
            "password": password,
            "name": "Me User",
        },
    )

    resp = client.get(f"{BASE_URL}/me")
    assert resp.status_code == 200

    body = resp.json()
    assert body["user"]["email"] == email


def test_get_me_without_auth_returns_401(client: TestClient):
    # Cookie をクリアして未認証状態にする
    client.cookies.clear()

    resp = client.get(f"{BASE_URL}/me")
    assert resp.status_code == 401
    body = resp.json()
    # エラーコードは INVALID_CREDENTIALS or UNAUTHORIZED など実装に合わせて調整
    assert "error" in body


# ============================================================
# /auth/logout
# ============================================================

def test_logout_clears_cookies_and_returns_204(client: TestClient):
    email = _make_email("logout_ok")
    password = "test-password"

    client.post(
        f"{BASE_URL}/register",
        json={
            "email": email,
            "password": password,
            "name": "Logout User",
        },
    )

    # ログアウト
    resp = client.post(f"{BASE_URL}/logout")
    assert resp.status_code == 204
    _assert_auth_cookies_cleared(resp)

    # 以降 /me は 401 になる想定
    me_resp = client.get(f"{BASE_URL}/me")
    assert me_resp.status_code == 401


def test_logout_without_auth_returns_401(client: TestClient):
    client.cookies.clear()

    resp = client.post(f"{BASE_URL}/logout")
    assert resp.status_code == 401
    body = resp.json()
    assert "error" in body


# ============================================================
# /auth/me (DELETE)
# ============================================================

def test_delete_me_marks_deleted_and_clears_cookies(client: TestClient):
    email = _make_email("delete_ok")
    password = "test-password"

    client.post(
        f"{BASE_URL}/register",
        json={
            "email": email,
            "password": password,
            "name": "Delete User",
        },
    )

    resp = client.delete(f"{BASE_URL}/me")
    assert resp.status_code == 204
    _assert_auth_cookies_cleared(resp)

    # 削除後は /me で 401 (USER_NOT_FOUND など) が返ってくる想定
    me_resp = client.get(f"{BASE_URL}/me")
    assert me_resp.status_code == 401
    body = me_resp.json()
    # auth_error_handler で USER_NOT_FOUND を返すならここで確認
    # assert body["error"]["code"] == "USER_NOT_FOUND"
    assert "error" in body


def test_delete_me_without_auth_returns_401(client: TestClient):
    client.cookies.clear()

    resp = client.delete(f"{BASE_URL}/me")
    assert resp.status_code == 401
    body = resp.json()
    assert "error" in body


# ============================================================
# /auth/refresh
# ============================================================

def test_refresh_issues_new_tokens(client: TestClient):
    email = _make_email("refresh_ok")
    password = "test-password"

    # register すると REFRESH_TOKEN Cookie がセットされる
    client.post(
        f"{BASE_URL}/register",
        json={
            "email": email,
            "password": password,
            "name": "Refresh User",
        },
    )

    resp = client.post(f"{BASE_URL}/refresh")
    assert resp.status_code == 200

    body = resp.json()
    assert body["ok"] is True
    assert body["user"]["email"] == email
    _assert_auth_cookies_set(resp)


def test_refresh_without_cookie_returns_401(client: TestClient):
    client.cookies.clear()

    resp = client.post(f"{BASE_URL}/refresh")
    assert resp.status_code == 401
    body = resp.json()
    # Missing / invalid refresh token → UNAUTHORIZED を返す実装に合わせる
    assert body["error"]["code"] in ("UNAUTHORIZED", "INVALID_CREDENTIALS")
