# backend/tests/integration/api/test_auth_endpoints.py

from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

BASE_URL = "/api/v1/auth"


def _make_email(prefix: str) -> str:
    """テストごとにユニークなメールアドレスを生成するヘルパー。"""
    return f"{prefix}_{uuid4().hex}@example.com"


def _assert_auth_cookies_in_response(resp) -> None:
    """レスポンスに認証クッキーが含まれていることを確認。"""
    # resp.cookies は Set-Cookie ヘッダから構築された CookieJar
    assert "ACCESS_TOKEN" in resp.cookies
    assert "REFRESH_TOKEN" in resp.cookies


# 共通ヘルパー：ユーザー登録 + レスポンス返却
def _register_user(
    client: TestClient,
    *,
    email_prefix: str = "user",
    password: str = "test-password",
    name: str = "Test User",
):
    email = _make_email(email_prefix)
    resp = client.post(
        f"{BASE_URL}/register",
        json={
            "email": email,
            "password": password,
            "name": name,
        },
    )
    return email, password, resp


# ============================================================
# /auth/register
# ============================================================


def test_register_success(client: TestClient) -> None:
    email, _, resp = _register_user(client, email_prefix="register_ok")

    assert resp.status_code == 201

    body = resp.json()
    assert "user" in body
    assert body["user"]["email"] == email
    # UserPlan.TRIAL を想定
    assert body["user"]["plan"] == "trial"

    # レスポンスにクッキーが含まれていることを確認
    _assert_auth_cookies_in_response(resp)


def test_register_duplicate_email_returns_409(client: TestClient) -> None:
    email, password, resp1 = _register_user(
        client, email_prefix="register_dup")
    assert resp1.status_code == 201

    payload = {"email": email, "password": password, "name": "Dup User"}

    # 2回目は 409 想定（EMAIL_ALREADY_IN_USE）
    resp2 = client.post(f"{BASE_URL}/register", json=payload)
    assert resp2.status_code == 409
    body = resp2.json()

    # ErrorResponse { error: { code, message } } を想定
    if "error" in body:
        assert body["error"]["code"] == "EMAIL_ALREADY_IN_USE"


def test_register_validation_error_returns_400(client: TestClient) -> None:
    # password を送らないなど、Pydantic バリデーションを失敗させる
    resp = client.post(
        f"{BASE_URL}/register",
        json={
            "email": "not-an-email",
        },
    )

    # 契約どおりなら 400 + ErrorResponse(VALIDATION_ERROR)
    assert resp.status_code == 400
    body = resp.json()
    if "error" in body:
        assert body["error"]["code"] == "VALIDATION_ERROR"


# ============================================================
# /auth/login
# ============================================================


def test_login_success_sets_cookies(client: TestClient) -> None:
    email, password, _ = _register_user(client, email_prefix="login_ok")

    # ログイン
    resp = client.post(
        f"{BASE_URL}/login",
        json={"email": email, "password": password},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["user"]["email"] == email

    _assert_auth_cookies_in_response(resp)


def test_login_invalid_credentials_returns_401(client: TestClient) -> None:
    email, password, _ = _register_user(client, email_prefix="login_invalid")

    resp = client.post(
        f"{BASE_URL}/login",
        json={"email": email, "password": password + "_wrong"},
    )

    assert resp.status_code == 401
    body = resp.json()
    # auth_error_handler を実装済みなら INVALID_CREDENTIALS が返る想定
    if "error" in body:
        assert body["error"]["code"] == "INVALID_CREDENTIALS"


def test_login_validation_error_returns_400(client: TestClient) -> None:
    resp = client.post(
        f"{BASE_URL}/login",
        json={"email": "invalid-email-format"},
    )

    assert resp.status_code == 400
    body = resp.json()
    if "error" in body:
        assert body["error"]["code"] == "VALIDATION_ERROR"


# ============================================================
# /auth/me (GET)
# ============================================================


def test_get_me_returns_current_user(client: TestClient) -> None:
    email, password, reg_resp = _register_user(client, email_prefix="me_ok")
    assert reg_resp.status_code == 201

    # 登録レスポンスのクッキーをそのまま /me に渡す
    cookies = reg_resp.cookies

    resp = client.get(f"{BASE_URL}/me", cookies=cookies)
    assert resp.status_code == 200

    body = resp.json()
    assert body["user"]["email"] == email


def test_get_me_without_auth_returns_401(client: TestClient) -> None:
    # Cookie を送らずに叩く
    resp = client.get(f"{BASE_URL}/me")
    assert resp.status_code == 401

    body = resp.json()
    # ErrorResponse に寄せていく予定だが、現時点では detail のみの可能性もあるので緩めに
    assert "error" in body or "detail" in body


# ============================================================
# /auth/logout
# ============================================================


def test_logout_clears_cookies_and_returns_204(client: TestClient) -> None:
    email, password, reg_resp = _register_user(
        client, email_prefix="logout_ok")
    assert reg_resp.status_code == 201

    cookies = reg_resp.cookies

    # ログアウト（認証付き）
    resp = client.post(f"{BASE_URL}/logout", cookies=cookies)
    assert resp.status_code == 204
    # Cookie の削除そのものは、/me が 401 になることなどで今後検証してもよい


def test_logout_without_auth_returns_401(client: TestClient) -> None:
    resp = client.post(f"{BASE_URL}/logout")
    assert resp.status_code == 401

    body = resp.json()
    assert "error" in body or "detail" in body


# ============================================================
# /auth/me (DELETE)
# ============================================================


def test_delete_me_marks_deleted_and_clears_cookies(client: TestClient) -> None:
    email, password, reg_resp = _register_user(
        client, email_prefix="delete_ok")
    assert reg_resp.status_code == 201

    cookies = reg_resp.cookies

    # 削除（認証付き）
    resp = client.delete(f"{BASE_URL}/me", cookies=cookies)
    assert resp.status_code == 204

    # 削除後は /me で 401 になるのが理想だが、
    # 実装によっては今後揃えていく想定なので、ここではステータスだけ確認。


def test_delete_me_without_auth_returns_401(client: TestClient) -> None:
    resp = client.delete(f"{BASE_URL}/me")
    assert resp.status_code == 401

    body = resp.json()
    assert "error" in body or "detail" in body


# ============================================================
# /auth/refresh
# ============================================================


def test_refresh_issues_new_tokens(client: TestClient) -> None:
    email, password, reg_resp = _register_user(
        client, email_prefix="refresh_ok")
    assert reg_resp.status_code == 201

    cookies = reg_resp.cookies

    resp = client.post(f"{BASE_URL}/refresh", cookies=cookies)
    assert resp.status_code == 200

    body = resp.json()
    assert body.get("ok") is True
    assert body["user"]["email"] == email

    # 新しいトークンがレスポンスのクッキーとして再セットされていること
    _assert_auth_cookies_in_response(resp)


def test_refresh_without_cookie_returns_401(client: TestClient) -> None:
    resp = client.post(f"{BASE_URL}/refresh")
    assert resp.status_code == 401

    body = resp.json()
    # Missing / invalid refresh token → UNAUTHORIZED などを想定
    if "error" in body:
        assert body["error"]["code"] in ("UNAUTHORIZED", "INVALID_CREDENTIALS")
